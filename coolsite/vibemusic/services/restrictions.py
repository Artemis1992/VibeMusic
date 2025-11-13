from __future__ import annotations

from typing import Tuple
from django.contrib.auth.models import AbstractBaseUser

# Берём реальную реализацию из utils
from ..utils.ip_restriction import user_has_active_restriction as _user_has_active_restriction


def user_has_active_restriction(user: AbstractBaseUser) -> tuple[bool, int]:
    """
    Обёртка над utils.user_has_active_restriction.

    Возвращает кортеж:
    - restricted: True, если для пользователя сейчас действует ограничение;
    - ttl: сколько секунд осталось до снятия ограничения (0, если нет ограничения).
    """
    return _user_has_active_restriction(user)