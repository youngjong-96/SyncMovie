import os
import django

# Django 환경 설정 로드
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Syncmovie.settings')
django.setup()

from django.core.management import call_command

def run():
    try:
        print("--- 데이터 적재 프로세스 시작 ---")
        # migrate를 먼저 실행하여 테이블 구조를 최신화합니다.
        call_command('migrate')
        print("1. 마이그레이션 완료")

        # fixture 파일을 로드합니다.
        print("2. 데이터 주입 중 (이 작업은 몇 분 정도 소요될 수 있습니다)...")
        call_command('loaddata', 'movie.json')
        print("--- 모든 데이터 적재 완료! ---")
    except Exception as e:
        print(f"!!! 에러 발생: {e}")

if __name__ == "__main__":
    run()