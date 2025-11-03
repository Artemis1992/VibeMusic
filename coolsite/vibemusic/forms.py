# forms.py

from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django import forms
from .models import Comment, Track, Profile, PostImage, Post  # Добавляем Post для формы создания постов

# Импорты для crispy-forms (для красивого рендеринга форм с Bootstrap 5)
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field





# Кастомная форма регистрации
class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)  # Поле email обязательно

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True  # Разрешаем множественный выбор файлов


    class Meta:
        model = User  # Используем встроенную модель User
        fields = ['username', 'email', 'password1', 'password2']  # Поля формы регистрации

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # Вызываем родительский конструктор
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',  # Класс Bootstrap для стиля
            'placeholder': 'Логин',  # Плейсхолдер для поля
        })
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',  # Класс Bootstrap для стиля
            'placeholder': 'Email',  # Плейсхолдер для поля
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',  # Класс Bootstrap для стиля
            'placeholder': 'Пароль',  # Плейсхолдер для поля
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',  # Класс Bootstrap для стиля
            'placeholder': 'Подтвердите пароль',  # Плейсхолдер для поля
        })

    def save(self, commit=True):
        user = super().save(commit=False)  # Создаём пользователя без сохранения
        if commit:
            user.save()  # Сохраняем пользователя
        return user  # Возвращаем пользователя

    def clean_email(self):
        email = self.cleaned_data.get('email')  # Получаем очищенный email
        if User.objects.filter(email=email).exists():  # Проверяем, существует ли email
            raise forms.ValidationError('Этот email уже зарегистрирован.')  # Выбрасываем ошибку валидации
        return email  # Возвращаем email, если он уникален
    

# Форма входа
class LoginViewForm(AuthenticationForm):
    username = forms.CharField(
        label='Логин',  # Метка поля
        widget=forms.TextInput(attrs={
            'class': 'form-control',  # Класс Bootstrap для стиля
            'placeholder': 'Логин',  # Плейсхолдер для поля
        })
    )
    password = forms.CharField(
        label='Пароль',  # Метка поля
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',  # Класс Bootstrap для стиля
            'placeholder': 'Пароль',  # Плейсхолдер для поля
            'autocomplete': 'off',  # Отключаем автозаполнение
        })
    )

    class Meta:
        fields = ['username', 'password']  # Поля формы входа

