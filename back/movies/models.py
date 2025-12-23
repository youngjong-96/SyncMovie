from django.db import models
from django.conf import settings

# -------------------------------------------------------------------------
# 1. 메타 데이터 모델 (장르, 배우)
# F-08, F-09 추천 알고리즘의 핵심 기준이 됩니다.
# -------------------------------------------------------------------------

class Genre(models.Model):
    # seeds.py에서 name 필드를 기준으로 get_or_create 합니다.
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Actor(models.Model):
    # F-09: 배우 기반 추천을 위해 분리된 모델
    # seeds.py에서 name 필드를 기준으로 get_or_create 합니다.
    name = models.CharField(max_length=100, unique=True)
    
    # 추후 배우 사진 등을 넣고 싶다면 필드 추가 가능 (현재 데이터엔 없음)
    # profile_path = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.name


# -------------------------------------------------------------------------
# 2. 영화 정보 모델 (Core)
# F-03, F-04, F-08, F-10 기능을 담당합니다.
# -------------------------------------------------------------------------

class Movie(models.Model):
    # [식별자]
    tmdb_id = models.IntegerField(unique=True, db_index=True)  # TMDB 고유 ID (검색 속도 위해 인덱스 추가)
    
    # [기본 정보]
    title = models.CharField(max_length=200)       # 제목
    release_date = models.DateField(null=True, blank=True) # 개봉일
    poster_path = models.CharField(max_length=300, null=True, blank=True) # 포스터 URL (전처리된 전체 경로)
    backdrop_path = models.CharField(max_length=300, null=True, blank=True) # 배경 이미지 URL (추가)
    
    # [알고리즘용 데이터]
    overview = models.TextField(blank=True)        # F-08: 줄거리 (TF-IDF 분석 대상)
    director = models.CharField(max_length=100, null=True, blank=True) # 감독
    popularity = models.FloatField(default=0)      # F-10: Bandit 알고리즘의 '활용(Exploitation)' 지표
    vote_average = models.FloatField(default=0)    # 평점 (단순 정렬용)
    
    # [관계 설정]
    # F-09: 배우와 장르는 N:M 관계
    genres = models.ManyToManyField(Genre, related_name='movies')
    actors = models.ManyToManyField(Actor, related_name='movies')
    
    # F-07: 영화 좋아요 (User와 N:M)
    like_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='like_movies', blank=True)

    def __str__(self):
        return self.title


# -------------------------------------------------------------------------
# 3. 커뮤니티 기능 모델 (리뷰)
# F-05, F-06 기능을 담당합니다.
# -------------------------------------------------------------------------

class Review(models.Model):
    # User와 Movie의 관계 연결
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='reviews')
    
    # [리뷰 내용]
    content = models.TextField()               # 후기 내용
    rank = models.IntegerField()               # 평점 (1~10점)
    
    # [메타 데이터]
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # F-06: 리뷰 좋아요 기능 (이 리뷰를 좋아하는 사람들)
    like_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='like_reviews', blank=True)

    def __str__(self):
        return f'{self.movie.title} - {self.user.username}'