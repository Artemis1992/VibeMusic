
# vibemusic/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, TemplateView
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView
from django.views.decorators.http import require_POST
from django.contrib.auth.views import (
    PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView,
    LoginView,
)
from .models import Post, Genre, Artist, Comment, SiteSettings, Track, Reaction, Profile
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

logger = logging.getLogger(__name__)

class PostListView(DataMixin, ProfileContextMixin, ListView):
    model = Post                                                               # Указываем модель Post для представления
    template_name = 'vibemusic/index.html'                                     # Задаём шаблон для главной страницы
    context_object_name = 'page_obj'                                           # Имя объекта пагинации в шаблоне
    paginate_by = 10                                                           # Устанавливаем количество постов на страницу

    def get_queryset(self):
        queryset = Post.objects.prefetch_related('artist', 'genre', 'images', 'tracks')  # Оптимизируем запрос с подтягиванием связанных данных
        genre_slug = self.request.GET.get('genre')                             # Получаем параметр genre из GET-запроса
        if genre_slug:                                                         # Если жанр указан в запросе
            try:
                genre = Genre.objects.get(slug=genre_slug)                     # Находим жанр по slug
                related_genre_names = genre.related_genres.values_list('name', flat=True)  # Получаем имена связанных жанров
                queryset = queryset.filter(
                    Q(genre=genre) |
                    Q(artist__genres=genre) |
                    Q(genre__name__in=related_genre_names) |
                    Q(artist__genres__name__in=related_genre_names)
                ).distinct()                                                   # Фильтруем посты по жанру или связанным жанрам
            except Genre.DoesNotExist:
                logger.warning(f"Genre with slug {genre_slug} not found")      # Логируем, если жанр не найден
        return queryset.order_by('-created_at')                             # Сортируем посты по дате создания (новые сверху)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)                        # Получаем базовый контекст от родительских классов
        context['genres'] = Genre.objects.all()                            # Добавляем все жанры в контекст
        context['site_settings'] = SiteSettings.objects.first()            # Добавляем первую запись настроек сайта
        genre_slug = self.request.GET.get('genre')                         # Получаем параметр genre из GET-запроса
        if genre_slug:                                                     # Если жанр указан
            try:
                context['selected_genre'] = Genre.objects.get(slug=genre_slug)  # Добавляем выбранный жанр в контекст
            except Genre.DoesNotExist:
                context['selected_genre'] = None                           # Устанавливаем None, если жанр не найден
        else:
            context['selected_genre'] = None                               # Устанавливаем None, если жанр не указан
        return context                                                     # Возвращаем обновлённый контекст

class PostDetailView(DataMixin, ProfileContextMixin, DetailView):
    model = Post                                                               # Указываем модель Post для представления
    template_name = 'vibemusic/post_detail.html'                               # Задаём шаблон для страницы поста
    slug_url_kwarg = "post_slug"                                               # Указываем имя параметра slug в URL
    context_object_name = 'post'                                               # Имя объекта поста в шаблоне

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)                        # Получаем базовый контекст от родительских классов
        extra_context = self.get_context_menu(title=context['post'].title) # Получаем дополнительный контекст меню
        comments = self.object.comments.all().order_by('-created_at')      # Получаем комментарии к посту, сортируем по дате
        logger.debug(f"Found {comments.count()} comments for post {self.object.id}")  # Логируем количество комментариев
        context['page_obj'] = self.get_paginated_comments(comments, self.request)  # Добавляем пагинированные комментарии
        context['form'] = CommentForm()                                    # Добавляем форму для комментариев
        context['artist_bio'] = self.object.artist.bio if self.object.artist else ""  # Добавляем биографию исполнителя, если есть
        if self.object.genre and self.object.genre.background_image:        # Проверяем наличие фонового изображения жанра
            context['background_image'] = self.object.genre.background_image.url  # Устанавливаем фоновое изображение жанра
            logger.info(f"Post genre background: {context['background_image']}")  # Логируем использование фона жанра
        elif self.object.artist and self.object.artist.genres.exists():     # Проверяем наличие жанров у исполнителя
            first_genre = self.object.artist.genres.first()                # Получаем первый жанр исполнителя
            if first_genre and first_genre.background_image:               # Проверяем наличие фонового изображения
                context['background_image'] = first_genre.background_image.url  # Устанавливаем фоновое изображение
                logger.info(f"Artist genre background: {context['background_image']}")  # Логируем использование фона исполнителя
        else:
            context['background_image'] = None                             # Устанавливаем None, если фон не найден
            logger.info("No background image set for post")                # Логируем отсутствие фона
        context['site_settings'] = SiteSettings.objects.first()            # Добавляем настройки сайта
        return {**context, **extra_context}                                # Объединяем контексты и возвращаем

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
    fields = PostForm                # Поля формы создания поста
    template_name = 'vibemusic/post_form.html'                                 # Задаём шаблон для формы создания поста
    success_url = reverse_lazy('vibemusic:home')                               # Устанавливаем URL перенаправления

    def form_valid(self, form):
        form.instance.author = self.request.user                               # Устанавливаем текущего пользователя автором
        return super().form_valid(form)                                        # Вызываем родительский метод form_valid

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)                           # Получаем базовый контекст
        extra_context = self.get_context_menu(title="Создание поста")          # Получаем контекст меню
        context['site_settings'] = SiteSettings.objects.first()                # Добавляем настройки сайта
        return {**context, **extra_context}                                    # Объединяем контексты и возвращаем

