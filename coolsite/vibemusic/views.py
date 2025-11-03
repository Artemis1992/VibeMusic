
# vibemusic/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, TemplateView, UpdateView
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.http import require_POST
from django.http import HttpResponseRedirect
from django.contrib.auth.views import (
    PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView,
    LoginView,
)
from .models import *
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.contrib.auth import logout
from django.db.models import Q
from .forms import RegisterForm, CommentForm, LoginViewForm, TrackUploadForm, ProfileForm, PostForm
from django.views import View
from .utils import *
import threading
import logging
import json
import re

logger = logging.getLogger(__name__)

# Ваши существующие представления остаются без изменений
class PostListView(DataMixin, ProfileContextMixin, ListView):
    model = Post
    template_name = 'vibemusic/index.html'
    context_object_name = 'page_obj'
    paginate_by = 10

    def get_queryset(self):
        queryset = Post.objects.prefetch_related('artist', 'genre', 'images', 'tracks')

        # Фильтрация по жанру
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

        # Добавляем like_count и liked_by_me
        if self.request.user.is_authenticated:
            queryset = queryset.annotate(
                like_count=Count('liked_by'),
                liked_by_me=Exists(
                    Post.objects.filter(
                        id=OuterRef('pk'),
                        liked_by=self.request.user
                    )
                )
            )
        else:
            queryset = queryset.annotate(like_count=Count('liked_by'))

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['genres'] = Genre.objects.all()
        context['site_settings'] = SiteSettings.objects.first()
        genre_slug = self.request.GET.get('genre')
        if genre_slug:
            try:
                context['selected_genre'] = Genre.objects.get(slug=genre_slug)
            except Genre.DoesNotExist:
                context['selected_genre'] = None
        else:
            context['selected_genre'] = None
        extra_context = self.get_context_menu(title="Главная")
        context.update(extra_context)
        context['current_date'] = timezone.now()
        context['post_count'] = Post.objects.count()
        return context



class PostDetailView(DataMixin, ProfileContextMixin, DetailView):
    model = Post
    template_name = 'vibemusic/post_detail.html'
    slug_url_kwarg = "post_slug"
    context_object_name = 'post'

    def get_queryset(self):
        queryset = super().get_queryset()

        # === АННОТАЦИИ ДЛЯ ПОСТА ===
        if self.request.user.is_authenticated:
            queryset = queryset.annotate(
                like_count=Count('liked_by'),
                liked_by_me=Exists(
                    Post.objects.filter(id=OuterRef('pk'), liked_by=self.request.user)
                )
            )
        else:
            queryset = queryset.annotate(like_count=Count('liked_by'))

        # === АННОТАЦИИ ДЛЯ ТРЕКОВ ===
        track_queryset = Track.objects.annotate(like_count=Count('liked_by'))
        if self.request.user.is_authenticated:
            track_queryset = track_queryset.annotate(
                liked_by_me=Exists(
                    Track.objects.filter(id=OuterRef('pk'), liked_by=self.request.user)
                )
            )

        track_prefetch = Prefetch('tracks', queryset=track_queryset)

        # === АННОТАЦИИ ДЛЯ КОММЕНТАРИЕВ ===
        comment_queryset = Comment.objects.annotate(like_count=Count('liked_by'))
        if self.request.user.is_authenticated:
            comment_queryset = comment_queryset.annotate(
                liked_by_me=Exists(
                    Comment.objects.filter(id=OuterRef('pk'), liked_by=self.request.user)
                )
            )
        comment_queryset = comment_queryset.prefetch_related('replies')
        comment_prefetch = Prefetch('comments', queryset=comment_queryset)

        # === ПРИМЕНЯЕМ prefetch_related ===
        queryset = queryset.prefetch_related(track_prefetch, comment_prefetch)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        extra_context = self.get_context_menu(title=context['post'].title)

        # Комментарии с пагинацией
        comments = self.object.comments.all().order_by('-created_at')
        context['page_obj'] = self.get_paginated_comments(comments, self.request)
        context['form'] = CommentForm()
        context['artist_bio'] = self.object.artist.bio if self.object.artist else ""

        # Фон
        if self.object.genre and self.object.genre.background_image:
            context['background_image'] = self.object.genre.background_image.url
        elif self.object.artist and self.object.artist.genres.exists():
            first_genre = self.object.artist.genres.first()
            if first_genre and first_genre.background_image:
                context['background_image'] = first_genre.background_image.url
        else:
            context['background_image'] = None

        context['site_settings'] = SiteSettings.objects.first()
        return {**context, **extra_context}
    


