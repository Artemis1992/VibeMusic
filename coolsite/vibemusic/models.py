# models.py
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify                                   # только маленькие буквы, цифры, дефисы и без пробелов
from vibemusic.core_utils import extract_metadata, UniqueSlugGenerator
from vibemusic.spotify_utils import search_track, download_image
import logging


logger = logging.getLogger(__name__)


class Activity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    message = models.TextField()  # Сообщение, например, "Вы подписались на пользователя X"
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Активность"
        verbose_name_plural = "Активности"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}: {self.message}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name="Пользователь")                    # Пользователь, связанный с профилем
    photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True, verbose_name="Фото профиля")                          # Фото профиля пользователя
    telegram_username = models.CharField(max_length=150, blank=True, null=True, verbose_name="Имя пользователя Telegram (с @)")         # Имя пользователя Telegram
    telegram_chat_id = models.BigIntegerField(blank=True, null=True, db_index=True, verbose_name="Идентификатор чата Telegram (ID)")    # ID чата Telegram                                                      
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Номер телефона")                                # Номер телефона пользователя
    following = models.ManyToManyField('self', symmetrical=False, related_name='followers', blank=True, verbose_name="Подписки")        # Пользователи, на которых подписан профиль

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

    def __str__(self):
        return f"Профиль пользователя{self.user.username}"


