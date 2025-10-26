# vibemusic/urls.py

from django.urls import path
from django.views.decorators.cache import cache_page
from . import views
from .views import (
    PostListView, ArtistDetailView, GenreDetailView, PostCreateView, 
    PostDetailView, RegisterView, CustomLoginView, UpdateProfileView,
    ToggleLikeView, AddCommentView, TrackUploadView, TelegramWebhookView,
    PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, 
    PasswordResetCompleteView, MyProfileView, contact, logout_user,
    AboutView, ProfileView,
)

app_name = 'vibemusic'  # Пространство имён для маршрутов

urlpatterns = [
    
    path('', cache_page(60)(PostListView.as_view()), name='home'),                                  # Главная страница с кэшированием на 60 секунд
    path('my_profile/', views.MyProfileView.as_view(), name='my_profile'),
    path('artist/<slug:artist_slug>/', views.ArtistDetailView.as_view(), name='artist_detail'),           # Детали исполнителя по slug (для ссылки в base.html: {% url 'vibemusic:artist_detail' post.artist.id %})
    path('post/<slug:post_slug>/add_comment/', views.AddCommentView.as_view(), name='add_comment'),       # Добавление комментария к посту
    path('genre/<slug:genre_slug>/', views.GenreDetailView.as_view(), name='genre_detail'),               # Детали жанра по slug (для ссылки в base.html: {% url 'vibemusic:genre_detail' genre.slug %})
    path('post/<slug:post_slug>/', views.PostDetailView.as_view(), name='post_detail'),                   # Детали поста по slug
    path('post/add/', views.PostCreateView.as_view(), name='add_post'),                                   # Создание поста (для ссылки в _profile_menu.html: {% url 'vibemusic:add_post' %})
    path('toggle_like/', views.ToggleLikeView.as_view(), name='toggle_like'),                             # Переключение лайков для постов, треков и комментариев
    path('upload_track/', views.TrackUploadView.as_view(), name='upload_track'),                          # Загрузка трека
    path('telegram/webhook/', views.TelegramWebhookView.as_view(), name='telegram_webhook'),              # Вебхук для Telegram-уведомлений
    path('about/', views.AboutView.as_view(), name='about'),                                              # Страница "О нас" (для устранения NoReverseMatch)
    path('contact/', contact, name='contact'),                                                      # Страница "Контакты"
    path('update_profile/', views.UpdateProfileView.as_view(), name='update_profile'),                    # Обновление профиля (для формы в _profile_menu.html: {% url 'vibemusic:update_profile' %})
    path('profile/<int:pk>/', views.ProfileView.as_view(), name='profile'),                         # Страница профиля (раскомментировано и добавлено для поддержки меню профиля)
    path('follow/<int:pk>/', views.toggle_follow, name='toggle_follow'),                            # Подписка/отписка (для кнопки .follow-btn, отправляющей AJAX на /follow/<id>/)
    path('logout/', logout_user, name='logout'),                                                    # Выход из системы
    path('register/', views.RegisterView.as_view(), name='register'),                                     # Регистрация
    path('login/', views.CustomLoginView.as_view(), name='login'),                                        # Вход
    path('password-reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', views.CustomPasswordResetView.as_view(), name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset/complete/', views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('telegram_settings/', views.TelegramSettingsView.as_view(), name='telegram_settings'),
    path('logout_confirm/', views.LogoutConfirmView.as_view(), name='logout_confirm'),

    # Маршруты для сброса пароля
    path('password_reset/', PasswordResetView.as_view(template_name='vibemusic/password_reset.html'), name='password_reset'),
    path('password_reset/done/', PasswordResetDoneView.as_view(template_name='vibemusic/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name='vibemusic/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', PasswordResetCompleteView.as_view(template_name='vibemusic/password_reset_complete.html'), name='password_reset_complete'),
]