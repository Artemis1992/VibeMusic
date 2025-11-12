# from __future__ import annotations
from typing import Tuple
from django.contrib.auth.models import AbstractBaseUser
from django.core.cache import cache                     # Кэш Django: даёт get/set ключей (Redis/Memcached/локальный бэкенд) для хранения флагов и TTL ограничений
from django.utils import timezone
from django.conf import settings                        # Доступ к конфигурации Django (настройки проекта: TIME_ZONE, кэш/БД, наши IP_CHANGE_* константы и т.п.)
from datetime import timedelta
from ..models import IPChangeLog                        # Импортируем модель логов IP-адресов из родительского пакета (на уровень выше текущего модуля)


def user_has_active_restriction(user: AbstractBaseUser) -> tuple[bool, int]:
    """
    Проверяем: "Может ли пользователь сейчас загружать файлы?"
    Если — "Нет",  возвращает, сколько секунд осталось до разблокировки.
    - ключ в кэше для флага ограничения загрузки:
        срабатывает при превышении лимита по МБ; по нему читаем TTL (оставшееся время блокировки).
    - cache.get(key) - берём значение из кэша по ключу key.
    - если ключ истёк, возвращаем (False, 0).
    """
    key = f"upload_restricton_user_{user.pk}"                   # Уникальный ключь                            
    val = cache.get(key)                                                        
    if val is None:                                                                
        return False, 0
    # Узнаём оставшийся TTL ключа (в секундах), если бэкенд кэша поддерживает метод .ttl; иначе используем заглушку, которая возвращает 0
    ttl = getattr(cache, "ttl", lambda _k: 0)(key)
    return True, max(int(ttl or 0), 0)                      # ttl or 0 → если ttl равен None/0/пустому значению — подставляем 0; int(...) → приводим к целому числу; max(..., 0) → не даём уйти в отрицательные значения


def check_id_changes_and_maybe_restrict(
        user: AbstractBaseUser,
        current_ip: str | None,
) -> tuple[bool, int]:
    """
    Проверить изменения IP-адреса и, возможно, ограничить.
    """
    restricted, ttl = user_has_active_restriction((user))       # Узнаём, есть ли уже активное ограничение для этого пользователя и сколько секунд осталось (ttl)
    if restricted:                                              # Если ограничение уже действует -
        return True, ttl                                        # сразу выходим и возвращаем (True, оставшиеся_секунды)
    
    window_hours: int = int(getattr(settings, "IP_CHANGE_WINDOW_HOURS", 1))                 # Размер «окна» в часах для подсчёта уникальных IP; берём из настроек, по умолчанию 1 час
    threshold: int = int(getattr(settings, "IP_CHANGE_THRESHOLD", 3))                       # Порог уникальных IP в окне: если их >= threshold, включаем ограничение (по умолчанию 3)
    restriction_seconds: int = int(getattr(settings, "IP_CHANGE_RESTRICTION_SECONDS", 5 * 3600))    # Длительность ограничения в секундах; берём из настроек, по умолчанию 5 часов (18000 сек)

    
    """
    Вычисляем now - этот промежуток.
    Если сейчас 21:30, то при window_hours=1 получится 20:30.
    """
    since = timezone.now() - timedelta(hours=window_hours)          # Метка начала окна: текущее (tz-aware) время минус window_hours часов; всё, что новее since, попадает в расчёт
 

    unique_ips_qs = (
        IPChangeLog.objects                             # берём таблицу логов IP-адресов
        .filter(user=user, timestamp__gte=since)        # фильтруем по текущему пользователю и по дате: только записи новее/равные since (началу окна)
        .values_list("ip", flat=True)                   # Берём только значения поля "ip" как плоский список (без кортежей flat=True), например ['1.2.3.4', '5.6.7.8', ...]
        .distinct()                                     # Убираем дубликаты IP в результирующем queryset/списке — оставляем только уникальные значения
    )

    if current_ip and current_ip not in set(unique_ips_qs): # Если current_ip существует И его ещё нет в списке уникальных IP — тогда...
        unique_count += 1

    if unique_count >= threshold:                           # Если уникальных IP больше установленного порога:
        key = f"upload_restriction_user_{user.pk}"       
        cache.set(key, True, timeout=restriction_seconds)   # Поставить блокировку пользователю: ключ = True, на restriction_seconds секунд. Через это время - блокировка автоматически снимется
        return True, restriction_seconds                    # Возвращаем кортеж: True - ограничение активно, restriction_seconds - длительность блокировки в секундах
    return False, 0                                         # Ограничение не активно; 0 - нет оставшегося времени блокировки