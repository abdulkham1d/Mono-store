import base64

from django.contrib.auth import authenticate
from rest_framework.authentication import BaseAuthentication

from apps.users.models import *
from apps.users.utils import verify_jwt_token


class BasicAuthentication(BaseAuthentication):

    def get_header(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')

        if isinstance(auth_header, str):
            auth_header = auth_header.encode()

        return auth_header

    def authenticate(self, request):
        auth_header = self.get_header(request).split()

        if len(auth_header) != 2 or auth_header[0].lower() != b'basic':
            return None

        if auth_header is None:
            return None

        auth_header = base64.b64decode(auth_header[1]).decode()
        username, password = auth_header.split(':')

        user = authenticate(request=request, username=username, password=password)

        if user is None:
            return None

        return (user, None)


class TokenAuthentication(BaseAuthentication):
    keyword = b'token'

    def get_header(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')

        if isinstance(auth_header, str):
            auth_header = auth_header.encode()

        return auth_header

    def authenticate(self, request):
        auth_header = self.get_header(request)

        if not auth_header:
            return None

        auth_header = auth_header.split()

        if len(auth_header) != 2 or auth_header[0].lower() != self.keyword:
            return None

        try:
            token = Token.objects.select_related('user').get(token=auth_header[1].decode())
        except Token.DoesNotExist:
            return None

        return (token.user, token)


class JWTAuthentication(BaseAuthentication):

    def authenticate(self, request):
        token = request.headers.get('Authorization', '').split()

        if len(token) != 2 or token[0].lower() != 'bearer':
            return None

        try:
            payload = verify_jwt_token(token[1])

            if not payload:
                return None

            return (User.objects.get(pk=payload['user_id']), None)

        except Exception as e:
            return None
