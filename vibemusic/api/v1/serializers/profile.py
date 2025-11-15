# vibemusic/api/v1/serializers/profile.py
from rest_framework import serializers
from vibemusic.models import Profile
from .auth import UserSerializer


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    following_count = serializers.IntegerField(source='following.count', read_only=True)
    followers_count = serializers.IntegerField(source='followers.count', read_only=True)

    class Meta:
        model = Profile
        fields = ['user', 'photo', 'telegram_username', 'following_count', 'followers_count']
        read_only_fields = ['following_count', 'followers_count']