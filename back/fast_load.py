import os
import json
import django
from django import db

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Syncmovie.settings')
django.setup()

from movies.models import Movie, Actor, Genre # 모델 이름 확인 필요

def run():
    with open('movie.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        total = len(data)
        print(f"총 {total}개의 데이터 로드 완료. 주입 시작...")

        for i, item in enumerate(data):
            try:
                if item['model'] == 'movies.genre':
                    Genre.objects.update_or_create(pk=item['pk'], defaults=item['fields'])
                elif item['model'] == 'movies.actor':
                    Actor.objects.update_or_create(pk=item['pk'], defaults=item['fields'])
                elif item['model'] == 'movies.movie':
                    fields = item['fields']
                    actors = fields.pop('actors', [])
                    genres = fields.pop('genres', [])
                    # 영화 데이터 주입 시작 로그
                    movie, created = Movie.objects.update_or_create(pk=item['pk'], defaults=fields)
                    movie.actors.set(actors)
                    movie.genres.set(genres)
                
                # 100개가 아니라 10개 단위로 찍어서 멈춤 현상을 더 빨리 파악합시다.
                if i % 10 == 0:
                    db.reset_queries() # 메모리에 쌓인 쿼리 로그를 비워줍니다.
                    print(f"메모리 최적화 및 {i}번째 진행 중...")
                    
            except Exception as e:
                print(f"에러 발생 (PK {item.get('pk')}): {e}")

    print("모든 데이터 주입 완료!")

if __name__ == "__main__":
    run()