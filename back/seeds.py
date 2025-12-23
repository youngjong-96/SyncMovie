import os
import json
import django
import math # NaN 체크를 위해 추가

# ---------------------------------------------------------
# 1. Django 환경 설정
# ---------------------------------------------------------
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Syncmovie.settings") # 프로젝트 이름 확인!
django.setup()

from movies.models import Movie, Genre, Actor

# ---------------------------------------------------------
# 2. JSON 데이터 로드
# ---------------------------------------------------------
json_path = './api_data.json'

with open(json_path, 'r', encoding='utf-8') as f:
    movies_data = json.load(f)

print(f"총 {len(movies_data)}개의 영화 데이터를 가져옵니다...")

# ---------------------------------------------------------
# 3. 데이터 적재 (DB Save)
# ---------------------------------------------------------
created_count = 0
updated_count = 0

for idx, data in enumerate(movies_data):
    if idx % 100 == 0:
        print(f"진행 중: {idx} / {len(movies_data)}")

    # [수정된 부분] 날짜 데이터 예외 처리 및 타임스탬프 변환
    import datetime
    release_date_raw = data.get('release_date')
    release_date = None
    
    if release_date_raw and isinstance(release_date_raw, (int, float)):
        try:
            # 타임스탬프(ms) -> date 객체
            release_date = datetime.date.fromtimestamp(release_date_raw / 1000)
        except (ValueError, TypeError, OSError):
            release_date = None
    elif isinstance(release_date_raw, str):
        # 혹시 모를 문자열 형식 대비
        try:
            release_date = datetime.datetime.strptime(release_date_raw, '%Y-%m-%d').date()
        except ValueError:
            release_date = None

    
    director = data.get('director')

    # Backdrop Path URL 구성
    backdrop_path_raw = data.get('backdrop_path')
    backdrop_path = None
    if backdrop_path_raw:
        backdrop_path = f"https://image.tmdb.org/t/p/w1280{backdrop_path_raw}"

    # 이미 존재하는 영화인지 확인
    movie = Movie.objects.filter(tmdb_id=data['id']).first()

    if movie:
        # 이미 존재하면 감독 정보 업데이트 (필요한 경우)
        if director and movie.director != director:
            movie.director = director
            movie.save(update_fields=['director'])
            updated_count += 1
        # 배경 이미지 업데이트
        if backdrop_path and movie.backdrop_path != backdrop_path:
            movie.backdrop_path = backdrop_path
            movie.save(update_fields=['backdrop_path'])
            updated_count += 1
        continue

    # 존재하지 않으면 새로 생성
    try:
        movie = Movie.objects.create(
            tmdb_id=data['id'],
            title=data['title'],
            release_date=release_date, # 변환된 날짜 사용
            overview=data['overview'],
            popularity=data['popularity'],
            vote_average=data['vote_average'],
            poster_path=data.get('poster_path_full'), # 새 데이터셋 필드명 확인
            backdrop_path=backdrop_path, # 배경 이미지 추가
            director=director # 감독 추가
        )
        created_count += 1
    except Exception as e:
        print(f"⚠️ Error saving movie [{data.get('title')}]: {e}")
        continue

    # --- 영화 생성이 성공해야 아래 코드가 실행됨 ---

    # 2) Genre (Many-to-Many)
    for genre_name in data['genres_list']:
        if not genre_name: continue
        genre, created = Genre.objects.get_or_create(name=genre_name)
        movie.genres.add(genre)

    # 3) Actor (Many-to-Many)
    for actor_name in data['cast_top5']:
        if not actor_name: continue
        actor, created = Actor.objects.get_or_create(name=actor_name)
        movie.actors.add(actor)

print(f"데이터 적재 완료! (생성: {created_count}, 업데이트: {updated_count}) 🎉")