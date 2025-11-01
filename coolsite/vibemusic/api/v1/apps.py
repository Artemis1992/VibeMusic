# vibemusic/api/v1/apps.py
from django.apps import AppConfig


class ApiV1Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'vibemusic.api.v1'                               # ← точечный путь
    label = 'api_v1'                                        # ← короткое имя