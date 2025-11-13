# vibemusic/services.py  связь с views.py
from __future__ import annotations

from dataclasses import dataclass           # Импортирует декоратор @dataclass, который автоматически создаёт __init__, __repr__, __eq__ и т.д. для класса
from django.db import transaction           # Управление транзакциями БД (atomic, commit, rollback)

from .models import Profile, Activity       # Activity  Нужен нам для логирование


@dataclass
class FollowResult:
    action: str # "followed" | "unfollowed"
    followers_count: str

@transaction.atomic
def toggle_follow(user_profile: Profile, profile_to_follow: Profile) -> FollowResult:
    """
    Переключает состояние "подписан / не подписан" и создаёт Activity при подписке.
    Возвращает информацию для ответа во вьюхе.
    """
    if user_profile == profile_to_follow:                       # Если user_profile — это тот же объект, что и profile_to_follow
        raise ValueError("Нельзя подписаться на самого себя")
    
    if user_profile in profile_to_follow.followers.all():       # Если user_profile уже есть в списке подписчиков profile_to_follow
        # Отписка
        user_profile.following.remove(profile_to_follow)
        action = "unfollowed"
    else:
        # Подписка
        user_profile.following.add(profile_to_follow)
        action = "followed"

        Activity.objects.create(                            # Логируем подписку в журнал активности для сбора статистики подписок кто на кого
            user=user_profile.user,                         # Кто совершил действие
            target_user=profile_to_follow.user,             # На кого направлено
            activity_type="follow",                         # Тип активности: подписка "activity_type"
        )
    followers_count = profile_to_follow.followers.count()   # Подсчитываем, сколько пользователей подписано НА profile_to_follow
    return FollowResult(action=action, followers_count=followers_count) # возвращаем результат действия: что сделал + сколько теперь подписчиков