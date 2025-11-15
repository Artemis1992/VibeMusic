# utils/ip.py           
from typing import Optional                             # Аннотация: функция вернёт str или None (если IP определить нельзя)
from ipaddress import ip_address                        # Это валидатор IP-адресов - проверяет, что строка - правильный IPv4 или IPv6.
from django.http import HttpRequest                     # Тип запроса Django содержит META с сырыми заголовками/переменными WSGI.

def get_client_ip(request: HttpRequest) -> Optional[str]:
    """
    Извлечь IP клиента:
    - если есть X-Forwarded-For → берём первый IP (как правило, исходный клиент),
      валидируем; иначе
    - REMOTE_ADDR (то, что видит сервер напрямую).
    Внимание: доверять XFF стоит только за доверенным прокси.
    """
    xff = request.META.get("HTTP_X_FORWARDED_FOR")           # Сырое значение заголовка X-Forwarded-For от прокси/балансировщика; вернёт строку с цепочкой IP через запятую (например "1.2.3.4, 10.0.0.1") или None, если заголовка нет.
    if xff:
        return xff.split(",")[0].strip()                    # Берём первый IP слева (исходный клиент) и убираем пробелы; без доп. проверки и доверенных прокси это поле может быть подделано.
    return request.META.get("REMOTE_ADDR")                  # Фоллбек IP который видит сервер напрямую (часто адрес ближайшего прокси). Вернёт строку или None, если ключа нет.
