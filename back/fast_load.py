import os
import json
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Syncmovie.settings')
django.setup()

from movies.models import Movie, Actor, Genre # 모델 이름 확인 필요

def run():
    with open('movie.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        total = len(data)
        print(f"총 {total}개의 데이터 로드 완료. 주입 시작...")

        for i, item in enumerate(data):
            # 각자의 테이블 구조에 맞게 Django가 알아서 처리하도록 loaddata의 내부 로직 활용
            # 하지만 여기서는 가장 안전한 개별 저장을 시도합니다.
            try:
                if item['model'] == 'movies.genre':
                    Genre.objects.update_or_create(pk=item['pk'], defaults=item['fields'])
                elif item['model'] == 'movies.actor':
                    Actor.objects.update_or_create(pk=item['pk'], defaults=item['fields'])
                elif item['model'] == 'movies.movie':
                    fields = item['fields']
                    # ManyToMany 관계(actors, genres)는 일반 필드 저장 후 별도로 처리해야 함
                    actors = fields.pop('actors', [])
                    genres = fields.pop('genres', [])
                    movie, _ = Movie.objects.update_or_create(pk=item['pk'], defaults=fields)
                    movie.actors.set(actors)
                    movie.genres.set(genres)
                
                if i % 100 == 0:
                    print(f"진행률: {i}/{total}...")
            except Exception as e:
                print(f"Skipping pk {item['pk']} due to error: {e}")

    print("모든 데이터 주입 완료!")

if __name__ == "__main__":
    run()