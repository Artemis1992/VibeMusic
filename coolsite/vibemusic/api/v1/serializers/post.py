# vibemusic/api/v1/serializers/post.py

from rest_framework import serializers
from vibemusic.models import Post, PostImage
from .auth import UserSerializer


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ['image', 'caption']


class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)                                         # клиент не может менять автора через API - оно только для чтения.
    images = PostImageSerializer(many=True, read_only=True)                         # many=True говорит, что это список объектов. read_only=True - нельзя создавать или менять изображения через этот сериализатор.
    like_count = serializers.IntegerField(source='liked_by.count', read_only=True)  # like_count — вычисляемое поле, показывающее количество лайков, берётся из liked_by.count и доступно только для чтения.
    liked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'content', 'author',
            'artist', 'genre', 'created_at', 'images',
            'like_count', 'liked'
        ]
        read_only_fields = ['slug', 'author', 'like_count', 'liked']

    def get_liked(self, obj):
        user = self.context['request'].user
        return user.is_authenticated and obj.liked_by.filter(id=user.id).exists()