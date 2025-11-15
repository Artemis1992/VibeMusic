# vibemusic/urls.py
from django.urls import path, include
from . import views
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

app_name = 'vibemusic'

schema_view = get_schema_view(
    openapi.Info(title="VibeMusic API", default_version='v1'),
    public=True,
)

urlpatterns = [
    # === API v1 ===
    path('api/v1/', include('vibemusic.api.v1.urls')),  # ← ВСЁ API (посты, треки, лайки)

    # === JWT ===
    path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # === Swagger ===
    path('swagger/', schema_view.with_ui('swagger'), name='swagger'),

    # === HTML страницы ===
    path('', views.PostListView.as_view(), name='home'),  # ← ОСТАВЬ ТОЛЬКО ОДИН
    path('my_profile/', views.MyProfileView.as_view(), name='my_profile'),
    path('artist/<slug:artist_slug>/', views.ArtistDetailView.as_view(), name='artist_detail'),
    path('post/<slug:post_slug>/add_comment/', views.AddCommentView.as_view(), name='add_comment'),
    path('genre/<slug:genre_slug>/', views.GenreDetailView.as_view(), name='genre_detail'),
    path('post/<slug:post_slug>/', views.PostDetailView.as_view(), name='post_detail'),
    path('post/add/', views.PostCreateView.as_view(), name='add_post'),

    path('upload_track/', views.TrackUploadView.as_view(), name='upload_track'),
    path('telegram/webhook/', views.TelegramWebhookView.as_view(), name='telegram_webhook'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('contact/', views.contact, name='contact'),
    path('update_profile/', views.UpdateProfileView.as_view(), name='update_profile'),
    path('profile/<int:pk>/', views.ProfileView.as_view(), name='profile'),
    path('follow/<int:pk>/', views.toggle_follow, name='toggle_follow'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),

    # === Сброс пароля ===
    path('password-reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', views.CustomPasswordResetView.as_view(), name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset/complete/', views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('telegram_settings/', views.TelegramSettingsView.as_view(), name='telegram_settings'),
    path('logout_confirm/', views.LogoutConfirmView.as_view(), name='logout_confirm'),
]