class ToggleLikeView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        logger.debug(f"User {request.user} is authenticated: {request.user.is_authenticated}")  # Добавил лог для проверки авторизации
        try:
            data = json.loads(request.body)
            type = data.get('type')
            user = request.user
            if not user.is_authenticated:
                return JsonResponse({'success': False, 'message': 'User not authenticated'}, status=403)                                                # Получаем текущего пользователя

            if type == 'track':                                                # Проверяем, если тип — трек
                track_id = data.get('track_id')                                # Получаем ID трека
                track = get_object_or_404(Track, id=track_id)                  # Находим трек или возвращаем 404
                reaction, created = Reaction.objects.get_or_create(user=user, track=track)  # Создаём или получаем реакцию
                if not created:                                                # Если реакция уже существует
                    reaction.delete()                                          # Удаляем реакцию (unlike)
                return JsonResponse({'success': True, 'like_count': track.liked_by.count()})  # Возвращаем JSON с количеством лайков

            elif type == 'comment':                                            # Проверяем, если тип — комментарий
                comment_id = data.get('comment_id')                            # Получаем ID комментария
                comment = get_object_or_404(Comment, id=comment_id)            # Находим комментарий или возвращаем 404
                reaction, created = Reaction.objects.get_or_create(user=user, comment=comment)  # Создаём или получаем реакцию
                if not created:                                                # Если реакция уже существует
                    reaction.delete()                                          # Удаляем реакцию (unlike)
                return JsonResponse({'success': True, 'like_count': comment.liked_by.count()})  # Возвращаем JSON с количеством лайков

            elif type == 'post':                                               # Проверяем, если тип — пост
                post_id = data.get('post_id')                                  # Получаем ID поста
                post = get_object_or_404(Post, id=post_id)                     # Находим пост или возвращаем 404
                reaction, created = Reaction.objects.get_or_create(user=user, post=post)  # Создаём или получаем реакцию
                if not created:                                                # Если реакция уже существует
                    reaction.delete()                                          # Удаляем реакцию (unlike)
                return JsonResponse({'success': True, 'like_count': post.liked_by.count()})  # Возвращаем JSON с количеством лайков

            elif type == 'artist':                                             # Проверяем, если тип — исполнитель
                artist_id = data.get('artist_id')                              # Получаем ID исполнителя
                artist = get_object_or_404(Artist, id=artist_id)               # Находим исполнителя или возвращаем 404
                reaction, created = Reaction.objects.get_or_create(user=user, artist=artist)  # Создаём или получаем реакцию
                if not created:                                                # Если реакция уже существует
                    reaction.delete()                                          # Удаляем реакцию (unlike)
                return JsonResponse({'success': True, 'like_count': artist.liked_by.count()})  # Возвращаем JSON с количеством лайков

            return JsonResponse({'success': False, 'message': 'Invalid type'}, status=400)  # Возвращаем ошибку для неверного типа

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON'}, status=400)  # Возвращаем ошибку для неверного JSON
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)  # Возвращаем ошибку для других исключений

