from pathlib import Path                    # объектно-ориентированная работа с путями (files/dirs)
import os                                   # утилиты ОС: переменные окружения, пути, cwd, список файлов
from datetime import timedelta              # интервалы времени (часы/дни), для таймаутов/TTL/расписаний


BASE_DIR = Path(__file__).resolve().parent.parent.parent    # корень проекта (поднимаемся на 3 уровня вверх)

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "unisafe-secret")
DEBUG = os.getenv("DJANGO_DEBUG", "False").lower() == "true"


ALLOWED_HOSTS = [h.strip() for h in os.getenv("DJANGO_ALLOWED_HOSTS", "").split(",") if h.strip()]

# Application definition

INSTALLED_APPS = [
    # Django core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # 3rd-party
    "rest_framework",              # DRF
    "rest_framework.authtoken",    
    "rest_framework_simplejwt",    # JWT-аутентификация
    "drf_yasg",                    # Swagger/OpenAPI
    "corsheaders",                 # CORS

    # Local apps
    'vibemusic.apps.VibemusicConfig',
    'vibemusic.api.v1.apps.ApiV1Config',                                # ← API v1
]



MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",        # базовая безопасность
    "whitenoise.middleware.WhiteNoiseMiddleware",           # раздача статики (prod)
    "corsheaders.middleware.CorsMiddleware",                # CORS: должен идти до CommonMiddleware
    "django.contrib.sessions.middleware.SessionMiddleware", # сессии (нужны дальше)
    "django.middleware.common.CommonMiddleware",            # общие заголовки/перенаправления
    "django.middleware.csrf.CsrfViewMiddleware",            # CSRF-защита форм
    "django.contrib.auth.middleware.AuthenticationMiddleware", # аутентификация пользователя
    "django.contrib.messages.middleware.MessageMiddleware", # флеш-сообщения
    "django.middleware.clickjacking.XFrameOptionsMiddleware", # защита от clickjacking
]

ROOT_URLCONF = 'coolsite.urls'                              # модуль с urlpatterns проекта
WSGI_APPLICATION = 'coolsite.wsgi.application'              # WSGI-точка входа (gunicorn/uwsgi)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",                 # драйвер БД: PostgreSQL
        "NAME": os.getenv("POSTGRES_DB", "vibemusic"),             # имя базы
        "USER": os.getenv("POSTGRES_USER", "vibemusic"),           # пользователь
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", ""),            # пароль (в проде обязателен!)
        "HOST": os.getenv("POSTGRES_HOST", "localhost"),           # хост БД
        "PORT": os.getenv("POSTGRES_PORT", "5432"),                # порт
        "CONN_MAX_AGE": 60,                                        # кэширование соединений (секунды)
        "OPTIONS": {"connect_timeout": 5},                         # таймаут подключения (секунды)
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},   # запрет похожих на имя/почту паролей
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 8}},  # мин. длина
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},            # бан частых паролей (123456 и т.п.)
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},           # запрет чисто цифровых паролей
]

LANGUAGE_CODE = "ru-ru"
TIME_ZONA = "Asia/Tashkent"
USE_I18N = True             # включить международализацию (переводы, локали)
USE_TZ = True               # хранить время в UTC и конвертировать по TIME_ZONE
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'vibemusic/static']
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# WhiteNoise: сжатие и хэшированные имена
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


# DRF: пагинация, фильтры, троттлинг
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (  # аутентификация по умолчанию
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (      # права по умолчанию
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",  # пагинация страницами
    "PAGE_SIZE": 20,                     # размер страницы

    "DEFAULT_THROTTLE_CLASSES": [        # лимиты запросов (throttling)
        "rest_framework.throttling.AnonRateThrottle",  # для анонимов
        "rest_framework.throttling.UserRateThrottle",  # для авторизованных
    ],
    "DEFAULT_THROTTLE_RATES": {          # скорости: N/час
        "anon": "100/hour",
        "user": "1000/hour",
    },

    "DEFAULT_FILTER_BACKENDS": [         # бэкенды фильтрации/поиска/сортировки
        "rest_framework.filters.OrderingFilter",
        "rest_framework.filters.SearchFilter",
        # "django_filters.rest_framework.DjangoFilterBackend",  # ← добавь при установке django-filter
    ],
}


# JWT сроки жизни из .env
ACCESS_MIN = int(os.getenv("ACCESS_TOKEN_LIFETIME_MIN", "60"))   # минуты для access-токена
REFRESH_DAYS = int(os.getenv("REFRESH_TOKEN_LIFETIME_DAYS", "7"))# дни для refresh-токена
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=ACCESS_MIN),      # срок жизни access
    "REFRESH_TOKEN_LIFETIME": timedelta(days=REFRESH_DAYS),      # срок жизни refresh
    # "ROTATE_REFRESH_TOKENS": True,                              # опц. выдавать новый refresh при обновлении
    # "BLACKLIST_AFTER_ROTATION": True,                           # опц. старый refresh в чёрный список (нужен app blacklist)
}


# CORS
CORS_ALLOWED_ORIGINS = [o.strip() for o in os.getenv("CORS_ALLOWED_ORIGINS", "").split(",") if o.strip()]   # берём из .env строку доменов через запятую - чистим пробелы - оставляем непустые


# Ограничение загрузок
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "300"))   # лимит размера загрузки в МБ (берём из .env, по умолчанию 300)
# Переводим МБ → байты (1 МБ = 1024 * 1024 байт)
MAX_UPLOAD_BYTES = MAX_UPLOAD_MB
# Ограничиваем, сколько Django держит в памяти при загрузке
DATA_UPLOAD_MAX_MEMORY_SIZE = MAX_UPLOAD_MB                 # для форм (POST, JSON + файлы)
FILE_UPLOAD_MAX_MEMORY_SIZE = MAX_UPLOAD_MB                 # только для файлов













