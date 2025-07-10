from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify


class UserProf(models.Model):
    pass

class SiteSettings(models.Model):
    header_image = models.ImageField(upload_to='site_settings/', blank=True, null=True, verbose_name="Изображение шапки")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Настроки сайта"
        verbose_name_plural = "Настроки сайта"
    
    def __str__(self):
        return "Настроки сайта"

# Модель для жанров музыки
class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название жанра")
    slug = models.SlugField(max_length=255, unique=True, db_index=True, blank=True, verbose_name="URL") # изменить после слаги в БД
    # Поле для выбора иконки из предопределённого списка.
    # Хранит имя файла иконки, по умолчанию (пустое значение-default.png).
    icon = models.ImageField(upload_to='genre_icons/', blank=True, null=True, verbose_name="Иконка жанра")
    background_image = models.ImageField(upload_to='genre_backgrounds/', blank=True, null=True, verbose_name="Фоновое изображение")
    description = models.TextField(blank=True, verbose_name="Описание жанра")                                                           # Не обязательное поле          
    related_genres = models.ManyToManyField('self', blank=True, symmetrical=False, verbose_name="Связанные жанры")                      # фозможность связать жанры между собой

    class Meta:
        # Настройки модели для админ-панели Django.
        verbose_name = "Жанр" # Название модели в единственном числе.
        verbose_name_plural = "Жанры" # Название модели во множественном числе.
    
    # Строковое представление объекта модели, возвращает название жанра.
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name, allow_unicode=True)
            self.slug = base_slug
            counter = 1
            while Genre.objects.filter(slug=self.slug).exclude(id=self.id).exists():
                self.slug = f"{base_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)  # Вызываем save до проверки уникальности


# Модели для исполнителя
class Artist(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name="Имя исполнителя")
    slug = models.SlugField(max_length=255, unique=True, db_index=True, blank=True, verbose_name="URL") # изменить после слаги в БД
    bio = models.TextField(max_length=7000, blank=True, verbose_name="Биография")
    photo = models.ImageField(upload_to='artist_photos/', blank=True, null=True, verbose_name="Фото исполнителя") # Поле для фото исполнителя, сохраняется в media/artist_photos/, может быть пустым
    genres = models.ManyToManyField(Genre, related_name='artists', verbose_name="Жанры")                          # Связь "многие ко многим" с моделью Genre, позволяет присваивать исполнителю несколько жанров
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")                            # Поле для даты создания записи, автоматически заполняется при создании

    class Meta:
        verbose_name = "Исполнитель"
        verbose_name_plural = "Исполнители"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    # Метод для строкового представления исполнителя (возвращает имя)
    def __str__(self):
        return self.name


# Модель для поста
class Post(models.Model):
    artist = models.ForeignKey(Artist, on_delete=models.SET_NULL, null=True, blank=True, related_name="posts", verbose_name="Исполнитель")
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts', verbose_name="Жанр")
    title = models.CharField(max_length=200, verbose_name="Заголовок поста")
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")
    content = models.TextField(verbose_name="Содержимое поста")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    images = models.ManyToManyField('PostImage', blank=True, related_name='posts', verbose_name="Фотографии")
    tracks = models.ManyToManyField('Track', blank=True, related_name='posts', verbose_name="Треки")


    class Meta:
        verbose_name = "Пост"
        verbose_name_plural = "Посты"
        ordering = ['-created_at'] # Сортируем от новых к старым

    def __str__(self):
        return f"{self.title} - ({self.artist.name})"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            # Убедимся, что slug уникален
            original_slug = self.slug
            counter = 1
            while Post.objects.filter(slug=self.slug).exclude(id=self.id).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)


# Модель для музыкального трека
class Track(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название трека")
    artist = models.ForeignKey(Artist, on_delete=models.SET_NULL, null=True, verbose_name="Исполнитель")
    audio_file = models.FileField(upload_to='tracks/', verbose_name="Аудиофайл")
    album_image = models.ImageField(upload_to='images/', null=True, blank=True, verbose_name="Изображение альбома")                          

    class Meta:
        verbose_name = "Трек"
        verbose_name_plural = "Треки"

    # Метод для строкового представления трека (названия и имя исполнителя)
    def __str__(self):
        return f"{self.title} - {self.artist.name}"
    


# Модель для фотографий в посте
class PostImage(models.Model):
    image = models.ImageField(upload_to='post_images/', verbose_name="Фотография")                                  # Поле для изображения, сохраняется в media/post_images/
    caption = models.CharField(max_length=200, blank=True, verbose_name="Подпись к фото")                           # Поле для подписи к фото, строка до 200 символов, может быть пустым

    class Meta:
        verbose_name = "Фотография поста"
        verbose_name_plural = "Фотография постов"

    def __str__(self):
        return self.caption or f"Фото {self.id}"                                                                    # Метод для строкового представления фотографии (подпись или ID)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments", verbose_name="Пост")          # Связь "один ко многим" с моделью Post, комментарий привязан к посту
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор")                                  # Связь "один ко многим" с моделью User, комментарий привязан к пользователю
    content = models.TextField(verbose_name="Текст комментария")                                                    # Произвольная длина
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")                               # Поле для даты создания комментария, автоматически заполняется
    # Связь с самим собой для поддержки вложенных комментариев (ответов), может быть пустым
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies', verbose_name="Родительский комментарий")
    
    class Meta:
        verbose_name= "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ['created_at']
    
    # Метод для строкового представления комментария (автор и пост)
    def __str__(self):
        return f"Комментарий от {self.user.username} к {self.post.title}"

