class TrackUploadView(LoginRequiredMixin, ProfileContextMixin, CreateView):
    model = Track                                                              # Указываем модель Track для представления
    form_class = TrackUploadForm                                               # Указываем форму TrackUploadForm для ввода данных
    template_name = 'vibemusic/track_upload.html'                              # Задаём шаблон для страницы загрузки трека
    success_url = '/'                                                          # Устанавливаем URL перенаправления на главную

    def form_valid(self, form):
        try:
            track = form.save(commit=False)                                    # Создаём объект Track без сохранения в БД
            track.user = self.request.user                                     # Привязываем текущего пользователя к треку
            track.save()                                                       # Сохраняем трек в базу данных
            logger.info(f"Пользователь {self.request.user.username} загруженный трек: {track.title} (ID: {track.id})")  # Логируем успешную загрузку
            messages.success(self.request, "Трек успешно загружен!")           # Добавляем сообщение об успехе
            return redirect(reverse('track_detail', kwargs={'pk': track.pk}))  # Перенаправляем на страницу трека
        except Exception as e:
            logger.error(f"Ошибка сохранения трека пользователя {self.request.user.username}: {e}")  # Логируем ошибку
            messages.error(self.request, "Ошибка при загрузке трека. Попробуйте снова.")  # Добавляем сообщение об ошибке
            return redirect('track_upload')                                    # Перенаправляем на форму загрузки

    def form_invalid(self, form):
        logger.warning(f"Неверная отправка формы пользователем {self.request.user.username}: {form.errors}")  # Логируем ошибки формы
        messages.error(self.request, "Ошибка при загрузке трека.")         # Добавляем сообщение об ошибке
        return self.render_to_response(self.get_context_data(form=form))   # Рендерим шаблон с формой и ошибками

class RegisterView(DataMixin, CreateView):
    form_class = RegisterForm                                                  # Указываем форму RegisterForm для регистрации
    template_name = 'vibemusic/register.html'                                  # Задаём шаблон для страницы регистрации
    success_url = reverse_lazy('login')                                        # Устанавливаем URL перенаправления на login

    def form_valid(self, form):
        logger.info(f"Пользователь зарегистрирован: {form.cleaned_data['username']}")  # Логируем успешную регистрацию
        response = super().form_valid(form)                                    # Вызываем родительский метод form_valid
        messages.success(self.request, 'Регистрация успешна! Пожалуйста, войдите.')  # Добавляем сообщение об успехе
        return response                                                        # Возвращаем ответ для перенаправления

    def form_invalid(self, form):
        logger.error(f"Регистрация не удалась: {form.errors}")                # Логируем ошибки формы
        messages.error(self.request, 'Ошибка регистрации. Проверьте данные')  # Добавляем сообщение об ошибке
        return super().form_invalid(form)                                      # Рендерим шаблон с ошибками

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)                           # Получаем базовый контекст
        extra_context = self.get_context_menu(title="Регистрация")            # Получаем контекст меню
        context['site_settings'] = SiteSettings.objects.first()                # Добавляем настройки сайта
        return {**context, **extra_context}                                    # Объединяем контексты и возвращаем