class AddCommentView(LoginRequiredMixin, View):
    def post(self, request, post_slug, *args, **kwargs):
        post = get_object_or_404(Post, slug=post_slug)                         # Находим пост по slug или возвращаем 404
        form = CommentForm(request.POST, request.FILES)                        # Создаём форму с данными из запроса
        if form.is_valid():                                                    # Проверяем валидность формы
            comment = form.save(commit=False)                                  # Создаём комментарий без сохранения в БД
            comment.post = post                                                # Привязываем комментарий к посту
            comment.user = request.user                                        # Устанавливаем текущего пользователя автором
            comment.save()                                                     # Сохраняем комментарий в базу данных
            messages.success(request, "Комментарий успешно добавлен!")         # Добавляем сообщение об успехе
            return redirect('vibemusic:post_detail', post_slug=post.slug)      # Перенаправляем на страницу поста
        else:
            messages.error(request, "Ошибка при добавлении комментария.")      # Добавляем сообщение об ошибке
            return redirect('vibemusic:post_detail', post_slug=post.slug)      # Перенаправляем на страницу поста

class TelegramWebhookView(View):
    def post(self, request, *args, **kwargs):
        if request.method != 'POST':                                           # Проверяем, что запрос является POST
            return HttpResponse(status=405)                                    # Возвращаем ошибку для неразрешённого метода
        try:
            data = json.loads(request.body)                                    # Декодируем JSON из тела запроса
        except json.JSONDecodeError:
            return JsonResponse({'ok': False, 'error': 'Invalid JSON'}, status=400)  # Возвращаем ошибку для неверного JSON
        message = data.get('message') or data.get('edited_message')         # Получаем сообщение или отредактированное сообщение
        if not message:                                                    # Проверяем наличие сообщения
            return JsonResponse({'ok': True})                              # Возвращаем успешный ответ, если сообщения нет
        text = message.get('text', '')                                     # Извлекаем текст сообщения
        chat_id = message['chat'].get('id')                                # Получаем ID чата
        username = message['from'].get('username')                         # Получаем имя пользователя Telegram
        if text.startswith('/start'):                                      # Проверяем, является ли команда /start
            self._handle_start_command(chat_id, username, text)            # Обрабатываем команду /start
        return JsonResponse({'ok': True})                                  # Возвращаем успешный ответ

    def _handle_start_command(self, chat_id, username, text):
        parts = text.split()                                               # Разделяем текст на части
        if len(parts) > 1:                                                 # Проверяем наличие токена после /start
            token = parts[1]                                               # Извлекаем токен
            user_pk = unsign_telegram_connect_token(token)                 # Проверяем и расшифровываем токен
            if user_pk:                                                    # Если токен валиден
                user = get_object_or_404(User, pk=user_pk)                 # Находим пользователя или возвращаем 404
                profile, _ = Profile.objects.get_or_create(user=user)       # Получаем или создаём профиль
                profile.telegram_chat_id = chat_id                         # Устанавливаем ID чата
                profile.telegram_username = f"@{username}" if username else None  # Устанавливаем имя пользователя Telegram
                profile.save()                                             # Сохраняем профиль
                threading.Thread(
                    target=send_telegram_message,
                    args=(chat_id, "Ваш аккаунт успешно привязан к Telegram! Теперь вы можете получать уведомления.")
                ).start()                                                  # Отправляем сообщение асинхронно
            else:
                threading.Thread(
                    target=send_telegram_message,
                    args=(chat_id, "Неверный или просроченный токен. Попробуйте заново.")
                ).start()                                                  # Отправляем сообщение об ошибке
    def dispatch(self, request, *args, **kwargs):
        if request.method.lower() in self.http_method_names:                # Проверяем, поддерживается ли метод запроса
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)  # Получаем обработчик метода
            return handler(request, *args, **kwargs)                       # Вызываем обработчик
        return super().dispatch(request, *args, **kwargs)                  # Вызываем родительский dispatch

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
    form_class = LoginViewForm                                                 # Указываем форму LoginViewForm
    template_name = 'vibemusic/login.html'                                     # Задаём шаблон для входа
    success_url = reverse_lazy('vibemusic:home')                               # Устанавливаем URL перенаправления

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'vibemusic/password_reset_done.html'                       # Задаём шаблон для страницы после сброса

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'vibemusic/password_reset_confirm.html'                    # Задаём шаблон для подтверждения сброса
    success_url = reverse_lazy('vibemusic:password_reset_complete')            # Устанавливаем URL перенаправления

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'vibemusic/password_reset_complete.html'                   # Задаём шаблон для завершения сброса

class AboutView(DataMixin, ProfileContextMixin, TemplateView):
    template_name = 'vibemusic/about.html'  # Шаблон для страницы "О нас"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        extra_context = self.get_context_menu(title='О нас')  # Контекст меню
        context['site_settings'] = SiteSettings.objects.first()  # Настройки сайта
        return {**context, **extra_context}  # Объединяем контексты

