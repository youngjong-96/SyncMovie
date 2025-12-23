from rest_framework import serializers
from .models import Movie, Genre, Actor, Review

# 1. 목록 조회용 Serializer (가볍게 필요한 정보만)
# 영화 목록 페이지나 추천 결과 등에서 여러 개의 영화를 간략하게 보여줄 때 사용
class MovieListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ('id', 'tmdb_id', 'title', 'poster_path', 'vote_average', 'popularity', 'overview')


# 2. 상세 조회용 Serializer (모든 정보 포함)
# 영화 상세 페이지에서 사용될 장르 정보 시리얼라이저
class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name',)

# 영화 상세 페이지에서 사용될 배우 정보 시리얼라이저
class ActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = ('name',)

# 영화 상세 페이지에서 영화의 모든 정보를 보여줄 때 사용
# 장르, 배우 정보를 포함하며, 현재 요청한 유저가 좋아요를 눌렀는지 여부(is_liked)를 계산하여 반환함
class MovieDetailSerializer(serializers.ModelSerializer):
    # N:M 관계에 있는 데이터들을 내부 필드로 가져오기
    genres = GenreSerializer(many=True, read_only=True)
    actors = ActorSerializer(many=True, read_only=True)
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Movie
        fields = '__all__' # 모든 필드 포함

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.like_users.filter(pk=request.user.pk).exists()
        return False


# 3. 리뷰 Serializer
# 리뷰 목록 조회 및 작성 시 사용
# 작성자의 유저네임(user_name)을 포함하여 보여줌
class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.nickname', read_only=True)
    user_id = serializers.IntegerField(source='user.pk', read_only=True)

    class Meta:
        model = Review
        fields = ('id', 'content', 'rank', 'user_name', 'user_id', 'created_at')
        read_only_fields = ('movie', 'user')
