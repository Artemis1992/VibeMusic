# views.py
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Post, Genre, Artist, Comment
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import RegisterForm, CommentForm
from .utils import *
from django.conf import settings
import logging

logger = logging.getLogger(__name__)




class PostListView(DataMixin, ListView):
    model = Post
    template_name = 'vibemusic/index.html'
    context_object_name = 'posts'

    # def get_queryset(self):
    #     # Предзагрузка связанных данных для оптимизации
    #     queryset = Post.objects.select_related('artist', 'genre').prefetch_related('images', 'tracks') # Загружаем artist и genre через JOIN, а images и tracks — отдельными запросами для оптимизации
    #     genre_slug = self.request.Get.get('genre') # Извлекаем из URL GET-параметр с названием genre и сохраняем ее. Если нет то отпровляем None
    #     if genre_slug:
    #         try:
    #             genre = Genre.objects.get(name=genre_slug) # получаем обьект жанра
    #             # фильтрация по жанру поста или жанрам исполнителя.
                



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        extra_context = self.get_context_menu(title=context)
        # Пагинация постов
        posts = self.get_queryset()
        context['page_obj'] = self.get_paginated_posts(posts, self.request)
        return {**context, **extra_context}




# Регистрация
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
        context['form'] = context.get('form', self.form_class())
        extra_context = self.get_context_menu(title=context['posts'])
        return {**context, **extra_context}

# Страница жанра
class GenreDetailView(DataMixin, DetailView):
    model = Genre
    template_name = 'vibemusic/genre_detail.html'
    slug_url_kwarg = "genre_slug"
    context_object_name = 'genre'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        extra_context = self.get_context_menu(title=context['genre'].name)
        return {**context, **extra_context}

# Страница исполнителя
class ArtistDetailView(DataMixin, DetailView):
    model = Artist
    template_name = 'vibemusic/artist_detail.html'
    context_object_name = 'artist'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        extra_context = self.get_context_menu(title="Исполнитель: " + context['artist'].name)
        return {**context, **extra_context}

# Страница поста с пагинацией комментариев
class PostDetailView(DataMixin, DetailView):
    model = Post
    template_name = 'vibemusic/post_detail.html'
    slug_url_kwarg = "post_slug"
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        extra_context = self.get_context_menu(title=context['post'])
        # Пагинация комментариев
        comments = self.object.comments.all().order_by('-created_at')
        logger.debug(f"Found {comments.count()} comments for post {self.object.id}")
        context['page_obj'] = self.get_paginated_comments(comments, self.request)
        context['form'] = CommentForm()
        # Биография исполнителя
        context['artist_bio'] = self.object.artist.bio if self.object.artist else ""
        return {**context, **extra_context}

# Добавление комментария
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

# Добавление поста
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
        extra_context = self.get_context_menu(title=context('post'))
        return {**context, **extra_context}

# Страница "О сайте"
def about(request):
    return render(request, 'vibemusic/about.html', {'menu': menu, 'genres': Genre.objects.all()})

# Страница "Обратная связь"
def contact(request):
    return render(request, 'vibemusic/contact.html', {'menu': menu, 'genres': Genre.objects.all()})

# Страница профиля
@login_required
def profile(request):
    return render(request, 'vibemusic/profile.html', {'menu': menu, 'genres': Genre.objects.all()})