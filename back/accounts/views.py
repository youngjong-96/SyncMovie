from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import UserSerializer
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from google import genai
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request, user_id=None):
    if user_id:
        User = get_user_model()
        user = get_object_or_404(User, pk=user_id)
    else:
        user = request.user
    serializer = UserSerializer(user)
    return Response(serializer.data)

@api_view(['POST', 'GET'])
@permission_classes([AllowAny])
def check_username(request):
    User = get_user_model()
    if request.method == 'POST':
        username = request.data.get('username', None)
        if not username:
            return Response({'error': '아이디를 입력해주세요.'}, status=400)
        exists = User.objects.filter(username=username).exists()
        return Response({'exists': exists})
    else:  # GET request
        username = request.query_params.get('username', None)
        if not username:
            return Response({'error': '아이디를 입력해주세요.'}, status=400)
        exists = User.objects.filter(username=username).exists()
        return Response({
            'is_available': not exists,
            'message': '사용 가능한 아이디입니다.' if not exists else '이미 사용 중인 아이디입니다.'
        })

@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    username = request.data.get('username')
    password = request.data.get('password')
    password2 = request.data.get('password2')
    
    User = get_user_model()
    user = get_object_or_404(User, username=username)
    
    if password != password2:
        return Response({'password': ['비밀번호가 일치하지 않습니다.']}, status=status.HTTP_400_BAD_REQUEST)
    
    if user.check_password(password):
        return Response({'password': ['이전 비밀번호와 동일합니다.']}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        validate_password(password, user=user)
    except ValidationError as e:
        return Response({'password': e.messages}, status=status.HTTP_400_BAD_REQUEST)
        
    user.set_password(password)
    user.save()
    
    return Response({'message': '비밀번호가 성공적으로 변경되었습니다.'}, status=status.HTTP_200_OK)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_account(request):
    request.user.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes([AllowAny])
def recommend_nickname(request):
    gms_key = os.environ.get("GMS_API_KEY")
    if not gms_key:
        return Response({"error": "API 키가 설정되지 않았습니다."}, status=500)
    try:
        # GMS 사양에 맞춘 클라이언트 생성
        client = genai.Client(
            api_key=gms_key,
            http_options={
                "base_url": "https://gms.ssafy.io/gmsapi/generativelanguage.googleapis.com"
            }
        )
        # gemini-2.0-flash 모델 호출
        response = client.models.generate_content(
            model="gemini-2.5-pro",
            contents="""
            너는 재치있고 유행하는 밈을 좋아하는 작명가야.
            커뮤니티에 사용할 창의적인 한국어 닉네임을 하나만 추천해줘.
            5~10글자의 닉네임으로 추천해줘.
            특수문자나 이모티콘은 사용하면 안돼.
            응답은 다른 추가적인 설명 없이 오직 닉네임만 출력해.
            """
        )
        return Response({'nickname': response.text.strip()})
    except Exception as e:
        return Response({"error": str(e)}, status=500)
    
    
@api_view(['GET'])
@permission_classes([AllowAny])
def check_nickname(request):
    nickname = request.query_params.get('nickname', None)
    User = get_user_model()
    if not nickname:
        return Response({'error': '닉네임을 입력해주세요.'}, status=400)
    # DB에서 해당 닉네임이 존재하는지 확인
    exists = User.objects.filter(nickname=nickname).exists()
    return Response({
        'is_available': not exists,
        'message': '사용 가능한 닉네임입니다.' if not exists else '이미 사용 중인 닉네임입니다.'
    })