class LoginView(DataMixin, LoginView):
    form_class = LoginViewForm                                                 # Указываем форму LoginViewForm для входа
    template_name = 'vibemusic/login.html'                                     # Задаём шаблон для страницы входа

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)                           # Получаем базовый контекст
        extra_context = self.get_context_menu(title='Авторизация')            # Получаем контекст меню
        site_settings = SiteSettings.objects.first()                           # Получаем первую запись настроек сайта
        if not site_settings:                                                  # Проверяем, существует ли SiteSettings
            logger.warning("Объект SiteSettings не найден в базе данных")      # Логируем предупреждение, если не найден
            extra_context['site_settings'] = None                              # Устанавливаем None для site_settings
        else:
            logger.info(f"LoginView SiteSettings: {site_settings}, Header Image: {site_settings.header_image.url if site_settings.header_image else 'None'}, background_image: {context.get('background_image', 'None')}")  # Логируем информацию о SiteSettings
            extra_context['site_settings'] = site_settings                     # Добавляем SiteSettings в контекст
        context.update(extra_context)                                          # Обновляем контекст
        logger.debug(f"LoginView Context: {context}")                          # Логируем полный контекст
        return context                                                         # Возвращаем контекст

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()                                      # Получаем контекст для шаблона
        return self.render_to_response(context)                                # Рендерим шаблон с контекстом

    def get_success_url(self):
        return reverse_lazy('vibemusic:home')                                  # Устанавливаем URL перенаправления после входа

def logout_user(request):
    logout(request)                                                            # Выполняем выход пользователя
    return redirect('login')                                                   # Перенаправляем на страницу входа

class GenreDetailView(DataMixin, ProfileContextMixin, DetailView):
    model = Genre                                                              # Указываем модель Genre для представления
    template_name = 'vibemusic/genre_detail.html'                              # Задаём шаблон для страницы жанра
    context_object_name = 'genre'                                              # Имя объекта жанра в шаблоне

    def get_object(self):
        identifier = self.kwargs.get("genre_slug")                             # Извлекаем параметр genre_slug из URL
        if str(identifier).isdigit():                                          # Проверяем, является ли идентификатор числом
            logger.debug(f"Получение жанра по id: {identifier}")               # Логируем поиск по ID
            return get_object_or_404(Genre, id=int(identifier))                # Возвращаем жанр по ID или 404
        logger.debug(f"Получение жанра по слагу: {identifier}")                # Логируем поиск по slug
        return get_object_or_404(Genre, slug=identifier)                       # Возвращаем жанр по slug или 404

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)                           # Получаем базовый контекст
        genre = self.get_object()                                              # Получаем объект жанра
        context['posts'] = (
            Post.objects.filter(Q(genre=genre) | Q(artist__genres=genre))      # Выбираем посты, связанные с жанром
            .select_related('artist', 'genre')                                 # Оптимизируем запрос для artist и genre
            .prefetch_related('images', 'tracks')                              # Оптимизируем загрузку изображений и треков
            .order_by('-created_at')                                           # Сортируем по дате создания
            .distinct()                                                        # Устраняем дубликаты
        )
        logger.info(f"Получено {context['posts'].count()} постов для жанра {genre.name}")  # Логируем количество постов
        context['site_settings'] = SiteSettings.objects.first()                # Добавляем настройки сайта
        if genre.background_image:                                             # Проверяем наличие фонового изображения
            context['background_image'] = genre.background_image.url           # Устанавливаем фоновое изображение
            logger.info(f"Genre background: {context['background_image']}")    # Логируем использование фона
        else:
            context['background_image'] = None                                 # Устанавливаем None, если фон отсутствует
            logger.info(f"No background image for genre {genre.name}")         # Логируем отсутствие фона
        extra_context = self.get_context_menu(title=f"Жанр: {genre.name}")     # Получаем контекст меню
        return {**context, **extra_context}                                    # Объединяем контексты и возвращаем

class ArtistDetailView(DataMixin, ProfileContextMixin, DetailView):
    model = Artist                                                             # Указываем модель Artist для представления
    template_name = 'vibemusic/artist_detail.html'                             # Задаём шаблон для страницы исполнителя
    slug_url_kwarg = "artist_slug"                                             # Указываем имя параметра slug в URL
    context_object_name = 'artist'                                             # Имя объекта исполнителя в шаблоне

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)                           # Получаем базовый контекст
        extra_context = self.get_context_menu(title="Исполнитель: " + context['artist'].name)  # Получаем контекст меню
        context['site_settings'] = SiteSettings.objects.first()                # Добавляем настройки сайта
        return {**context, **extra_context}                                    # Объединяем контексты и возвращаем

