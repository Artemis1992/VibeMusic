# vibemusic/signals.py
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile


logger = logging.getLogger(__name__)

@receiver(post_save, sender=User)                                       # Подписываем функцию на сигнал post_save модели User: будет вызвана после сохранения User (создание или обновление)
def create_user_profile(sender, instance, created, **kwargs):
    """Автоматически создаёт Profile при создании нового User."""
    if created:
        Profile.objects.create(user=instance)
        logger.info(f"Profile создан автоматически для пользователя {instance.username}")

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Сохраняет изменения в Profile при обновлении User (опционально)."""
    try:
        instance.profile.save()
    except Profile.DoesNotExist:
        # Если Profile не существует (редко), создаём
        Profile.objects.create(user=instance)
        logger.info(f"Profile создан при обновлении для {instance.username}")

