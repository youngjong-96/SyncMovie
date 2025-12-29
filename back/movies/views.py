from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from django.shortcuts import get_object_or_404, get_list_or_404
from django.core.paginator import Paginator
from django.core.cache import cache
from django.db.models import Q

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import random
import re
import numpy as np

from .models import Movie, Review
from .serializers import MovieListSerializer, MovieDetailSerializer, ReviewSerializer


# 영화 목록 조회 및 장르별 추천 뷰
# 파라미터로 genre가 주어지면 해당 장르의 영화를 랜덤으로 10개 반환하고,
# 그렇지 않으면 인기도가 높은 상위 100개 중 10개를 랜덤으로 추천하여 반환함
@api_view(['GET'])
def movie_list(request):
    genre_name = request.GET.get('genre')
    
    if genre_name:
        # 장르별 랜덤 추천 (10개)
        movies = Movie.objects.filter(genres__name=genre_name).order_by('?')[:10]
        serializer = MovieListSerializer(movies, many=True)
        return Response(serializer.data)
    
    # 1. 인기도 높은 상위 100개 중 10개 랜덤 추천
    top_movies = Movie.objects.order_by('-popularity')[:100]
    
    # 리스트로 변환 후 랜덤 샘플링
    top_movies_list = list(top_movies)
    if len(top_movies_list) >= 10:
        selected_movies = random.sample(top_movies_list, 10)
    else:
        selected_movies = top_movies_list

    # 3. Serializer를 통해 JSON 변환
    serializer = MovieListSerializer(selected_movies, many=True)
    
    return Response(serializer.data)

# 영화 상세 정보 조회 뷰
# 특정 영화의 ID(movie_pk)를 받아 상세 정보를 반환하며, 좋아요 여부 확인을 위해 request context를 전달함
@api_view(['GET'])
def movie_detail(request, movie_pk):
    # 1. 해당 ID의 영화가 없으면 404 에러 발생
    movie = get_object_or_404(Movie, pk=movie_pk)
    
    # 2. 상세 정보 JSON 변환
    serializer = MovieDetailSerializer(movie, context={'request': request})
    return Response(serializer.data)

