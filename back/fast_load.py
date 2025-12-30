import os, json, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Syncmovie.settings')
django.setup()
from movies.models import Movie, Actor, Genre

def run():
    with open('movie.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    # 영화(Movie) 데이터만 추출
    movie_data = [item for item in data if item['model'] == 'movies.movie']
    total = len(movie_data)
    print(f"total {total}")

    for i, item in enumerate(movie_data):
        try:
            fields = item['fields']
            
            # ManyToMany 필드들은 따로 추출 (set() 메서드 사용을 위해)
            actors_ids = fields.pop('actors', [])
            genres_ids = fields.pop('genres', [])
            like_users_ids = fields.pop('like_users', []) # 이 부분이 에러의 원인이었습니다!
            
            # 1. 일반 필드 먼저 저장
            movie, created = Movie.objects.update_or_create(
                pk=item['pk'], 
                defaults=fields
            )
            
            # 2. 관계 필드 설정 (.set() 사용)
            movie.actors.set(actors_ids)
            movie.genres.set(genres_ids)
            movie.like_users.set(like_users_ids)
            
            if i % 10 == 0:
                print(f"progress: {i}/{total} (PK: {item['pk']})")
                
        except Exception as e:
            print(f"error(PK {item['pk']}): {e}")

    print("🏁 [성공] 모든 영화 데이터가 정상적으로 주입되었습니다!")

if __name__ == "__main__":
    run()