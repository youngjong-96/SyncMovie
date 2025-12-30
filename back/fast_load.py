import os, json, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Syncmovie.settings')
django.setup()
from movies.models import Movie, Actor, Genre

def run():
    with open('movie.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    # 영화(Movie) 데이터만 필터링해서 따로 모읍니다.
    movie_data = [item for item in data if item['model'] == 'movies.movie']
    total = len(movie_data)
    print(f"start total:{total}")

    for i, item in enumerate(movie_data):
        try:
            fields = item['fields']
            actors = fields.pop('actors', [])
            genres = fields.pop('genres', [])
            
            # 영화 정보 저장
            movie, _ = Movie.objects.update_or_create(pk=item['pk'], defaults=fields)
            
            # 관계 설정 (배우가 없으면 에러 날 수 있으니 try-except)
            try:
                movie.actors.set(actors)
                movie.genres.set(genres)
            except:
                pass 
                
            if i % 10 == 0:
                print(f"ing... {i}/{total} complete (PK: {item['pk']})")
        except Exception as e:
            print(f"error(PK {item['pk']}): {e}")

    print("🏁 finish!")

if __name__ == "__main__":
    run()