class SiteSettings(models.Model):
    header_image = models.ImageField(upload_to='site_settings/', blank=True, null=True, verbose_name="Изображение шапки")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Настройка сайта"
        verbose_name_plural = "Настройки сайта"

    def __str__(self):
        return "Настройки сайта"

    @classmethod
    def get_solo(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название жанра")
    slug = models.SlugField(max_length=255, unique=True, db_index=True, blank=True, verbose_name="URL")
    icon = models.ImageField(upload_to='genre_icons/', blank=True, null=True, verbose_name="Иконка жанра")
    background_image = models.ImageField(upload_to='genre_backgrounds/', blank=True, null=True, verbose_name="Фоновое изображение")
    description = models.TextField(blank=True, verbose_name="Описание жанра")
    related_genres = models.ManyToManyField('self', blank=True, symmetrical=False, verbose_name="Связанные жанры")

    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"
        ordering = ['name']               # Сортировка по алфавиту

    def save(self, *args, **kwargs):
        UniqueSlugGenerator(self, 'slug', 'name').generate()    # Генерируем slug на основе поля name
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Artist(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name="Имя исполнителя")
    slug = models.SlugField(max_length=255, unique=True, db_index=True, blank=True, verbose_name="URL")
    bio = models.TextField(max_length=7000, blank=True, verbose_name="Биография")
    photo = models.ImageField(upload_to='artist_photos/', blank=True, null=True, verbose_name="Фото исполнителя")
    genres = models.ManyToManyField(Genre, related_name='artists', verbose_name="Жанры")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    liked_by = models.ManyToManyField(User, through='Reaction', related_name='liked_artists', blank=True)
    
    class Meta:
        verbose_name = "Исполнитель"
        verbose_name_plural = "Исполнители"
        ordering = ['name']

    def save(self, *args, **kwargs):
        UniqueSlugGenerator(self, 'slug', 'name').generate()  # Генерируем slug на основе поля name
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.name


class PostImage(models.Model):
    image = models.ImageField(upload_to='post_images/', verbose_name="Фотография")
    caption = models.CharField(max_length=200, blank=True, verbose_name="Подпись к фото")
    # Поле, автоматически сохраняющее дату и время создания объекта (загрузки), 
    # с возможностью задания значения по умолчанию (на случай ручного создания)
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Дата загрузки")

    class Meta:
        verbose_name = "Фотография поста"
        verbose_name_plural = "Фотографии постов"

    def __str__(self):
        return self.caption or f"Фото {self.id}"


class Track(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название трека")
    artist = models.ForeignKey(Artist, on_delete=models.SET_NULL, null=True, verbose_name="Исполнитель")
    audio_file = models.FileField(upload_to='tracks/', verbose_name="Аудиофайл")
    album_name = models.CharField(max_length=200, blank=True, verbose_name="Название альбома")
    album_image = models.ImageField(upload_to='images/', null=True, blank=True, verbose_name="Изображение альбома")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    liked_by = models.ManyToManyField(User, through='Reaction', related_name='liked_tracks', blank=True)

    class Meta:
        verbose_name = "Трек"
        verbose_name_plural = "Треки"
        ordering = ['-created_at']

    def save(self, *args, **kwargs):                                                    # Переопределяет метод save модели для кастомной логики перед сохранением
                                                                                        # Извлечение метаданных из аудиофайла
        if self.audio_file and not self.album_image:                                    # Проверяет наличие аудиофайла и отсутствие обложки альбома
            logger.debug(f"Извлечение метаданных для трека: {self.title}")                                    
            metadata = extract_metadata(self.audio_file)                                # Извлекает метаданные из аудиофайла с помощью функции extract_metadata
            self.title = self.title or metadata.get('title', '')                                # С помощью (get() безопасно) Обновляем название трека метаданными, если поле пустое
            self.album_name = self.album_name or metadata.get('album', '')                      # Обновляет название альбома метаданными, если поле пустое
            if metadata.get('artist') and not self.artist:                                  # Проверяет наличие исполнителя в метаданных и отсутствие в модели
                artist_name = metadata['artist']
                artist, created = Artist.objects.get_or_create(                               # Получает или создаёт объект Artist по имени
                    name=artist_name,                                            # Устанавливает имя исполнителя из метаданных
                    defaults={'slug': slugify(artist_name, allow_unicode=True)}  # Генерирует slug по умолчанию с поддержкой unicode
                )                                                                       # Завершает get_or_create
                self.artist = artist                                                    # Присваивает объект Artist полю модели
                logger.debug(f"Автоматически создан/найден исполнитель: {artist.name}")
            
                                                                                        # Поиск обложек в Spotify
            # Поиск обложки в Spotify
            if metadata.get('title') and metadata.get('artist'):                                    # Проверяет наличие названия трека и имени исполнителя в метаданных
                logger.debug(f"Поиск в Spotify: {metadata['title']} - {metadata['artist']}") # Логирует попытку поиска трека в Spotify по названию и исполнителю
                try:                                                                        # Пытается выполнить запрос к Spotify API
                    spotify_data = search_track(metadata['title'], metadata['artist'])      # Ищет трек в Spotify по метаданным
                    if spotify_data and spotify_data.get('album_image_url'):                    # Если найдено и есть URL обложки альбома
                        filename = f"{slugify(self.artist.slug) if self.artist else 'unknown'}_{slugify(self.title)}.jpg" # Формирует имя файла для сохранения обложки
                        image_path = download_image(spotify_data['album_image_url'], filename) # Скачивает изображение по ссылке
                        if image_path:                                                      # Если скачивание прошло успешно
                            self.album_image = image_path                                   # Сохраняет путь к обложке в модель
                            self.album_name = self.album_name or spotify_data.get('album_name', '') # Устанавливает название альбома, если поле пустое
                            logger.debug(f"Обложка из Spotify сохранена: {image_path}")                # Логирует успешное сохранение обложки
                        else:                                                               # Если не удалось скачать изображение
                            self.album_image = getattr(settings, 'DEFAULT_ALBUM_IMAGE', None)           # Получает дефолтное изображение альбома из настроек, если не указано, присваивает None
                            logger.warning(f"Трек не найден в Spotify, используется дефолт: {self.album_image}") # Логирует предупреждение
                    else:                                                                   # Если трек не найден или нет обложки
                        self.album_image = getattr(settings, 'DEFAULT_ALBUM_IMAGE', None)                     # Устанавливает дефолтную обложку
                        logger.warning(f"Трек не найден в Spotify, используется дефолт: {self.album_image}") # Логирует предупреждение
                except Exception as e:                                                      # Обрабатывает любые ошибки при работе с API
                    logger.error(f"Ошибка при поиске в Spotify: {e}")                       # Логирует ошибку с описанием
                    self.album_image = getattr(settings, 'DEFAULT_ALBUM_IMAGE', None)                         # Устанавливает дефолтную обложку
                    

            super().save(*args, **kwargs)                                                    # Вызывает оригинальный метод save для сохранения объекта
                    

    def __str__(self):
        return f"{self.title} - {self.artist.name if self.artist else 'Unknown'}"


class Post(models.Model):
    artist = models.ForeignKey(Artist, on_delete=models.SET_NULL, null=True, blank=True, related_name="posts", verbose_name="Исполнитель")  # Связь с исполнителем. Если исполнитель удалён — поле становится NULL (запись поста сохраняется)
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор")                                                        # Связь с пользователем (автором поста). Если пользователь удалён — удаляются и все его посты 
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts', verbose_name="Жанр")           # Связь с жанром. Если жанр удалён — поле станет NULL (пост сохранится без жанра).
    title = models.CharField(max_length=200, verbose_name="Заголовок поста")                                                                # Связь с заголовком и ограничением 200 символов
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")                                                 # Связь со слагом, Обязательно должно быть уникальное имя и ограничение 255 символов, индексируем для удобного поиска.
    content = models.TextField(verbose_name="Содержимое поста")                                                                             # Связь с Контентом без ограничение на символы.
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")                                                      # Cохраняет дату/время, когда объект был создан. auto_now_add=True Устанавливается один раз автоматически.
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")                                                        # Обнавляем дату/время, когда обьект был перезаписан. auto_now=True Позволяет обновлять при каждом изменение
    images = models.ManyToManyField(PostImage, blank=True, related_name='posts', verbose_name="Фотографии")                                 # Связи многие-ко-многим
    tracks = models.ManyToManyField(Track, blank=True, related_name='related_posts', verbose_name="Треки")
    liked_by = models.ManyToManyField(User, through='Reaction', related_name='liked_posts', blank=True)

    class Meta:
        verbose_name = "Пост"
        verbose_name_plural = "Посты"
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        UniqueSlugGenerator(self, 'slug', 'title').generate()  # Генерируем slug на основе поля title
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - ({self.artist.name if self.artist else 'No Artist'})"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments", verbose_name="Пост")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор")
    content = models.TextField(verbose_name="Текст комментария")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies', verbose_name="Родительский комментарий")
    image = models.ImageField(upload_to='comment_images/', blank=True, null=True, verbose_name="Изображение")
    liked_by = models.ManyToManyField(User, through='Reaction', related_name='liked_comments', blank=True)

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ['created_at']

    def __str__(self):
        return f"Комментарий от {self.user.username} к {self.post.title}"


class Reaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reactions')
    track = models.ForeignKey(Track, on_delete=models.CASCADE, null=True, blank=True, related_name='track_reactions')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True, related_name='comment_reactions')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True, related_name='post_reactions')
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, null=True, blank=True, related_name='artist_reactions')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['user', 'track'], ['user', 'comment'], ['user', 'post'], ['user', 'artist']]
        verbose_name = "Реакция"
        verbose_name_plural = "Реакции"

    def __str__(self):
        if self.track:
            return f"{self.user.username} liked track {self.track.title}"
        elif self.comment:
            return f"{self.user.username} liked comment {self.comment.id}"
        elif self.post:
            return f"{self.user.username} liked post {self.post.title}"
        elif self.artist:
            return f"{self.user.username} liked artist {self.artist.name}"
        return f"{self.user.username} reaction"
    

class IPChangeLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ip = models.CharField(max_length=45)                                            # IPv4 или IPv6
    timestamp = models.DateTimeField(auto_now_add=True)
    bytes_uploaded = models.BigIntegerField(default=0)                              # можно пополнять если нужно учитывать байты

    class Meta:
        indexes = [
            models.Index(fields=["user", "timestamp"]),
            models.Index(fields=["id", "timestamp"]),
        ]

    def __str__(self):
        return f"({self.user_id} @ {self.ip} at {self.timestamp.isoformat()})"