def contact(request):
    mixin = DataMixin()
    context = mixin.get_context_menu(title="Обратная связь")                   # Получаем контекст меню
    context['site_settings'] = SiteSettings.objects.first()                    # Добавляем настройки сайта
    if request.user.is_authenticated:                                          # Проверяем, авторизован ли пользователь
        try:
            profile = Profile.objects.get(user=request.user)                   # Получаем профиль текущего пользователя
        except Profile.DoesNotExist:
            profile = Profile.objects.create(user=request.user)                # Создаём профиль, если он не существует
            logger.info(f"Profile создан для {request.user.username} в contact")  # Логируем создание профиля
            messages.success(request, "Профиль создан автоматически!")         # Добавляем сообщение об успехе
        context['form'] = ProfileForm(instance=profile)                        # Добавляем форму профиля
        context['user_posts'] = Post.objects.filter(author=request.user)       # Добавляем посты пользователя
        context['telegram_token'] = make_telegram_connect_token(request.user)  # Генерируем токен для Telegram
        context['TELEGRAM_BOT_USERNAME'] = getattr(settings, 'TELEGRAM_BOT_USERNAME', None)  # Получаем имя бота
    return render(request, 'vibemusic/contact.html', context)                  # Рендерим шаблон с контекстом


class ProfileView(DataMixin, ProfileContextMixin, DetailView):
    model = User
    template_name = 'vibemusic/profile.html'
    context_object_name = 'user_profile'
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        extra_context = self.get_context_menu(title=f'Профиль {self.object.username}')
        context['site_settings'] = SiteSettings.objects.first()
        context['user_posts'] = Post.objects.filter(author=self.object)
        context['following'] = self.object.profile.following.all()
        context['profile'] = self.object.profile
        context['telegram_token'] = self.request.user.profile.telegram_token if self.request.user.is_authenticated else ''
        context['TELEGRAM_BOT_USERNAME'] = settings.TELEGRAM_BOT_USERNAME
        context['activities'] = Activity.objects.filter(user=self.object)[:10]  # Последние 10 активностей
        return {**context, **extra_context}

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        profile = self.object.profile
        photo = request.FILES.get('photo')
        phone_number = request.POST.get('phone_number')

        if photo:
            profile.photo = photo
        if phone_number:
            profile.phone_number = phone_number
        profile.save()

        messages.success(request, 'Профиль успешно обновлён!')
        return redirect('vibemusic:profile', pk=self.object.id)

class UpdateProfileView(LoginRequiredMixin, ProfileContextMixin, UpdateView):
    model = Profile                                                            # Указываем модель Profile для представления
    form_class = ProfileForm                                                   # Указываем форму ProfileForm для редактирования
    template_name = 'vibemusic/base.html'                                      # Задаём шаблон base.html для формы

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
        context['TELEGRAM_BOT_USERNAME'] = getattr(settings, 'TELEGRAM_BOT_USERNAME', None)  # Получаем имя бота
        return context                                                         # Возвращаем обновлённый контекст

    def form_valid(self, form):
        messages.success(self.request, "Профиль обновлён!")                    # Добавляем сообщение об успехе
        return super().form_valid(form)                                        # Вызываем родительский метод form_valid

    def form_invalid(self, form):
        messages.error(self.request, "Ошибка в форме. Проверьте данные.")     # Добавляем сообщение об ошибке
        return super().form_invalid(form)                                      # Вызываем родительский метод form_invalid

    def get_success_url(self):
        return reverse_lazy('vibemusic:home')                                  # Устанавливаем URL перенаправления на главную



@login_required
@require_POST
def toggle_follow(request, pk):
    try:
        profile_to_follow = Profile.objects.get(user__id=pk)
        user_profile = request.user.profile
        if user_profile != profile_to_follow:
            if user_profile in profile_to_follow.followers.all():
                user_profile.following.remove(profile_to_follow)
                action = 'unfollowed'
                Activity.objects.create(
                    user=request.user,
                    message=f"Вы отписались от {profile_to_follow.user.username}"
                )
            else:
                user_profile.following.add(profile_to_follow)
                action = 'followed'
                Activity.objects.create(
                    user=request.user,
                    message=f"Вы подписались на {profile_to_follow.user.username}"
                )
                # Отправка уведомления в Telegram (если настроено)
                if profile_to_follow.telegram_chat_id:
                    # Реализуй отправку сообщения через Telegram API
                    pass
            return JsonResponse({'success': True, 'action': action})
        return JsonResponse({'success': False, 'error': 'Cannot follow yourself'})
    except Profile.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Profile not found'})