# 영화 좋아요 토글 뷰
# 로그인한 유저가 특정 영화에 좋아요를 누르면 추가하고, 이미 눌렀다면 취소(삭제)함
# 현재의 좋아요 상태(is_liked)를 반환함
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def like_movie(request, movie_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    if movie.like_users.filter(pk=request.user.pk).exists():
        movie.like_users.remove(request.user)
        is_liked = False
    else:
        movie.like_users.add(request.user)
        is_liked = True
    return Response({'is_liked': is_liked})

# 알고리즘 기반 영화 추천 뷰
# 사용자가 선택한 영화 목록(movie_ids)을 기반으로, 줄거리(overview) 유사도 또는 배우(actors) 기반으로
# 비슷한 영화를 찾아 추천해줌
def simple_korean_tokenizer(text):
    return re.findall(r'[가-힣a-zA-Z0-9]+', text)

@api_view(['POST'])
def recommend_movies(request):
    data = request.data
    movie_ids = data.get('movie_ids')
    recommendation_type = data.get('type')

    if not movie_ids or not isinstance(movie_ids, list) or len(movie_ids) == 0:
        return Response({'error': 'movie_ids must be a non-empty list'}, 
                         status=status.HTTP_400_BAD_REQUEST)

    # --- 캐싱 로직 시작 ---
    cache_key = f"recommend_data_{recommendation_type}"
    cached_data = cache.get(cache_key)

    if cached_data:
        # 캐시된 데이터가 있으면 바로 사용
        vectorizer, tfidf_matrix, all_movies_list = cached_data
    else:
        # 캐시가 없으면 데이터 로드 및 계산 (최초 1회 또는 캐시 만료 시)
        all_movies_qs = Movie.objects.all().prefetch_related('actors', 'genres')
        all_movies_list = list(all_movies_qs)
        
        if recommendation_type == 'overview':
            contents = [f"{m.overview or ''}" for m in all_movies_list]
        elif recommendation_type == 'actors':
            def build_text(m):
                actors = m.actors.values_list('name', flat=True)[:5]
                norm_actors = ['_'.join(n.split()) for n in actors]
                director = '_'.join(m.director.split()) if m.director else ''
                return ' '.join(norm_actors + ([director] if director else []))
            contents = [build_text(m) for m in all_movies_list]
        else:
            return Response({'error': 'Invalid type'}, status=status.HTTP_400_BAD_REQUEST)

        vectorizer = TfidfVectorizer(
            tokenizer=simple_korean_tokenizer,
            stop_words=['의', '가', '에', '들', '는', '을', '를', '이', '와', '로', '으로', '에서'],
            max_features=5000
        )
        tfidf_matrix = vectorizer.fit_transform(contents)
        
        # 결과를 캐시에 저장 (유효기간 1시간 = 3600초)
        cache.set(cache_key, (vectorizer, tfidf_matrix, all_movies_list), 3600)
    # --- 캐싱 로직 끝 ---

    # 1. 입력받은 movie_ids에 해당하는 인덱스 찾기
    # 캐시된 all_movies_list 내에서 base_movie들의 위치를 찾습니다.
    movie_id_to_idx = {movie.id: i for i, movie in enumerate(all_movies_list)}
    base_indices = [movie_id_to_idx[m_id] for m_id in movie_ids if m_id in movie_id_to_idx]

    if not base_indices:
        return Response({'error': 'Movies not found'}, status=status.HTTP_404_NOT_FOUND)

    # 2. Sparse Matrix 연산
    base_vecs = tfidf_matrix[base_indices]
    user_vec = base_vecs.mean(axis=0)

    # 3. 모든 영화와의 유사도 계산
    cosine_sim = cosine_similarity(user_vec, tfidf_matrix).flatten()

    # 4. 자기 자신(입력 영화) 제외하고 상위 10개 추출
    # 입력 영화들의 인덱스 점수를 0으로 만들어 추천에서 제외
    for idx in base_indices:
        cosine_sim[idx] = -1

    top_indices = cosine_sim.argsort()[::-1][:10]
    recommended_movies = [all_movies_list[i] for i in top_indices]

    serializer = MovieListSerializer(recommended_movies, many=True)
    return Response(serializer.data)


# 랜덤 영화 추천 뷰
# 전체 영화 중 특정 영화(exclude)를 제외하고 지정된 개수(num)만큼 랜덤하게 추출하여 반환함
@api_view(['GET'])
def random_movies(request):
    num = int(request.GET.get('num', 10))
    exclude_ids = request.GET.get('exclude', '')
    exclude_list = [int(id.strip()) for id in exclude_ids.split(',') if id.strip()]
    
    # 전체 영화에서 exclude_list 제외하고 랜덤으로 num개 추출 (popularity >= 10(3사분위 값) 인 영화들에 대해서)
    # movies = Movie.objects.exclude(id__in=exclude_list).order_by('?')[:num]
    movies = Movie.objects.filter(popularity__gte=10).exclude(id__in=exclude_list).order_by('?')[:num]
    serializer = MovieListSerializer(movies, many=True)
    return Response(serializer.data)

# 리뷰 목록 조회 및 작성 뷰
# GET: 특정 영화의 모든 리뷰를 최신순으로 반환함
# POST: 특정 영화에 대한 리뷰를 작성함 (로그인 필요)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def review_list_create(request, movie_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)

    if request.method == 'GET':
        reviews = movie.reviews.all().order_by('-created_at')
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(movie=movie, user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def review_detail(request, movie_pk, review_pk):
    review = get_object_or_404(Review, pk=review_pk)
    
    if request.user != review.user:
        return Response({'detail': '권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)
    
    review.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def movie_search(request):
    q = request.GET.get('q', '').strip()
    # print('검색어 q =', repr(q))  # 🔥 1) 진짜 "어벤져스" 들어오는지 확인

    if not q:
        return Response([])

    movies = Movie.objects.filter(
        Q(title__icontains=q)
    ).order_by('-popularity')

    # print('검색 결과 개수 =', movies.count())  # 🔥 2) DB에서 몇 개 나오는지

    serializer = MovieListSerializer(movies, many=True)
    return Response(serializer.data)
