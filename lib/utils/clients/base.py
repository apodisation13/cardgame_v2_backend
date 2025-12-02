from abc import ABC, abstractmethod
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
import smtplib

from lib.utils.config.base import BaseConfig
import requests


logger = logging.getLogger(__name__)


class BaseClient(ABC):
    """Базовый класс для клиентов отправки сообщений"""

    def __init__(self, config: BaseConfig):
        self.config = config

    @abstractmethod
    async def send(self, to: str, message: str, subject: str | None = None) -> bool:
        """Отправка сообщения"""


class EmailClient(BaseClient):
    """Клиент для отправки email сообщений"""

    def __init__(self, config: BaseConfig):
        super().__init__(config)

    async def send(self, to: str, message: str, subject: str | None = None) -> bool:
        """Асинхронная отправка email"""
        try:
            # Создание сообщения
            msg = MIMEMultipart()
            msg["From"] = self.config.EMAIL_USER
            msg["To"] = to
            msg["Subject"] = subject or "Уведомление"
            msg.attach(MIMEText(message, "plain"))

            with smtplib.SMTP_SSL(self.config.SMTP_SERVER, self.config.SMTP_PORT) as server:
                server.login(self.config.EMAIL_USER, self.config.EMAIL_PASSWORD)
                server.send_message(msg)

            logger.info("Email отправлен на %s", to)
            return True

        except Exception as e:
            logger.error("Ошибка отправки email: %s", e)
            return False


class SmsClient(BaseClient):
    """Клиент для отправки SMS сообщений"""

    def __init__(self, config: BaseConfig):
        super().__init__(config)

    async def send(self, to: str, message: str, subject: str | None = None) -> bool:
        """Отправка SMS через email2sms"""
        try:
            # Формируем email адрес для SMS
            sms_email = f"{self.config.SMS_TOKEN}+{to}@sms.ru"

            # mts_email = f"{to}@sms.mts.ru"

            print(555555555555555555555555, sms_email)

            # Создаем сообщение
            msg = MIMEMultipart()
            msg["From"] = self.config.EMAIL_USER
            msg["To"] = sms_email
            msg["Subject"] = "SMS"  # Тема не важна для SMS

            # Текст сообщения - это и будет SMS
            msg.attach(MIMEText(message, "plain"))

            with smtplib.SMTP_SSL(self.config.SMTP_SERVER, self.config.SMTP_PORT) as server:
                server.login(self.config.EMAIL_USER, self.config.EMAIL_PASSWORD)
                server.send_message(msg)

            logger.info("SMS отправлено на %s через email2sms", to)
            return True

        except Exception as e:
            logger.error("Ошибка отправки SMS: %s", e)
            return False


class TelegramClient(BaseClient):
    """Клиент для отправки сообщений в Telegram"""

    def __init__(self, config: BaseConfig):
        super().__init__(config)

    async def send(self, to: str, message: str, subject: str | None = None) -> bool:
        """Отправка сообщения в Telegram"""
        try:
            # Формирование URL для API Telegram
            url = f"https://api.telegram.org/bot{self.config.TG_TOKEN}/sendMessage"

            # Параметры запроса
            payload = {
                "chat_id": to,  # ID чата или пользователя
                "text": message,
                "parse_mode": "HTML",
            }

            # Отправка запроса
            response = requests.post(url, data=payload, timeout=30)
            result = response.json()

            if result.get("ok"):
                logger.info("Сообщение отправлено в Telegram chat_id: %s", to)
                return True
            else:
                logger.error("Ошибка Telegram API: %s", result.get("description"))
                return False

        except Exception as e:
            logger.error("Ошибка отправки в Telegram: %s", e)
            return False
