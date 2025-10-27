# vibemusic/urls.py
from django.urls import path
from django.views.decorators.cache import cache_page
from . import views
from .views import (
    PostListView, ArtistDetailView, GenreDetailView, PostCreateView,
    PostDetailView, RegisterView, CustomLoginView, UpdateProfileView,
    ToggleLikeView, AddCommentView, TrackUploadView, TelegramWebhookView,
    PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView,
    PasswordResetCompleteView, MyProfileView, contact,
    AboutView, ProfileView,
)

app_name = 'vibemusic'

urlpatterns = [
    path('', (PostListView.as_view()), name='home'),
    path('my_profile/', views.MyProfileView.as_view(), name='my_profile'),
    path('artist/<slug:artist_slug>/', views.ArtistDetailView.as_view(), name='artist_detail'),
    path('post/<slug:post_slug>/add_comment/', views.AddCommentView.as_view(), name='add_comment'),
    path('genre/<slug:genre_slug>/', views.GenreDetailView.as_view(), name='genre_detail'),
    path('post/<slug:post_slug>/', views.PostDetailView.as_view(), name='post_detail'),
    path('post/add/', views.PostCreateView.as_view(), name='add_post'),
    path('toggle_like/', views.ToggleLikeView.as_view(), name='toggle_like'),
    path('upload_track/', views.TrackUploadView.as_view(), name='upload_track'),
    path('telegram/webhook/', views.TelegramWebhookView.as_view(), name='telegram_webhook'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('contact/', contact, name='contact'),
    path('update_profile/', views.UpdateProfileView.as_view(), name='update_profile'),
    path('profile/<int:pk>/', views.ProfileView.as_view(), name='profile'),
    path('follow/<int:pk>/', views.toggle_follow, name='toggle_follow'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('password-reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', views.CustomPasswordResetView.as_view(), name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset/complete/', views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('telegram_settings/', views.TelegramSettingsView.as_view(), name='telegram_settings'),
    path('logout_confirm/', views.LogoutConfirmView.as_view(), name='logout_confirm'),
    path('password_reset/', PasswordResetView.as_view(template_name='vibemusic/password_reset.html'), name='password_reset'),
    path('password_reset/done/', PasswordResetDoneView.as_view(template_name='vibemusic/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name='vibemusic/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', PasswordResetCompleteView.as_view(template_name='vibemusic/password_reset_complete.html'), name='password_reset_complete'),
]