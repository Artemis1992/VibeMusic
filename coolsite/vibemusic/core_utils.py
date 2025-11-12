# utils.py
from django.db.models import *
from django.utils.text import slugify
from django.core.signing import TimestampSigner
from django.template.loader import render_to_string
from django.core.paginator import Paginator
from .models import *

from django.conf import settings
from django.contrib import messages
from vibemusic.utils.telegram import TelegramConnector
# для работы со Spotyfi
from mutagen.mp3 import MP3
from mutagen.id3 import ID3

import logging
import requests

from django.utils import timezone  # Добавлено для current_datetime




logger = logging.getLogger(__name__)
signer = TimestampSigner()                                    # Использует SECRET_KEY для подписи      

menu = [
    {"title": "Главная", "url_name": "vibemusic:home"},
    {"title": "О сайте", "url_name": "vibemusic:about"},
    {"title": "Обратная связь", "url_name": "vibemusic:contact"},
]

class DataMixin:

    def get_context_menu(self, **kwargs):
        from vibemusic.models import Genre
        context = kwargs.copy()
        context['menu'] = menu
        context['genres'] = Genre.objects.all()               # Cписок всех жанров из модели Genre
        return context

    def get_paginated_comments(self, comments, request):
        """Возвращает объект пагинатора для комментариев"""
        logger.debug(f"Постраничная разбивка комментариев: {settings.COMMENTS_PER_PAGE} на страницу")# Записываем в лог информацию о количестве комментариев на одну страницу
        paginator = Paginator(comments, settings.COMMENTS_PER_PAGE)                                 # Создаём объект пагинатора: разбивает список comments по N на страницу
        page_number = request.GET.get('page')                                                       # Получаем номер текущей страницы из параметра запроса (например, ?page=2)
        page_obj = paginator.get_page(page_number)                                                  # Получаем объект страницы с комментариями для данного номера
        logger.debug(f"Comments page number: {page_number}, Total pages: {paginator.num_pages}")    # Логируем текущую страницу и общее количество страниц
        return page_obj                                                                             # Возвращаем объект страницы — его можно использовать в шаблоне как page_obj
    

    # Метод для постраничного вывода постов (аналогично предыдущему, только для постов)
    def get_paginated_posts(self, posts, request):
        """Возвращаем обьект пагинатора для постов"""
        logger.debug(f"Paginating posts with {settings.POSTS_PER_PAGE} per page")                   # Логируем информацию о постах: сколько постов на одной странице
        paginator = Paginator(posts, settings.POSTS_PER_PAGE)                                       # Создаём пагинатор для постов (разбиваем их по N на страницу)
        page_number = request.GET.get('page')                                                       # Получаем номер нужной страницы из запроса
        page_obj = paginator.get_page(page_number)                                                  # Получаем номер нужной страницы из запроса
        logger.debug(f"Posts page number: {page_number}, Total pages: {paginator.num_pages}")       # Логируем номер текущей страницы и общее количество
        return page_obj                                                                             # Возвращаем объект страницы с постами



class ProfileContextMixin:
    """Миксин для добавления данных профиля в контекст."""
    def get_context_data(self, **kwargs):
        from vibemusic.models import Profile, Post                                                  # Локальный импорт
        from .forms import ProfileForm
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:                                                      # Проверяем, авторизован ли пользователь
            try:
                profile = Profile.objects.get(user=self.request.user)                               # Получаем профиль текущего пользователя
            except Profile.DoesNotExist:
                profile = Profile.objects.create(user=self.request.user)                            # Создаём профиль, если он не существует
                logger.info(f"Profile создан для {self.request.user.username} в {self.__class__.__name__}")  # Логируем создание профиля
                messages.success(self.request, "Профиль создан автоматически!")                     # Добавляем сообщение об успешном создании
            context['form'] = ProfileForm(instance=profile)                                         # Добавляем форму профиля в контекст
            context['user_posts'] = Post.objects.filter(author=self.request.user)                   # Добавляем посты пользователя
            context['telegram_token'] = TelegramConnector(self.request.user)              # Генерируем токен для Telegram
            context['TELEGRAM_BOT_USERNAME'] = getattr(settings, 'TELEGRAM_BOT_USERNAME', None)     # Получаем имя бота из настроек
            context['following'] = profile.following.all()                                          # Добавляем подписки, если есть M2M поле
        return context                                                                              # Возвращаем обновлённый контекст

class UniqueSlugGenerator:
    """Класс для генерации уникальных slug'ов для моделей Django."""

    def __init__(self, model_instance: Model, slug_field: str, source_field: str):              # Инициализация класса с аргументами и анатациями типов,
        """
        Инициализация генератора slug'ов.
        
        Args:
            model_instance: Экземпляр модели Django.
            slug_field: Название поля, в котором будет храниться slug.
            source_field: Название поля, из которого генерируется slug.
        """
        self.model_instance = model_instance
        self.slug_field = slug_field
        self.source_field = source_field
        self.model_class = model_instance.__class__
    
    def generate(self) -> None:
        """
        Генерирует уникальный slug и устанавливает его в указанное поле модели.
        Если slug уже существует, добавляет числовой суффикс.
        """
        if not getattr(self.model_instance, self.slug_field):
            base_slug = slugify(getattr(self.model_instance, self.slug_field), allow_unicode=True)
            slug = base_slug
            counter = 1
            while self.model_class.objects.filter(**{self.slug_field: slug}).exclude(pk=self.model_instance.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            setattr(self.model_instance, self.slug_field, slug)


# === Формируем сообщение для телеграма ===
def render_telegram_new_post_message(post,site_url):
    """
    Рендерит сообщение для Telegram из HTML-шаблона.
    Возвращает строку с HTML.
    """
    # Генерируем строку HTML для Telegram, используя шаблон 'vibemusic/telegram/new_post.html' и передавая в него контекст: сам пост (post) и базовый URL сайта без завершающего слеша (site_url.rstrip('/')), результат возвращаем как строку
    return render_to_string(                            
        'vibemusic/telegram/new_post.html',
        {
            'post': post,                               # Объект поста с данными (title, text и др.)
            'site_url': site_url.rstrip('/')            # Убираем завершающий слеш у URL сайта
        }
    ).strip()                                            # Убираем пробелы и переносы в начале и конце строки


# ДОПОЛНИТЕЛЬНО: Фото поста
def render_telegram_new_post_message(post, site_url):
    if post.images.exists():
        template = 'vibemusic/telegram/new_post_with_photo.html'
        context = {
            'post': post,
            'site_url': site_url.rstrip('/'),
            'photo_url': f"{site_url}{post.images.first().image.url}"
        }
    else:
        template = 'vibemusic/telegram/new_post.html'
        context = {'post': post, 'site_url': site_url.rstrip('/')}

    return render_to_string(template, context).strip()



# функцию для извлечения метаданных(работа со Spotyfi)
# ------------------------------------------------------------------------------------------------------------------------------
def extract_metadata(audio_file):
    """
    Извлечение метаданных из аудиофайла (MP3, FLAC, OGG).
    Поддерживает работу с путями к файлам или объектами UploadedFile в Django.
    """
    try:
        audio = MP3(audio_file, ID3=ID3)
        title = audio.get('TIT2', [''])[0]
        artist = audio.get('TPE1', [''])[0]
        album = audio.get('TALB', [''])[0]
        return {
            'title': title,
            'artist': artist,
            'album': album
        }
    except Exception as e:
        print(f"Ошибка при извлечении метаданных: {e}")
        return {'title': '', 'artist': '', 'album': ''}






