from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('profile/', views.user_profile),
    path('profile/<int:user_id>/', views.user_profile),
    path('check-username/', views.check_username),
    path('reset-password/', views.reset_password),
    path('delete/', views.delete_account),
    path('recommend-nickname/', views.recommend_nickname),
    path('check-nickname/', views.check_nickname),
]