class PostCreateView(DataMixin, LoginRequiredMixin, ProfileContextMixin, CreateView):
    model = Post                                                               # Указываем модель Post для представления
    form_class = PostForm                                                      # Поля формы создания поста
    template_name = 'vibemusic/post_form.html'                                 # Задаём шаблон для формы создания поста
    success_url = reverse_lazy('vibemusic:home')                               # Устанавливаем URL перенаправления

    def form_valid(self, form):
        form.instance.author = self.request.user                               # Устанавливаем текущего пользователя как автора
        logger.info(f"Пользователь {self.request.user.username} создал пост: {form.cleaned_data['title']}")  # Логируем создание поста
        messages.success(self.request, "Пост успешно создан!")                 # Добавляем сообщение об успехе
        return super().form_valid(form)                                        # Вызываем родительский метод form_valid

    def form_invalid(self, form):
        logger.warning(f"Ошибка создания поста пользователем {self.request.user.username}: {form.errors}")  # Логируем ошибки формы
        messages.error(self.request, "Ошибка при создании поста. Проверьте данные.")  # Добавляем сообщение об ошибке
        return super().form_invalid(form)                                      # Рендерим шаблон с ошибками

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)                           # Получаем базовый контекст
        extra_context = self.get_context_menu(title="Создание поста")          # Получаем контекст меню
        context['site_settings'] = SiteSettings.objects.first()                # Добавляем настройки сайта
        return {**context, **extra_context}                                    # Объединяем контексты и возвращаем



from django.template.loader import render_to_string

class AddCommentView(LoginRequiredMixin, View):
    def post(self, request, post_slug, *args, **kwargs):
        post = get_object_or_404(Post, slug=post_slug)
        form = CommentForm(request.POST, request.FILES)

        # ← ВСЕГДА AJAX (или обычная форма)
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.POST.get('ajax')

        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()

            comment_count = post.comments.count()
            comment_html = render_to_string(
                'vibemusic/partials/comment_item.html',
                {'comment': comment, 'user': request.user},
                request=request
            )

            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'comment_html': comment_html,
                    'comment_count': comment_count
                })

            # ← ЕСЛИ НЕ AJAX — ПЕРЕНАПРАВЛЯЕМ
            return redirect('vibemusic:post_detail', post_slug=post.slug)

        # ← ОШИБКИ
        if is_ajax:
            return JsonResponse({'success': False, 'errors': form.errors})

        # ← ЕСЛИ НЕ AJAX — РЕНДЕРИМ СТРАНИЦУ С ОШИБКАМИ
        return render(request, 'vibemusic/post_detail.html', {
            'post': post,
            'form': form,
            'page_obj': post.comments.all(),  # или твоя пагинация
        })    

