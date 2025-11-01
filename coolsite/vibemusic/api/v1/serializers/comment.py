# vibemusic/api/v1/serializers/comment.py

from rest_framework import serializers
from vibemusic.models import Comment
from .auth import UserSerializer


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    liked = serializers.SerializerMethodField()

    class Meta:
        model = Comment                                                     # Указываем, что сериализатор работает с моделью Comment.
        fields = ['id', 'content', 'user', 'created_at', 'image', 'liked']  # Список полей, которые будут возвращаться в JSON: id, текст комментария, автор, дата создания, изображение и статус лайка.
        read_only_fields = ['user', 'created_at', 'liked']                  # Эти поля доступны только для чтения — пользователь не может их изменить (заполняются автоматически на сервере).

    def get_liked(self, obj):                                               # Метод принадлежит CommentSerializer (или TrackSerializer) и вычисляет, лайкнул ли текущий пользователь объект.
        user = self.context['request'].user                                 # Берём текущего пользователя, сделавшего запрос. Если он авторизован — это объект User, иначе AnonymousUser.
        return user.is_authenticated and obj.liked_by.filter(id=user.id).exists()   # Возвращает True, если пользователь вошёл в систему и уже лайкнул этот объект, иначе False.