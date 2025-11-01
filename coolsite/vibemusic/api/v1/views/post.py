# api/v1/views/post.py


from rest_framework import viewsets, filters                                # Импортируем базовые классы для ViewSet и фильтры поиска и сортировки
from vibemusic.models import Post
from ..serializers.post import PostSerializer                               # Импорт сериализатора для Post
from rest_framework.permissions import IsAuthenticatedOrReadOnly            # Импорт права доступа: авторизованный может писать, все могут читать


class PostViewSet(viewsets.ReadOnlyModelViewSet):                           # ReadOnlyModelViewSet - только просмотр, нужен queryset; в like.py лайки вручную, queryset не нужен
    # Оптимизация: .select_related жадная загрузка связей один-к-одному/многие-к-одному
    # Оптимизация: .prefetch_related жадная загрузка связей многие-ко-многим/обратные связи
    queryset = Post.objects.select_related('author', 'artist', 'genre')\
                          .prefetch_related('images', 'tracks', 'comments')\
                          .order_by('-created_at')                          # Сортировка постов по дате создания от новых к старым
    serializer_class = PostSerializer                                       # Сериализатор, который превращает объекты Post в JSON
    lookup_field = 'slug'                                                   # Позволяет получать пост по slug вместо id в URL
    permission_classes = [IsAuthenticatedOrReadOnly]                        # Права доступа: все могут читать, только авторизованные могут писать (если бы были write-методы)
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]        # Подключаем фильтры поиска и сортировки
    search_fields = ['title', 'content', 'artist__name']                    # Поля для поиска (через ?search=)
    ordering_fields = ['created_at', 'like_count']                          # Поля, по которым можно сортировать (через ?ordering=)