class TelegramWebhookView(View):
    def post(self, request, *args, **kwargs):
        if request.method != 'POST':                                           # Проверяем, что запрос является POST
            return HttpResponse(status=405)                                    # Возвращаем ошибку 405 (Method Not Allowed)
        try:
            data = json.loads(request.body)                                    # Парсим JSON из тела запроса
        except json.JSONDecodeError:
            return JsonResponse({'ok': False, 'error': 'Invalid JSON'}, status=400)  # Возвращаем ошибку для неверного JSON
        message = data.get('message') or data.get('edited_message')             # Получаем сообщение или отредактированное сообщение
        if not message:                                                        # Проверяем наличие сообщения
            return JsonResponse({'ok': True})                                  # Возвращаем успешный ответ, если сообщение отсутствует
        text = message.get('text', '')                                         # Получаем текст сообщения
        chat_id = message['chat'].get('id')                                    # Получаем ID чата
        username = message['from'].get('username')                             # Получаем имя пользователя Telegram
        if text.startswith('/start'):                                          # Проверяем, начинается ли сообщение с /start
            self._handle_start_command(chat_id, username, text)                # Обрабатываем команду /start
        elif text.startswith('/unsubscribe'):                                  # Проверяем, начинается ли сообщение с /unsubscribe
            self._handle_unsubscribe_command(chat_id)                          # Обрабатываем команду /unsubscribe
        return JsonResponse({'ok': True})                                      # Возвращаем успешный ответ

    def _handle_start_command(self, chat_id, username, text):                  # Метод для обработки команды /start
        parts = text.split()                                                  # Разбиваем текст на части
        if len(parts) > 1:                                                    # Проверяем наличие токена
            token = parts[1]                                                  # Извлекаем токен
            user_pk = unsign_telegram_connect_token(token)                     # Декодируем токен для получения ID пользователя
            if user_pk:                                                       # Если токен валиден
                user = get_object_or_404(User, pk=user_pk)                     # Находим пользователя по ID или возвращаем 404
                profile, _ = Profile.objects.get_or_create(user=user)           # Получаем или создаём профиль пользователя
                profile.telegram_chat_id = chat_id                             # Устанавливаем ID чата Telegram
                profile.telegram_username = f"@{username}" if username else None  # Устанавливаем имя пользователя Telegram
                profile.save()                                                 # Сохраняем изменения в профиле
                threading.Thread(                                              # Запускаем отправку сообщения в отдельном потоке
                    target=send_telegram_message,
                    args=(chat_id, "Ваш аккаунт успешно привязан к Telegram!")
                ).start()                                                      # Асинхронная отправка сообщения
            else:                                                              # Если токен недействителен
                threading.Thread(                                              # Запускаем отправку сообщения об ошибке
                    target=send_telegram_message,
                    args=(chat_id, "Неверный или просроченный токен.")
                ).start()                                                      # Асинхронная отправка сообщения

    def _handle_unsubscribe_command(self, chat_id):                            # Метод для обработки команды /unsubscribe
        try:
            profile = Profile.objects.get(telegram_chat_id=chat_id)            # Находим профиль по ID чата
            profile.telegram_chat_id = None                                    # Сбрасываем ID чата
            profile.telegram_username = None                                   # Сбрасываем имя пользователя
            profile.save()                                                     # Сохраняем изменения
            threading.Thread(                                                  # Запускаем отправку сообщения об успехе
                target=send_telegram_message,
                args=(chat_id, "Ваш аккаунт отвязан от Telegram.")
            ).start()                                                          # Асинхронная отправка сообщения
        except Profile.DoesNotExist:                                           # Обрабатываем случай, если профиль не найден
            threading.Thread(                                                  # Запускаем отправку сообщения об ошибке
                target=send_telegram_message,
                args=(chat_id, "Ошибка: профиль не найден.")
            ).start()                                                          # Асинхронная отправка сообщения

class CustomPasswordResetView(PasswordResetView):
    template_name = 'vibemusic/password_reset.html'                            # Задаём шаблон для сброса пароля
    email_template_name = 'vibemusic/password_reset_email.html'                # Задаём шаблон письма для сброса пароля
    success_url = reverse_lazy('vibemusic:password_reset_done')                # Устанавливаем URL перенаправления

    def form_valid(self, form):
        response = super().form_valid(form)                                    # Вызываем родительский метод для отправки email
        email = form.cleaned_data.get('email')                                 # Получаем email из формы
        for user in form.get_users(email):                                     # Перебираем пользователей с данным email
            try:
                profile = Profile.objects.get(user=user)                       # Получаем профиль пользователя
                if profile.telegram_chat_id:                                   # Проверяем наличие ID чата Telegram
                    uid = urlsafe_base64_encode(force_bytes(user.pk))         # Кодируем ID пользователя
                    token = default_token_generator.make_token(user)           # Генерируем токен для сброса
                    reset_url = self.request.build_absolute_uri(
                        reverse('vibemusic:password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
                    )                                                          # Формируем URL для сброса пароля
                    message = (
                        f"Запрос на сброс пароля на VibeMusic.\n\n"
                        f"Ссылки: {reset_url}\n\n"
                        "Если не вы - игнорируйте."
                    )                                                          # Формируем сообщение для Telegram
                    threading.Thread(target=send_telegram_message, args=(profile.telegram_chat_id, message)).start()  # Отправляем сообщение асинхронно
            except Profile.DoesNotExist:
                pass                                                           # Пропускаем, если профиль не найден
        return response                                                    # Возвращаем ответ



class CustomLoginView(LoginView):
    template_name = 'vibemusic/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('vibemusic:home')

    def form_valid(self, form):
        """Обработка успешного входа с JSON-ответом для AJAX."""
        response = super().form_valid(form)
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'redirect_url': self.get_success_url(),
            })
        return response

    def form_invalid(self, form):
        """Обработка ошибки входа с JSON-ответом для AJAX."""
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': 'Неверное имя пользователя или пароль.',
                'username_error': form.errors.get('username', [''])[0] if form.errors.get('username') else '',
                'password_error': form.errors.get('password', [''])[0] if form.errors.get('password') else '',
            })
        return super().form_invalid(form)
    


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'vibemusic/password_reset_done.html'                       # Задаём шаблон для страницы после сброса

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'vibemusic/password_reset_confirm.html'                    # Задаём шаблон для подтверждения сброса
    success_url = reverse_lazy('vibemusic:password_reset_complete')            # Устанавливаем URL перенаправления

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'vibemusic/password_reset_complete.html'                   # Задаём шаблон для завершения сброса

