from django.contrib import admin
from .models import Movie, Genre, Actor

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'release_date', 'vote_average') # 목록에 보여줄 칼럼
    search_fields = ('title',) # 검색 기능 추가

admin.site.register(Genre)
admin.site.register(Actor)