# vibemusik/urls.py
from django.urls import path
from .views import PostListView, ArtistDetailView, GenreDetailView, add_comment, PostCreateView, about, contact, profile, PostDetailView, RegisterView

app_name = 'vibemusic'

urlpatterns = [
    path('', PostListView.as_view(), name='home'),
    path('artist/<int:pk>/', ArtistDetailView.as_view(), name='artist_detail'),
    path('genre/<slug:genre_slug>/', GenreDetailView.as_view(), name='genre_detail'),
    path('post/<slug:post_slug>/', PostDetailView.as_view(), name='post_detail'),
    path('post/<slug:post_slug>/comment/', add_comment, name='add_comment'),
    path('post/add/', PostCreateView.as_view(), name='add_post'),
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),
    path('profile/', profile, name='profile'),
    path('register/', RegisterView.as_view(), name='register'),
]