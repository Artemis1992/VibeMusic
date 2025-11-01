# api/v1/views/track.py

from rest_framework import viewsets, filters
from vibemusic.models import Track
from ..serializers.track import TrackSerializer                 # Импортируем класс TrackSerializer из файла track.py, 


class TrackViewSet(viewsets.ReadOnlyModelViewSet):
    # делаем один оптимизированный запрос к БД, который получает все треки и связанные с ними данные артистов
    queryset = Track.objects.select_related('artist').all()    # объединяем данные в один SQL-запрос (JOIN) с помощью select_related().
    serializer_class = TrackSerializer                          # Указываем сериализатор, который будет преобразовывать объекты Track в JSON и обратно.
    filter_backends = [filters.SearchFilter]                    # Подключаем фильтр поиска, чтобы можно было искать объекты через query-параметр ?search= в URL.
    search_fields = ['title', 'artist__name']                   # Указываем поля для поиска: по названию трека и имени артиста (двойное подчёркивание позволяет искать по связанным моделям).