# vibemusic/api/v1/urls.py
from django.urls import path, include                   # Импортируем функции path для определения маршрутов (URL-путей) и include для подключения других файлов с маршрутами, чтобы структурировать API по разным версиям или приложениям
from rest_framework.routers import DefaultRouter        # Импортируем DefaultRouter из DRF, который автоматически создаёт маршруты (URL) для ViewSet-ов, позволяя нам не писать каждый путь вручную
from .views.post import PostViewSet                     # Путь к PostViewSet/api/v1/post.py
from .views.track import TrackViewSet     
from .views.like import LikeViewSet       


router = DefaultRouter()
router.register(r'posts', PostViewSet)                  # Регистрируем маршрут 'posts' для PostViewSet, чтобы DRF автоматически создавал URL для операций с постами (raw string)
router.register(r'tracks', TrackViewSet)
router.register(r'like', LikeViewSet, basename='like')  # Регистрируем маршрут 'like' для LikeViewSet с указанием базового имени 'like'; DRF будет автоматически создавать URL для операций с лайками

urlpatterns = [
    path('', include(router.urls)),                     # Подключаем все маршруты, созданные DefaultRouter, чтобы они стали доступными по URL текущего приложения
]



