# views.py
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

class PostListView(ListView, DataMixin):
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

class RegisterView(DataMixin, CreateView):                                              # DataMixin и Django CreateView для обработки регистрации пользователя
    form_class = RegisterForm                                                           # Указываем пользовательскую форму RegisterForm для обработки данных регисрации
    template_name = 'vibemusic/register.html'                                           # Задаем шаблон 'vibemusic/register.html' для страницы регистрации
    success_url = reverse_lazy('login')                                                 # Обеспечиваем ленивую подгрузку URl адреса с перенапровленимем на страницу 'login'
    
    def form_valid(self, form):                                                         # Регестрируем пульзователя и показываем сообщение об успехе.
        logger.info(f"User registered: {form.cleaned_data['username']}")                # Извлекаем имя пользователя из формы и записываем в лог-файл с уровнем INFO
        response = super().form_valid(form)                                             # Вызываем form_valid() у родителя CrateView, он вызывает form_save() и перенапровляет на success_url. Результат HttpResponseRedirect сохраняем в переменную
        messages.success(self.request, 'Регистрация успешна! Пожалуйста, войдите.')     # Добавляем всплывающее сообщение для пользователей сообщение уровня успех(зеленое)
        return response
    
    def form_invalid(self, form):                                                       # При неправильной регестрации показываем сообщение об ошибке
        logger.error(f"Registration failed: {form.errors}")                             # Записываем ошибку в лог-файл в случае если пользователь совершил ошибку.
        messages.error(self.request, 'Ошибка регистрации. Проверьте данные')            # Добавили всплывающее сообщение для пользователей сообщение уровня ошибка(красное)
        return super().form_invalid(form)                                               # from_invalid() рендерим ту же страницу с формой и ее ошибками(передаем в шаблон чтобы пользователь мог увидеть и исправить)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        extra_context = self.get_context_menu(title="Регистрация")
        context['site_settings'] = SiteSettings.objects.first()  # Настройки сайта
        return {**context, **extra_context}
    



class LoginView(DataMixin, LoginView):                                                  # DataMixin и Django LoginView для обработки входа пользователя
    form_class = LoginViewForm                                                          # Указывает пользовательскую форму LoginViewForm для обработки данных входа
    template_name = 'vibemusic/login.html'                                              # Задает шаблон vibemusic/login.html для страницы входа

    def get_context_data(self, **kwargs):                                               # Переопределяет метод для настройки контекста, передаваемого в шаблон
        context = super().get_context_data(**kwargs)                                    # Получает стандартный контекст из родительского класса LoginView
        extra_context = self.get_context_menu(title='Авторизация')                      # Вызывает метод get_context_menu с заголовком "Авторизация" для добавления контекста
        site_settings = SiteSettings.objects.first()                                    # Получает первый объект SiteSettings из базы данных
        if not site_settings:                                                           # Проверяет, существует ли объект SiteSettings
            logger.warning("SiteSettings object not found in database")                 # Логирует предупреждение, если объект SiteSettings не найден
            extra_context['site_settings'] = None                                       # Устанавливает site_settings в None в дополнительном контексте
        else:                                                                           # Выполняется, если объект SiteSettings найден
            logger.info(f"LoginView SiteSettings: {site_settings}, Header Image: {site_settings.header_image.url if site_settings.header_image else 'None'}, background_image: {context.get('background_image', 'None')}") # Логирует информацию о SiteSettings, включая URL изображения заголовка и фоновое изображение
            extra_context['site_settings'] = site_settings                              # Добавляет объект SiteSettings в дополнительный контекст
        context.update(extra_context)                                                   # Обновляет основной контекст данными из extra_context
        logger.debug(f"LoginView Context: {context}")                                   # Логирует отладочную информацию о полном контексте
        return context                                                                  # Возвращает обновленный контекст для шаблона

    def get(self, request, *args, **kwargs):                                            # Обрабатывает GET-запрос для отображения страницы входа
        context = self.get_context_data()                                               # Получает контекст, вызывая метод get_context_data
        return self.render_to_response(context)                                         # Рендерит шаблон с полученным контекстом
    
    def get_success_url(self):                                                          # Определяет URL для перенаправления после успешного входа
        return reverse_lazy('vibemusic:home')                                           # Возвращает URL для имени 'vibemusic:home' с отложенной загрузкой
    
def logout_user(request):                                                               # Определяет функцию для выхода пользователя из системы
    logout(request)                                                                     # Выполняет выход пользователя, используя функцию Django logout
    return redirect('login')                                                            # Перенаправляет на страницу входа с именем 'login'

    



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
    mixin = DataMixin()
    context = mixin.get_context_menu(title="О сайте")
    context["site_settings"] = SiteSettings.objects.first()

    return render(request, 'vibemusic/about.html', context)

def contact(request):
    mixin = DataMixin()
    context = mixin.get_context_menu(title="Обратная связь")
    context['site_settings'] = SiteSettings.objects.first()

    return render(request, 'vibemusic/contact.html', context)

@login_required
def profile(request):
    mixin = DataMixin()
    context = mixin.get_context_menu(title="Профиль")
    context['site_settings'] = SiteSettings.objects.first()

    return render(request, 'vibemusic/profile.html', context)