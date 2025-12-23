from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404, get_list_or_404
from django.core.paginator import Paginator
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from .models import Movie, Review
from .serializers import MovieListSerializer, MovieDetailSerializer, ReviewSerializer

import re
from django.db.models import Q


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
@api_view(['POST'])
def recommend_movies(request):
    data = request.data
    movie_ids = data.get('movie_ids')  # 🔹 movie_ids 리스트로 변경
    recommendation_type = data.get('type')

    print('data:', data)  # 전체 데이터 확인
    print('movie_ids:', movie_ids)  # 리스트 확인
    print('type:', recommendation_type)

    # 리스트 검증
    if not movie_ids or not isinstance(movie_ids, list) or len(movie_ids) == 0:
        return Response({'error': 'movie_ids must be a non-empty list'}, 
                       status=status.HTTP_400_BAD_REQUEST)

    base_movies = get_list_or_404(Movie, pk__in=movie_ids)  # 🔹 여러 영화

    # # 각 영화 정보 출력
    # for movie in base_movies:
    #     print(f"base_movie {movie.id}: {movie.title}")
    #     print('overview:', movie.overview)
    #     print('genres:', [g.name for g in movie.genres.all()])

    if recommendation_type == 'overview':
        all_movies = Movie.objects.exclude(pk__in=movie_ids)
        
        candidate_contents = [
            (movie.overview or '') + ' ' + ' '.join(g.name.lower() for g in movie.genres.all())
            for movie in all_movies
        ]
        
        base_contents = [
            (movie.overview or '') + ' ' + ' '.join(g.name.lower() for g in movie.genres.all())
            for movie in base_movies
        ]
        
        all_contents = base_contents + candidate_contents
        
        # vectorizer = TfidfVectorizer(stop_words='english')
        # tfidf_matrix = vectorizer.fit_transform(all_contents)
        
        def simple_korean_tokenizer(text):
            # 한글, 영어만 추출 + 공백으로 분리
            korean = re.findall(r'[가-힣a-zA-Z]+', text)
            return korean

        TMDB_stopwords = [
            # 기본 조사/조사사
            '의', '가', '에', '들', '는', '을', '를', '이', '와', '로', '으로', '에서',
            
            # 동사/형용사 (줄거리에서 덜 중요)
            '이다', '되다', '있다', '되', '하는', '한다', '할', '수', '있', '만', '것',
            
            # 영화 도메인 (모든 영화에 공통)
            '영화', '영화의', '영화는', '감독', '배우', '출연', '등장', '주연', '조연',
            
            # 줄거리 공통 표현
            '이야기', '이야기를', '전개', '사람', '세계', '시작', '끝', '사실', '현실',
            
            # 시간/순서
            '첫', '두', '세', '마지막', '최종', '시작', '끝나', '결국', '그러나',
            
            # 부사/접속사
            '정말', '매우', '너무', '그리고', '하지만', '그러나', '그래서', '그러면'
        ]
        
        vectorizer = TfidfVectorizer(
            lowercase=True,
            tokenizer=simple_korean_tokenizer,
            stop_words=TMDB_stopwords + ['english'],
            ngram_range=(1, 3),
            max_features=5000  # 상위 5000단어만
        )
        tfidf_matrix = vectorizer.fit_transform(all_contents)
        
        base_vecs = tfidf_matrix[0:len(base_contents)].toarray()
        user_vec = np.mean(base_vecs, axis=0)
        user_vec_2d = user_vec.reshape(1, -1)
        
        candidate_vecs = tfidf_matrix[len(base_contents):].toarray()
        
        cosine_sim = cosine_similarity(user_vec_2d, candidate_vecs).flatten()
        
        # 🔥 가장 안전한 방법
        top_indices = cosine_sim.argsort()[::-1][:10]
        similar_indices = [int(idx) for idx in top_indices]
        
        print(f"Top indices: {similar_indices}")  # 디버깅용
        
        recommended_movies = [all_movies[i] for i in similar_indices]
    
    elif recommendation_type == 'actors':
        all_movies = Movie.objects.exclude(pk__in=movie_ids)
        
        # 0. 이름 정규화 함수: '톰 홀랜드' -> '톰_홀랜드'
        def normalize_person_name(name: str) -> str:
            if not name:
                return ''
            # 공백을 언더스코어로 치환해서 한 토큰으로 유지
            return '_'.join(name.split())

        # 1. feature 텍스트 생성 (배우 5명 + 감독, 이름은 한 토큰으로)
        def build_feature_text(movie):
            actor_names = movie.actors.values_list('name', flat=True)[:5]
            norm_actors = [normalize_person_name(n) for n in actor_names]
            director = normalize_person_name(movie.director) if movie.director else ''
            tokens = norm_actors + ([director] if director else [])
            return ' '.join(tokens)  # '톰_홀랜드 로버트_다우니_주니어' 형태
        
        # # 1. feature 텍스트 생성 (실시간 전처리)
        # candidate_features = [
        #     ' '.join(movie.actors.values_list('name', flat=True)[:5]) + ' ' + (movie.director or '')
        #     for movie in all_movies
        # ]
        
        # base_features = [
        #     ' '.join(movie.actors.values_list('name', flat=True)[:5]) + ' ' + (movie.director or '')
        #     for movie in base_movies
        # ]
        candidate_features = [build_feature_text(movie) for movie in all_movies]
        base_features = [build_feature_text(movie) for movie in base_movies]
        
        # 2. TF-IDF (overview와 동일)
        all_features = base_features + candidate_features
        
        vectorizer = TfidfVectorizer(
            lowercase=True,
            ngram_range=(1, 1),
            max_features=5000
        )
        tfidf_matrix = vectorizer.fit_transform(all_features)
        
        base_vecs = tfidf_matrix[0:len(base_features)].toarray()
        user_vec = np.mean(base_vecs, axis=0)
        user_vec_2d = user_vec.reshape(1, -1)
        
        candidate_vecs = tfidf_matrix[len(base_features):].toarray()
        cosine_sim = cosine_similarity(user_vec_2d, candidate_vecs).flatten()
        
        # 3. 상위 10개 (overview와 동일)
        top_indices = cosine_sim.argsort()[::-1][:10]
        similar_indices = [int(idx) for idx in top_indices]
        
        recommended_movies = [all_movies[i] for i in similar_indices]

    else:
        return Response({'error': 'Invalid recommendation type'}, status=status.HTTP_400_BAD_REQUEST)
    
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
