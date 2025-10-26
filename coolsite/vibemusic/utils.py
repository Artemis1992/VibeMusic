# utils.py
from django.db.models import *
from django.utils.text import slugify
from django.core.signing import TimestampSigner
from django.core.paginator import Paginator
from .models import *

from django.conf import settings
from django.contrib import messages

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
            context['telegram_token'] = make_telegram_connect_token(self.request.user)              # Генерируем токен для Telegram
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



# Функции для генерации/проверки токина и отправки сообщений 
# -----------------------------------------------------------------------------------------------------------------------------
def make_telegram_connect_token(user):
    """Генерирует signed token для привязки (содержит user.pk)."""
    return signer.sign(str(user.pk))                                        # Берем первичный ключь пользоателя, переводим в страку и генерируем криптографическую подпись защищая ее от подделки

def unsign_telegram_connect_token(token, max_age=60*60*24*7):               # 7 дней валидности
    """Проверяет и возвращает user.pk из token."""
    try:
        return signer.unsign(token, max_age=max_age)                        # Проверяем подлинность и "срок годности" токена, если все ОК то, Возвращаем исходный ID (или другие значение, которое было подписанно)
    except Exception as e:
        logger.error(f"Недействительный токен: {e}")
        return None

def send_telegram_message(chat_id, text, parse_mode='Markdown'):
    """Отпровляет сообщение в Telegram по chat_id."""
    if not chat_id:
        logger.warning("Для сообщения Telegram не указан chat_id.")         # Логируем предупреждение, если chat_id не указан
        return False
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"   # Формируем URL для API Telegram
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': parse_mode,
        'disable_web_page_preview': True,
    }
    try:
        response = requests.post(url, json=payload, timeout=10)             # Отправляем POST-запрос к API Telegram
        response.raise_for_status()                                         # Проверяем статус ответа
        logger.info(f"Сообщение Telegram отправлено на chat_id {chat_id}")  # Логируем успешную отправку
        return True
    except requests.RequestException as e:
        logger.error(f"Ошибка при отправке в Telegram: {e}")                # Логируем ошибку отправки
        return False

# ----------------------------------------------------------------------------------------------------------------------------