class AboutView(DataMixin, ProfileContextMixin, TemplateView):
    template_name = 'vibemusic/about.html'                                     # Шаблон для страницы "О нас"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)                           # Получаем базовый контекст
        extra_context = self.get_context_menu(title='О нас')                   # Получаем контекст меню
        context['site_settings'] = SiteSettings.objects.first()                # Добавляем настройки сайта
        return {**context, **extra_context}                                    # Объединяем контексты и возвращаем

def contact(request):
    mixin = DataMixin()                                                       # Создаём экземпляр DataMixin
    context = mixin.get_context_menu(title="Обратная связь")                   # Получаем контекст меню
    context['site_settings'] = SiteSettings.objects.first()                    # Добавляем настройки сайта
    if request.user.is_authenticated:                                          # Проверяем, авторизован ли пользователь
        try:
            profile = Profile.objects.get(user=request.user)                   # Получаем профиль текущего пользователя
        except Profile.DoesNotExist:
            profile = Profile.objects.create(user=request.user)                # Создаём профиль, если он не существует
            logger.info(f"Profile создан для {request.user.username} в contact")  # Логируем создание профиля
            messages.success(request, "Профиль создан автоматически!")         # Добавляем сообщение об успехе
        context['form'] = ProfileForm(instance=profile)                        # Добавляем форму профиля в контекст
        context['user_posts'] = Post.objects.filter(author=request.user)       # Добавляем посты пользователя
        context['telegram_token'] = make_telegram_connect_token(request.user)  # Генерируем токен для Telegram
        context['TELEGRAM_BOT_USERNAME'] = getattr(settings, 'TELEGRAM_BOT_USERNAME', None)  # Получаем имя бота из настроек
    return render(request, 'vibemusic/contact.html', context)                  # Рендерим шаблон с контекстом

