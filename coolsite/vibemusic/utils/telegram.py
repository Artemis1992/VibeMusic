# vibemusic/utils/telegram.py
from __future__ import annotations

import logging
from functools import lru_cache
from typing import Optional, Union, TYPE_CHECKING

import requests
from django.conf import settings  # берём токен из Django settings
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired

if TYPE_CHECKING:
    # Только для подсказок типов, без реального импорта модели на старте
    from ..models import User  # noqa: F401


class TelegramConnector:
    """
    Делает:
      - токен привязки по user.pk (с подписью и TTL),
      - верификацию токена → user_pk,
      - отправку сообщений в Telegram.
    """

    def __init__(
        self,
        bot_token: str,
        token_ttl_seconds: int = 60 * 60 * 24 * 7,  # 7 дней
        signer: Optional[TimestampSigner] = None,
        session: Optional[requests.Session] = None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self.bot_token = bot_token
        self.token_ttl_seconds = token_ttl_seconds
        self.signer = signer or TimestampSigner()
        self.session = session or requests.Session()
        self.logger = logger or logging.getLogger("telegram.connector")

    # ---------- Токены привязки (user.pk) ----------

    def make_connect_token(self, user_or_pk: Union[int, "User"]) -> str:
        """
        Сгенерировать подписанный токен по user.pk.
        """
        user_pk = getattr(user_or_pk, "pk", user_or_pk)
        raw = str(int(user_pk))
        signed = self.signer.sign(raw)
        return signed

    def parse_connect_token(self, token: str) -> Optional[int]:
        """
        Проверить подпись и TTL токена. Вернуть user_pk или None.
        """
        try:
            raw = self.signer.unsign(token, max_age=self.token_ttl_seconds)
            return int(raw)
        except SignatureExpired as e:
            self.logger.warning("Токен просрочен: %s", e)
            return None
        except BadSignature as e:
            self.logger.error("Недействительный токен: %s", e)
            return None
        except Exception as e:
            self.logger.exception("Ошибка при разборе токена: %s", e)
            return None

    # ---------- Отправка сообщения ----------

    def send_message(
        self,
        chat_id: Union[int, str],
        text: str,
        parse_mode: str = "Markdown",
        disable_web_page_preview: bool = True,
        timeout: int = 10,
    ) -> bool:
        """
        Отправить сообщение в Telegram. Вернёт True/False.
        """
        if not chat_id:
            self.logger.warning("Не указан chat_id для Telegram сообщения.")
            return False

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": disable_web_page_preview,
        }

        try:
            resp = self.session.post(url, json=payload, timeout=timeout)
            resp.raise_for_status()
            self.logger.info("Сообщение отправлено: chat_id=%s", chat_id)
            return True
        except requests.RequestException as e:
            self.logger.error("Ошибка отправки в Telegram: %s", e)
            return False

    # ---------- Фабрика из settings ----------

    @classmethod
    def from_settings(
        cls,
        *,
        token_ttl_seconds: int = 60 * 60 * 24 * 7,
        logger: Optional[logging.Logger] = None,
    ) -> "TelegramConnector":
        """
        Создать коннектор, подтянув токен из Django settings (TELEGRAM_BOT_TOKEN).
        """
        return cls(
            bot_token=settings.TELEGRAM_BOT_TOKEN,
            token_ttl_seconds=token_ttl_seconds,
            logger=logger,
        )


# ---------- Ленивый синглтон-коннектор и функции-обёртки (совместимость) ----------

@lru_cache(maxsize=1)
def _default_connector() -> TelegramConnector:
    return TelegramConnector.from_settings()


def make_telegram_connect_token(user_or_pk: Union[int, "User"]) -> str:
    """
    Совместимая обёртка для старого импорта.
    """
    return _default_connector().make_connect_token(user_or_pk)


def unsign_telegram_connect_token(token: str) -> Optional[int]:
    """
    Совместимая обёртка для старого импорта.
    """
    return _default_connector().parse_connect_token(token)


def send_telegram_message(
    chat_id: Union[int, str],
    text: str,
    parse_mode: str = "Markdown",
    disable_web_page_preview: bool = True,
    timeout: int = 10,
) -> bool:
    """
    Совместимая обёртка для старого импорта.
    """
    return _default_connector().send_message(
        chat_id=chat_id,
        text=text,
        parse_mode=parse_mode,
        disable_web_page_preview=disable_web_page_preview,
        timeout=timeout,
    )


__all__ = [
    # Класс
    "TelegramConnector",
    # Функции-обёртки (для существующего кода)
    "make_telegram_connect_token",
    "unsign_telegram_connect_token",
    "send_telegram_message",
]
