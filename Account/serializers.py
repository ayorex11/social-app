from rest_framework import serializers
from djoser.serializers import UserCreateSerializer
from .models import User
from djoser.serializers import UserCreateSerializer


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('id','first_name', 'last_name', 'email', 'username' ,'password')


class UserDetailsSerializer(serializers.Serializer):
    
    class Meta:
        fields = ['email', 'first_name', 'last_name',]
        read_only_fields = ['email',]
        model = User

        