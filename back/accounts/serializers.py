from rest_framework import serializers
from django.contrib.auth import get_user_model
from movies.models import Review
from movies.serializers import MovieListSerializer
from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import LoginSerializer

User = get_user_model()

class CustomRegisterSerializer(RegisterSerializer):
    nickname = serializers.CharField(max_length=20)

    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        data['nickname'] = self.validated_data.get('nickname', '')
        return data

    def save(self, request):
        user = super().save(request)
        user.nickname = self.cleaned_data.get('nickname')
        user.save()
        return user

class CustomLoginSerializer(LoginSerializer):
    def validate(self, attrs):
        username = attrs.get('username')
        # password = attrs.get('password')
        
        if username:
            # Check if username exists
            if not User.objects.filter(username=username).exists():
                 raise serializers.ValidationError({'username': ['존재하지 않는 아이디입니다.']})

        # Try to validate (authenticate)
        try:
            return super().validate(attrs)
        except serializers.ValidationError as e:
            # If authentication fails but username exists, it's likely a password issue
            # dj_rest_auth puts auth errors in non_field_errors
            if 'non_field_errors' in e.detail:
                 raise serializers.ValidationError({'password': ['비밀번호가 올바르지 않습니다.']})
            raise e

# 유저 프로필 페이지에서 사용자가 작성한 리뷰 목록을 보여줄 때 사용되는 시리얼라이저
# 리뷰의 기본 정보와 함께 해당 리뷰가 달린 영화의 제목과 ID를 포함함
class ProfileReviewSerializer(serializers.ModelSerializer):
    movie_title = serializers.CharField(source='movie.title', read_only=True)
    movie_id = serializers.IntegerField(source='movie.id', read_only=True)

    class Meta:
        model = Review
        fields = ('id', 'content', 'rank', 'movie_title', 'movie_id', 'created_at')

# 유저 프로필 조회 시 사용되는 메인 시리얼라이저
# 유저의 기본 정보와 함께 작성한 리뷰 목록, 좋아요한 영화 목록을 포함함
class UserSerializer(serializers.ModelSerializer):
    reviews = ProfileReviewSerializer(many=True, read_only=True)
    like_movies = MovieListSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'nickname', 'reviews', 'like_movies', 'date_joined')