# Форма для редактирования профиля
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile  # Используем модель Profile
        fields = ['photo', 'phone_number', 'telegram_username']  # Поля формы профиля

        widgets = {
            'photo': forms.FileInput(attrs={
                'class': 'form-control',  # Класс Bootstrap для стиля
                'accept': 'image/*',  # Разрешаем только изображения
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',  # Класс Bootstrap для стиля
                'placeholder': '+79991234567',  # Плейсхолдер для номера телефона
            }),
            'telegram_username': forms.TextInput(attrs={
                'class': 'form-control',  # Класс Bootstrap для стиля
                'placeholder': '@yourusername',  # Плейсхолдер для Telegram-username
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # Вызываем родительский конструктор
        self.helper = FormHelper()  # Настраиваем crispy-forms для Bootstrap 5
        self.helper.form_method = 'post'  # Метод отправки формы
        self.helper.add_input(Submit('submit', 'Сохранить профиль', css_class='btn btn-primary'))  # Кнопка отправки

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')  # Получаем очищенный номер телефона
        if phone:
            # Простая валидация номера телефона (можно улучшить с помощью библиотеки phonenumbers)
            if not phone.startswith('+7') and not phone.startswith('8'):  # Проверяем формат российского номера
                raise forms.ValidationError('Номер телефона должен начинаться с +7 или 8.')  # Выбрасываем ошибку
        return phone  # Возвращаем номер, если валиден

    def clean_telegram_username(self):
        username = self.cleaned_data.get('telegram_username')  # Получаем очищенный username Telegram
        if username and not username.startswith('@'):  # Проверяем, начинается ли с @
            raise forms.ValidationError('Имя пользователя Telegram должно начинаться с @.')  # Выбрасываем ошибку
        return username  # Возвращаем username, если валиден



# Форма для создания поста
class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True  # Разрешаем множественный выбор файлов



class PostForm(forms.ModelForm):
    images = forms.FileField(
        widget=MultipleFileInput(attrs={
            'class': 'form-control',  # Класс Bootstrap для стиля
            'accept': 'image/*',  # Разрешаем только изображения
        }),
        required=False,  # Поле не обязательно
        label='Изображения'  # Метка поля
    )
    tracks = forms.FileField(
        widget=MultipleFileInput(attrs={
            'class': 'form-control',  # Класс Bootstrap для стиля
            'accept': 'audio/*',  # Разрешаем только аудио
        }),
        required=False,  # Поле не обязательно
        label='Треки'  # Метка поля
    )

    class Meta:
        model = Post  # Используем модель Post
        fields = ['title', 'content', 'artist', 'genre', 'images', 'tracks']  # Поля формы (исключаем author и slug)
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',  # Класс Bootstrap для стиля
                'placeholder': 'Название поста',  # Плейсхолдер для заголовка
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',  # Класс Bootstrap для стиля
                'rows': 5,  # Количество строк
                'placeholder': 'Содержимое поста',  # Плейсхолдер для содержимого
            }),
            'artist': forms.Select(attrs={
                'class': 'form-control',  # Класс Bootstrap для стиля
            }),
            'genre': forms.Select(attrs={
                'class': 'form-control',  # Класс Bootstrap для стиля
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # Вызываем родительский конструктор
        self.helper = FormHelper()  # Настраиваем crispy-forms для Bootstrap 5
        self.helper.form_method = 'post'  # Метод отправки формы
        self.helper.form_enctype = 'multipart/form-data'  # Для загрузки файлов
        self.helper.add_input(Submit('submit', 'Создать пост', css_class='btn btn-primary'))  # Кнопка отправки

    def clean_images(self):
        images = self.files.getlist('images')  # Получаем список загруженных изображений
        if images:
            if len(images) > 5:  # Ограничиваем количество изображений
                raise forms.ValidationError('Можно загрузить не более 5 изображений.')  # Выбрасываем ошибку
            for image in images:
                if not image.content_type.startswith('image/'):
                    raise forms.ValidationError('Все файлы должны быть изображениями.')  # Проверяем тип файла
        return images  # Возвращаем список изображений

    def clean_tracks(self):
        tracks = self.files.getlist('tracks')  # Получаем список загруженных треков
        if tracks:
            if len(tracks) > 3:  # Ограничиваем количество треков
                raise forms.ValidationError('Можно загрузить не более 3 треков.')  # Выбрасываем ошибку
            for track in tracks:
                if not track.content_type.startswith('audio/'):
                    raise forms.ValidationError('Все файлы должны быть аудиофайлами.')  # Проверяем тип файла
        return tracks  # Возвращаем список треков

    def save(self, commit=True):
        post = super().save(commit=False)  # Создаём пост без сохранения в БД
        if commit:
            post.save()  # Сохраняем пост
            # Обработка изображений
            images = self.files.getlist('images')  # Получаем список изображений
            for image in images:
                image_instance = PostImage.objects.create(image=image)  # Создаём объект PostImage
                post.images.add(image_instance)  # Добавляем к посту
            # Обработка треков
            tracks = self.files.getlist('tracks')  # Получаем список треков
            for track in tracks:
                track_instance = Track.objects.create(
                    file=track,
                    user=self.instance.author,  # Устанавливаем автора
                    title=track.name  # Используем имя файла как заголовок (можно улучшить)
                )  # Создаём объект Track
                post.tracks.add(track_instance)  # Добавляем к посту
            self.save_m2m()  # Сохраняем ManyToMany связи (artist, genre)
        return post  # Возвращаем пост



# Форма для комментариев
class CommentForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Ваш комментарий (поддерживаются смайлики)',
            'id': 'comment-content'
        }),
        strip=False,
        required=False
    )

    class Meta:
        model = Comment
        fields = ['content', 'image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Отправить комментарий', css_class='btn btn-primary'))

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image and image.size > 5 * 1024 * 1024:
            raise forms.ValidationError('Размер изображения не должен превышать 5 МБ.')
        return image    


# Форма для загрузки трека
class TrackUploadForm(forms.ModelForm):
    class Meta:
        model = Track  # Используем модель Track
        fields = ['title', 'artist', 'audio_file', 'album_name']  # Поля формы трека

        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',  # Класс Bootstrap для стиля
                'placeholder': 'Название трека',  # Плейсхолдер для названия
            }),
            'artist': forms.Select(attrs={
                'class': 'form-control',  # Класс Bootstrap для стиля
            }),
            'audio_file': forms.FileInput(attrs={
                'class': 'form-control',  # Класс Bootstrap для стиля
                'accept': 'audio/*',  # Разрешаем только аудио
            }),
            'album_name': forms.TextInput(attrs={
                'class': 'form-control',  # Класс Bootstrap для стиля
                'placeholder': 'Название альбома',  # Плейсхолдер для альбома
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # Вызываем родительский конструктор
        self.helper = FormHelper()  # Настраиваем crispy-forms
        self.helper.form_method = 'post'  # Метод отправки формы
        self.helper.add_input(Submit('submit', 'Загрузить трек', css_class='btn btn-primary'))  # Кнопка отправки

    def clean_audio_file(self):
        audio_file = self.cleaned_data.get('audio_file')  # Получаем аудиофайл
        if audio_file:
            if audio_file.size > 10 * 1024 * 1024:  # Ограничиваем размер файла до 10 МБ
                raise forms.ValidationError('Размер аудиофайла не должен превышать 10 МБ.')  # Выбрасываем ошибку
            if not audio_file.name.lower().endswith(('.mp3', '.wav', '.ogg')):  # Проверяем расширение файла
                raise forms.ValidationError('Поддерживаются только MP3, WAV и OGG файлы.')  # Выбрасываем ошибку
        return audio_file  # Возвращаем аудиофайл