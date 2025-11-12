from __future__ import annotations
from typing import Callable
from django.http import HttpRequest, HttpResponse
from django.conf import settings

from ..utils.ip import get_client_ip                # Импортируем утилиту извлечения IP клиента из соседнего пакета utils/ip.py
from ..models import IPChangeLog


class LogIPMiddleware:

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        """
        Инициализация миддлвара.

        Аргументы:
        get_response: следующий обработчик в цепочке middleware.

        Что делает:
        - Сохраняет ссылку на get_response.
        - Читает префикс для эндпоинтов загрузки из settings.UPLOAD_API_PREFIX
            (по умолчанию "/api/uploads") и кладёт в self.upload_prefix.
        - Этот префикс далее используется, чтобы применять логику только к путям загрузки.
        """
        self.get_response = get_response
        self.upload_prefix: str = getattr(settings, "UPLOAD_API_PREFIX", "/api/uploads")    

    def __call__(self, request: HttpRequest) -> HttpResponse:           # Принимаем HttpRequest от клиента а возврощаем HttpResponse
        user = getattr(request, "user", None)                           # Безопасно берём request.user; если атрибут отсутствует (например, отключён AuthenticationMiddleware) — получим None вместо исключения
        if (
            user and getattr(user, "is_authenticated", False)           # есть user и он аутентифицирован
            and request.method in ("POST", "PUT")                       # И метод запроса которые меняются (не логируем GET и т.п.)
            and request.path.startswith(self.upload_prefix)             # путь запроса начинается с префикса загрузок (фильтруем «нужные» эндпоинты)
        ):
            
            ip = get_client_ip(request)                                 # Определяем IP клиента из заголовков (X-Forwarded-For → первый IP) или REMOTE_ADDR; вернёт строку IP или None    
            if ip:
                # можно логировать «попытку»; финальный размер лучше писать во вью после успешной загрузки
                IPChangeLog.objects.create(user=user, ip=ip, bytes_uploaded=0)      # Создаём запись в логе: кто (пользователь), откуда (IP), сколько байт загрузил (0)

        response = self.get_response(request)                       # Передаём управление следующему обработчику (вьюха или следующий middleware) и получаем готовый HttpResponse
        return response