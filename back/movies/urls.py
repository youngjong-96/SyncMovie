from django.urls import path
from . import views

urlpatterns = [
    path('movies/', views.movie_list),
    path('movies/<int:movie_pk>/', views.movie_detail),
    path('movies/<int:movie_pk>/likes/', views.like_movie),
    path('movies/random/', views.random_movies),
    path('recommend/', views.recommend_movies),
    path('movies/<int:movie_pk>/reviews/', views.review_list_create),
    path('movies/<int:movie_pk>/reviews/<int:review_pk>/', views.review_detail),
    path('movies/search/', views.movie_search),
]