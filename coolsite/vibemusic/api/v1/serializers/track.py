from rest_framework import serializers
from vibemusic.models import Track, Artist


class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = ['id', 'name', 'slug', 'photo']                # Не ID, а полный объект артиста - фронтенд получает сразу:


class TrackSerializer(serializers.ModelSerializer):
    artist = ArtistSerializer(read_only=True)                   # Вложенный сериализатор для артиста, только для чтения (не изменяется через TrackSerializer)
    liked = serializers.SerializerMethodField()                 # Поле для динамического вычисления, лайкнул ли текущий пользователь трек. будет вычисляться методом

    class Meta:
        model = Track
        fields = ['id', 'title', 'artist', 'audio_file', 'album_image', 'liked']    # Meta просто описывает модель и поля

    def get_liked(self, obj):                                   # Метод принадлежит TrackSerializer, вычисляет, лайкнул ли текущий пользователь трек
        user = self.context['request'].user                     # Берём текущего пользователя, который сделал запрос. Если пользователь авторизован — это объект User, иначе AnonymousUser.
        return user.is_authenticated and obj.liked_by.filter(id=user.id).exists()   # Возвращает True, если пользователь авторизован и уже лайкнул трек, иначе False.