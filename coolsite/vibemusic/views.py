from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView
from .models import Post, Genre, Artist, Comment, SiteSettings
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import logout
from django.db.models import Q
from .forms import RegisterForm, CommentForm, LoginViewForm
from .utils import *
import logging

logger = logging.getLogger(__name__)

class PostListView(ListView):
    model = Post
    template_name = 'vibemusic/index.html'
    context_object_name = 'page_obj'
    paginate_by = 10

    def get_queryset(self):
        queryset = Post.objects.select_related('artist', 'genre').prefetch_related('images', 'tracks')
        genre_slug = self.request.GET.get('genre')
        if genre_slug:
            try:
                genre = Genre.objects.get(slug=genre_slug)
                related_genre_names = genre.related_genres.values_list('name', flat=True)
                queryset = queryset.filter(
                    Q(genre=genre) |
                    Q(artist__genres=genre) |
                    Q(genre__name__in=related_genre_names) |
                    Q(artist__genres__name__in=related_genre_names)
                ).distinct()
            except Genre.DoesNotExist:
                logger.warning(f"Genre with slug {genre_slug} not found")
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['genres'] = Genre.objects.all()
        context['site_settings'] = SiteSettings.objects.first()  # Настройки сайта
        genre_slug = self.request.GET.get('genre')
        if genre_slug:
            try:
                context['selected_genre'] = Genre.objects.get(slug=genre_slug)
            except Genre.DoesNotExist:
                context['selected_genre'] = None
        else:
            context['selected_genre'] = None
        return context

class PostDetailView(DataMixin, DetailView):
    model = Post
    template_name = 'vibemusic/post_detail.html'
    slug_url_kwarg = "post_slug"
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        extra_context = self.get_context_menu(title=context['post'].title)
        # Пагинация комментариев
        comments = self.object.comments.all().order_by('-created_at')
        logger.debug(f"Found {comments.count()} comments for post {self.object.id}")
        context['page_obj'] = self.get_paginated_comments(comments, self.request)
        context['form'] = CommentForm()
        # Биография исполнителя
        context['artist_bio'] = self.object.artist.bio if self.object.artist else ""
        # Фон на основе жанра поста или первого жанра исполнителя
        if self.object.genre and self.object.genre.background_image:
            context['background_image'] = self.object.genre.background_image.url
            logger.info(f"Post genre background: {context['background_image']}")
        elif self.object.artist and self.object.artist.genres.exists():
            first_genre = self.object.artist.genres.first()
            if first_genre and first_genre.background_image:
                context['background_image'] = first_genre.background_image.url
                logger.info(f"Artist genre background: {context['background_image']}")
        else:
            context['background_image'] = None
            logger.info("No background image set for post")
        # Добавляем настройки сайта
        context['site_settings'] = SiteSettings.objects.first()
        return {**context, **extra_context}

class RegisterView(DataMixin, CreateView):
    form_class = RegisterForm
    template_name = 'vibemusic/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        logger.info(f"User registered: {form.cleaned_data['username']}")
        response = super().form_valid(form)
        messages.success(self.request, 'Регистрация успешна! Пожалуйста, войдите.')
        return response
    
    def form_invalid(self, form):
        logger.error(f"Registration failed: {form.errors}")
        messages.error(self.request, 'Ошибка регистрации. Проверьте данные')
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        extra_context = self.get_context_menu(title="Регистрация")
        context['site_settings'] = SiteSettings.objects.first()  # Настройки сайта
        return {**context, **extra_context}
    



class LoginView(DataMixin, LoginView):
    form_class = LoginViewForm
    template_name = 'vibemusic/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        extra_context = self.get_context_menu(title='Авторизация')
        extra_context['site_settings'] = SiteSettings.objects.first()
        return {**context, **extra_context}
    
    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        context['site_settings'] = SiteSettings.objects.first()
        return self.render_to_response(context)
    
    def get_success_url(self):
        return reverse_lazy('vibemusic:home')
    
def logout_user(request):
    logout(request)
    return redirect('login')


    




class GenreDetailView(DataMixin, DetailView):
    model = Genre
    template_name = 'vibemusic/genre_detail.html'
    context_object_name = 'genre'

    def get_object(self):
        identifier = self.kwargs.get("genre_slug")
        if str(identifier).isdigit():
            return get_object_or_404(Genre, id=int(identifier))
        return get_object_or_404(Genre, slug=identifier)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        genre = self.get_object()
        # Получаем посты, связанные с жанром напрямую или через исполнителя
        context['posts'] = Post.objects.filter(
            Q(genre=genre) | Q(artist__genres=genre)
        ).select_related('artist', 'genre').prefetch_related('images', 'tracks').order_by('-created_at').distinct()
        # Добавляем настройки сайта
        context['site_settings'] = SiteSettings.objects.first()
        # Фон жанра
        if genre.background_image:
            context['background_image'] = genre.background_image.url
            logger.info(f"Genre background: {context['background_image']}")
        else:
            context['background_image'] = None
            logger.info(f"No background image for genre {genre.name}")
        extra_context = self.get_context_menu(title=f"Жанр: {genre.name}")
        return {**context, **extra_context}

class ArtistDetailView(DataMixin, DetailView):
    model = Artist
    template_name = 'vibemusic/artist_detail.html'
    slug_url_kwarg = "artist_slug"
    context_object_name = 'artist'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        extra_context = self.get_context_menu(title="Исполнитель: " + context['artist'].name)
        context['site_settings'] = SiteSettings.objects.first()  # Настройки сайта
        return {**context, **extra_context}

@login_required
def add_comment(request, post_slug):
    try:
        post = Post.objects.get(slug=post_slug)
    except Post.DoesNotExist:
        messages.error(request, "Пост не найден.")
        return redirect('vibemusic:home')

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            Comment.objects.create(
                post=post,
                user=request.user,
                content=form.cleaned_data['content']
            )
            messages.success(request, "Комментарий успешно добавлен!")
            return redirect('vibemusic:post_detail', post_slug=post.slug)
        else:
            messages.error(request, "Комментарий не может быть пустым.")
    return redirect('vibemusic:post_detail', post_slug=post.slug)

class PostCreateView(DataMixin, LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content', 'artist', 'images', 'tracks']
    template_name = 'vibemusic/post_form.html'
    success_url = reverse_lazy('vibemusic:home')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        extra_context = self.get_context_menu(title="Создание поста")
        context['site_settings'] = SiteSettings.objects.first()  # Настройки сайта
        return {**context, **extra_context}

def about(request):
    context = {
        'menu': menu,
        'genres': Genre.objects.all(),
        'site_settings': SiteSettings.objects.first(),  # Настройки сайта
    }
    return render(request, 'vibemusic/about.html', context)

def contact(request):
    context = {
        'menu': menu,
        'genres': Genre.objects.all(),
        'site_settings': SiteSettings.objects.first(),  # Настройки сайта
    }
    return render(request, 'vibemusic/contact.html', context)

@login_required
def profile(request):
    context = {
        'menu': menu,
        'genres': Genre.objects.all(),
        'site_settings': SiteSettings.objects.first(),  # Настройки сайта
    }
    return render(request, 'vibemusic/profile.html', context)