class ProfileView(DataMixin, ProfileContextMixin, DetailView):
    model = User                                                              # Указываем модель User для представления
    template_name = 'vibemusic/profile.html'                                   # Задаём шаблон для страницы профиля
    context_object_name = 'user_profile'                                       # Имя объекта профиля в шаблоне
    pk_url_kwarg = 'pk'                                                       # Указываем имя параметра pk в URL

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)                           # Получаем базовый контекст
        extra_context = self.get_context_menu(title=f'Профиль {self.object.username}')  # Получаем контекст меню
        context['site_settings'] = SiteSettings.objects.first()                # Добавляем настройки сайта
        context['user_posts'] = Post.objects.filter(author=self.object)        # Добавляем посты пользователя
        context['following'] = self.object.profile.following.all()             # Добавляем список подписок
        context['profile'] = self.object.profile                              # Добавляем объект профиля
        context['telegram_token'] = make_telegram_connect_token(self.request.user) if self.request.user.is_authenticated else ''  # Генерируем токен для Telegram, если пользователь авторизован
        context['TELEGRAM_BOT_USERNAME'] = settings.TELEGRAM_BOT_USERNAME      # Получаем имя бота из настроек
        context['activities'] = Activity.objects.filter(user=self.object)[:10] # Добавляем последние 10 активностей пользователя
        return {**context, **extra_context}                                    # Объединяем контексты и возвращаем

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()                                        # Получаем объект пользователя
        profile = self.object.profile                                         # Получаем профиль пользователя
        photo = request.FILES.get('photo')                                     # Получаем загруженное фото из запроса
        phone_number = request.POST.get('phone_number')                        # Получаем номер телефона из запроса

        if photo:                                                              # Проверяем наличие фото
            profile.photo = photo                                              # Устанавливаем новое фото
        if phone_number and re.match(r'^\+7\d{10}$', phone_number):            # Проверяем формат номера телефона
            profile.phone_number = phone_number                                # Устанавливаем новый номер телефона
        else:
            messages.error(request, 'Неверный формат номера телефона.')        # Добавляем сообщение об ошибке
            return redirect('vibemusic:profile', pk=self.object.id)            # Перенаправляем на страницу профиля

        profile.save()                                                         # Сохраняем изменения в профиле
        messages.success(request, 'Профиль успешно обновлён!')                 # Добавляем сообщение об успехе
        return redirect('vibemusic:profile', pk=self.object.id)                # Перенаправляем на страницу профиля

class UpdateProfileView(LoginRequiredMixin, ProfileContextMixin, UpdateView):
    model = Profile                                                            # Указываем модель Profile для представления
    form_class = ProfileForm                                                   # Указываем форму ProfileForm для редактирования
    template_name = 'vibemusic/profile_form.html'                              # Задаём шаблон для формы

    def get_object(self, queryset=None):
        try:
            return self.request.user.profile                                   # Получаем профиль текущего пользователя
        except Profile.DoesNotExist:
            profile = Profile.objects.create(user=self.request.user)           # Создаём профиль, если он не существует
            logger.info(f"Profile создан для {self.request.user.username} в UpdateProfileView")  # Логируем создание профиля
            messages.success(self.request, "Профиль создан автоматически!")    # Добавляем сообщение об успехе
            return profile                                                     # Возвращаем созданный профиль

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)                           # Получаем базовый контекст
        context['user_posts'] = Post.objects.filter(author=self.request.user)  # Добавляем посты пользователя
        context['telegram_token'] = make_telegram_connect_token(self.request.user)  # Генерируем токен для Telegram
        context['TELEGRAM_BOT_USERNAME'] = getattr(settings, 'TELEGRAM_BOT_USERNAME', None)  # Получаем имя бота из настроек
        return context                                                         # Возвращаем обновлённый контекст

    def form_valid(self, form):
        messages.success(self.request, "Профиль обновлён!")                    # Добавляем сообщение об успехе
        return super().form_valid(form)                                        # Вызываем родительский метод form_valid

    def form_invalid(self, form):
        messages.error(self.request, "Ошибка в форме. Проверьте данные.")     # Добавляем сообщение об ошибке
        return super().form_invalid(form)                                      # Вызываем родительский метод form_invalid

    def get_success_url(self):
        return reverse_lazy('vibemusic:home')                                  # Устанавливаем URL перенаправления на главную

