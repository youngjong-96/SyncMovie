from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # 닉네임 필드(필요 시 사용)
    nickname = models.CharField(max_length=20, default='')
    
    # 유저 프로필 이미지(필요 시 사용)
    # profile_image = models.ImageField(upload_to='profile/', blank=True)