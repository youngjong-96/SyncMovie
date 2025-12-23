import os
import requests
import pandas as pd
from pathlib import Path

# TMDB API 설정
api_key = os.getenv('VITE_TMDB_API_KEY')
if not api_key:
    raise ValueError("TMDB_API_KEY 설정하세요 (.env)")

base_url = 'https://api.themoviedb.org/3'

def load_tmdb_full_dataset():
    """인기 영화 6000개 + 크레딧 + 상세정보 로드"""
    all_movies = []
    
    # 인기 영화 리스트 (페이지별)
    print("📥 인기 영화 로딩 중...")
    page = 1
    while len(all_movies) < 6000:
        url = f"{base_url}/movie/popular"
        params = {'api_key': api_key, 'language': 'ko-KR', 'page': page}
        response = requests.get(url, params=params)
        movies = response.json()['results']
        
        all_movies.extend(movies)
        print(f"Page {page}: {len(movies)}개 → 총 {len(all_movies)}개")
        page += 1
    
    # 크레딧 + 상세정보 포함 완전체 데이터
    print("\n🎬 크레딧 + 상세정보 로딩 중...")
    full_movies = []
    for i, movie_data in enumerate(all_movies):
        if i % 100 == 0:
            print(f"처리 중: {i+1}/{len(all_movies)} {movie_data['title'][:30]}")
        
        movie_info = movie_data.copy()
        tmdb_id = movie_data['id']
        
        # 1. 크레딧 API 호출 (배우 + 감독)
        credits_url = f"{base_url}/movie/{tmdb_id}/credits"
        credits_params = {'api_key': api_key, 'language': 'ko-KR'}
        credits_response = requests.get(credits_url, params=credits_params)
        credits = credits_response.json()
        
        # 감독 (첫 번째 감독)
        director = next((c['name'] for c in credits['crew'] if c['job'] == 'Director'), '')
        movie_info['director'] = director
        
        # 🔥 배우: order 기준 상위 5명만!
        cast_list = credits['cast']
        top5_cast = sorted(cast_list, key=lambda x: x.get('order', 999))[:5]
        cast_names = [c['name'] for c in top5_cast]
        movie_info['cast'] = ', '.join(cast_names)
        movie_info['cast_top5_order'] = cast_names  # 리스트로도 저장
        
        # 2. 상세정보 API 호출 (완전한 genres)
        details_url = f"{base_url}/movie/{tmdb_id}"
        details_params = {'api_key': api_key, 'language': 'ko-KR', 'append_to_response': 'genres'}
        details_response = requests.get(details_url, params=details_params)
        details = details_response.json()
        
        # 🔥 genres: 상세정보에서 가져오기
        genres = [g['name'] for g in details.get('genres', [])]
        movie_info['genres'] = ', '.join(genres)
        movie_info['genres_list'] = genres  # 리스트로도 저장
        
        full_movies.append(movie_info)
    
    return pd.DataFrame(full_movies)


# --------------------------------------------------------- 
# [전처리 1단계] 데이터 로드 & 필터링
# ---------------------------------------------------------
# 실행
df = load_tmdb_full_dataset()
print(f"\n✅ 완성! {df.shape[0]}개 영화")

# 필터링 (원본 코드와 동일)
df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
filter_df = df.dropna(subset=['id', 'title', 'poster_path', 'overview', 'release_date'])  # poster_path 결측치 114개 존재
filter_df = filter_df[filter_df['overview'].str.strip() != ""] # overview 컬럼은 결측치가 존재하지 않지만 빈 문자열 2301개 존재 

# 한글,영어,특수문자가 아닌 문자가 들어간 데이터 확인
# filter_df[~filter_df['title'].str.match( r'^[가-힣a-zA-Z0-9\s\.\'\-,!?:;()&+/*%#=@\[\]\{\}\^~]*$', na=False)].shape

filter_df = filter_df[filter_df['title'] != 'देवा'] # 해당 영화만 제거
print(f"📈 필터링 후: {filter_df.shape[0]}개") # 3698개

# --------------------------------------------------------- 
# [전처리 2단계] 데이터 가공 (전체 컬럼 유지)
# ---------------------------------------------------------
# 포스터 URL 완성
def make_poster_url(path):
    if pd.isna(path) or path == '':
        return None
    return f"https://image.tmdb.org/t/p/w500{path}"

filter_df['poster_path_full'] = filter_df['poster_path'].apply(make_poster_url)

# 장르 리스트 (추가 컬럼)
def str_to_list(x):
    if pd.isna(x) or x == '':
        return []
    return [item.strip() for item in str(x).split(',')]

filter_df['genres_list'] = filter_df['genres'].apply(str_to_list)

# 배우 상위 5명 리스트 (추가 컬럼)
def process_cast(x):
    if pd.isna(x) or x == '':
        return []
    people = [item.strip() for item in str(x).split(',')]
    return people[:5]

filter_df['cast_top5'] = filter_df['cast'].apply(process_cast)


# --------------------------------------------------------- 
# [전처리 3단계] 최종 데이터셋 (전체 컬럼 + 추가 컬럼)
# ---------------------------------------------------------
print("\n✅ 전처리 완료!")
print(f"최종 데이터: {filter_df.shape[0]}개 영화, {filter_df.shape[1]}개 컬럼")

# 모든 컬럼 출력
print("\n📋 컬럼 목록:")
print(list(filter_df.columns))

print("\n👀 샘플 데이터:")
print(filter_df[['title', 'director', 'cast_top5', 'genres_list']].head(3))

# --------------------------------------------------------- 
# [저장] Django fixtures + Pandas JSON
# ---------------------------------------------------------
# Django fixtures 형식 (JSON 배열)
filter_df.to_json('./back/api_data.json', orient='records', force_ascii=False, indent=2)

print(f"\n💾 저장 완료!")