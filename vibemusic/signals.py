# signals.py
from django.db.models.signals import post_save           # Импортируем сигнал, который срабатывает после сохранения объекта модели
from django.dispatch import receiver                       # Декоратор для подписки функции на сигнал
from django.contrib.auth.models import User               # Встроенная модель пользователя Django
from .models import Profile, Post                         # Импортируем свои модели Profile и Post
from django.conf import settings                           # Доступ к настройкам проекта (например, SITE_URL)
from .core_utils import render_telegram_new_post_message  # Функции для отправки сообщений в Telegram
import threading                                           # Для создания отдельного потока, чтобы не блокировать сервер
from vibemusic.utils.telegram import (
    send_telegram_message,
)
import logging

logger = logging.getLogger(__name__)                     # Настраиваем логгер для этого модуля


# === 1. Автосоздание профиля ===
@receiver(post_save, sender=User)                        # Подписываем функцию на сигнал post_save модели User
def create_user_profile(sender, instance, created, **kwargs):
    """Автоматически создаёт Profile при создании нового User."""
    if created:
        Profile.objects.create(user=instance)           # Создаём профиль, если пользователь только что создан
        logger.info(f"Profile создан автоматически для пользователя {instance.username}")  # Логируем создание профиля


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Сохраняет изменения в Profile при обновлении User (опционально)."""
    try:
        instance.profile.save()                          # Пытаемся сохранить связанный профиль
    except Profile.DoesNotExist:
        # Если Profile не существует (редко), создаём
        Profile.objects.create(user=instance)           # Создаём профиль, если его не было
        logger.info(f"Profile создан при обновлении для {instance.username}")  # Логируем создание профиля при обновлении


# === 2. Уведомление о новом посте в Telegram-группу ===
@receiver(post_save, sender=Post)
def notify_new_post_to_telegram(sender, instance, created, **kwargs):
    """Отправляет уведомление в Telegram-группу при создании нового поста."""
    if not created:
        return  # Выходим, если пост обновляется, а не создаётся
    
    # Формируем текст сообщения для Telegram, используя объект нового поста (instance) и базовый URL сайта (settings.SITE_URL), чтобы в сообщении была информация о заголовке, ссылке на пост и других данных, и чтобы сообщение сразу можно было отправлять в Telegram
    message = render_telegram_new_post_message(instance, settings.SITE_URL)  

    def send():
        if send_telegram_message(settings.TELEGRAM_GROUP_CHAT_ID, message):  # Отправляем сообщение в Telegram
            logger.info(f"Уведомление о посте '{instance.title}' отправлено")  # Логируем успешную отправку
        else:
            logger.error(f"Не удалось отправить уведомление о '{instance.title}'")  # Логируем ошибку отправки
        
    threading.Thread(target=send, daemon=True).start()  # Запускаем отправку в отдельном потоке, чтобы не блокировать сервер