# Новое представление для отображения профиля пользователя
class MyProfileView(LoginRequiredMixin, ProfileContextMixin, DataMixin, TemplateView):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'
    template_name = 'vibemusic/my_profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_profile = self.request.user.profile
        context['user_profile'] = user_profile
        context['following'] = user_profile.following.all()
        context['user_posts'] = Post.objects.filter(author=self.request.user)
        context['edit_form'] = ProfileForm(instance=user_profile)
        context['title'] = "Мой профиль"
        context['current_datetime'] = timezone.now()
        context['site_settings'] = SiteSettings.objects.first()
        return context

    def post(self, request, *args, **kwargs):
        user_profile = request.user.profile
        action = request.POST.get('action')
        edit_form = ProfileForm(request.POST, request.FILES, instance=user_profile)

        if action == 'edit_profile' and edit_form.is_valid():
            edit_form.save()
            messages.success(request, "Профиль успешно обновлён!")
            return redirect('vibemusic:my_profile')

        elif action == 'delete_post':
            post_id = request.POST.get('post_id')
            try:
                post = Post.objects.get(id=post_id, author=request.user)
                post.delete()
                messages.success(request, "Пост успешно удалён!")
            except Post.DoesNotExist:
                messages.error(request, "Пост не найден или вам не принадлежит.")
            return redirect('vibemusic:my_profile')

        if edit_form.errors:
            messages.error(request, "Ошибка при обновлении профиля. Проверьте введённые данные.")

        context = self.get_context_data()
        context['edit_form'] = edit_form
        return self.render_to_response(context)



# Новое представление для настройки Telegram
class TelegramSettingsView(LoginRequiredMixin, ProfileContextMixin, DataMixin, TemplateView):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'
    template_name = 'vibemusic/telegram_settings.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_profile = self.request.user.profile
        context['user_profile'] = user_profile
        context['telegram_token'] = make_telegram_connect_token(self.request.user)
        context['TELEGRAM_BOT_USERNAME'] = getattr(settings, 'TELEGRAM_BOT_USERNAME', None)
        context['title'] = "Настройки Telegram"
        context['site_settings'] = SiteSettings.objects.first()
        return context



class LogoutConfirmView(LoginRequiredMixin, ProfileContextMixin, DataMixin, TemplateView):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'
    template_name = 'vibemusic/logout_confirm.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            logger.debug("User already logged out, redirecting to home")
            return HttpResponseRedirect(reverse_lazy('vibemusic:home'))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_context_menu(title='Подтверждение выхода'))
        return context

    def post(self, request):
        logger.debug(f"Logout attempt for user: {request.user.username if request.user.is_authenticated else 'anonymous'}")
        if request.user.is_authenticated:
            request.session.flush()  # Полная очистка сессии
            logout(request)  # Завершение сессии
            logger.debug(f"Logout successful for user: {request.user.username}")
        else:
            logger.debug("User was not authenticated during logout")
        response = HttpResponseRedirect(reverse_lazy('vibemusic:home'))
        response.delete_cookie('sessionid')  # Явное удаление куки сессии
        return response
    
    
@login_required
@require_POST
def toggle_follow(request, pk):
    try:
        profile_to_follow = Profile.objects.get(user__id=pk)                   # Находим профиль пользователя по ID
        user_profile = request.user.profile                                   # Получаем профиль текущего пользователя
        if user_profile != profile_to_follow:                                  # Проверяем, что пользователь не пытается подписаться на себя
            if user_profile in profile_to_follow.followers.all():              # Проверяем, подписан ли уже пользователь
                user_profile.following.remove(profile_to_follow)               # Удаляем подписку (отписка)
                action = 'unfollowed'                                          # Устанавливаем действие как "отписка"
                Activity.objects.create(                                       # Создаём запись активности
                    user=request.user,
                    message=f"Вы отписались от {profile_to_follow.user.username}"
                )
            else:                                                              # Если подписки нет
                user_profile.following.add(profile_to_follow)                  # Добавляем подписку
                action = 'followed'                                            # Устанавливаем действие как "подписка"
                Activity.objects.create(                                       # Создаём запись активности
                    user=request.user,
                    message=f"Вы подписались на {profile_to_follow.user.username}"
                )
                if profile_to_follow.telegram_chat_id:                          # Проверяем наличие ID чата Telegram
                    pass                                                      # Реализуйте отправку сообщения через Telegram API, если нужно
            return JsonResponse({'success': True, 'action': action})            # Возвращаем JSON с успешным результатом
        return JsonResponse({'success': False, 'error': 'Cannot follow yourself'})  # Возвращаем ошибку, если попытка подписки на себя
    except Profile.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Profile not found'})   # Возвращаем ошибку, если профиль не найден