import uuid

from django.contrib.auth import authenticate
from django.core.cache import cache
from django.utils import timezone
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.authentication import JWTAuthentication
from apps.users.models import Token
from apps.users.serializers import *
from apps.users.utils import generate_token, generate_code, create_jwt_token


class UserDetailView(RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_object(self):
        return self.request.user


class Login(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, _ = User.objects.get_or_create(username=serializer.validated_data['username'])

        try:
            token = Token.objects.get(user=user)
        except Token.DoesNotExist:
            token = Token.objects.create(user=user, token=generate_token())
        return Response({'token': token.token, 'user_id': user.pk})


class LoginOtp(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserDetailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = generate_code()
        if cache.keys(f'otp_{serializer.validated_data["username"]}'):
            return Response({'data': 'sms_already_sent'})

        cache.set(f'otp_{serializer.validated_data["username"]}', code, 60 * 2)

        return Response({'data': 'sms_sent'})


class LoginConfirm(APIView):
    def post(self, request, *args, **kwargs):
        serializer = LoginConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code_in_cache = cache.get(f'otp_{serializer.validated_data["username"]}')

        if code_in_cache != serializer.validated_data['code']:
            return Response({'data': 'wrong_code'})

        cache.delete(f'otp_{serializer.validated_data["username"]}')

        user, _ = User.objects.get_or_create(username=serializer.validated_data["username"])

        try:
            token = Token.objects.get(user=user)
        except Token.DoesNotExist:
            token = Token.objects.create(user=user, token=generate_token())

        return Response({'token': token.token, 'user_id': user.pk})


class LoginWithUsernameAndPassword(APIView):

    def post(self, request, *args, **kwargs):
        serializer = UsernameAndPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(request=request, username=serializer.validated_data['username'],
                            password=serializer.validated_data['password'])

        if user is None:
            return Response({'data': 'Invalid INFO'})

        payload = {
            'user_id': user.id,
            'expired_date': (timezone.now() + timezone.timedelta(minutes=2)).timestamp(),
        }

        return Response({'token': create_jwt_token(payload)})
