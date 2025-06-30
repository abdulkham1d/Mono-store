from rest_framework import serializers
from apps.users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'is_staff', 'is_superuser')


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'is_staff', 'is_superuser')


class LoginConfirmSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6)
    username = serializers.CharField(max_length=150)


class UsernameAndPasswordSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(max_length=15)
