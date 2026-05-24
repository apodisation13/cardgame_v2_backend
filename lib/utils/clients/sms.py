from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
import smtplib

from lib.utils.clients.base import BaseClient
from lib.utils.config.base import BaseConfig


logger = logging.getLogger(__name__)


class SmsClient(BaseClient):
    """Клиент для отправки SMS сообщений"""

    def __init__(self, config: BaseConfig):
        super().__init__(config)

    async def send(self, to: str, message: str, subject: str | None = None) -> bool:
        try:
            sms_email = f"{self.config.SMS_TOKEN}+{to}@sms.ru"

            msg = MIMEMultipart()
            msg["From"] = self.config.EMAIL_USER
            msg["To"] = sms_email
            msg["Subject"] = "SMS"
            msg.attach(MIMEText(message, "plain"))

            with smtplib.SMTP_SSL(self.config.SMTP_SERVER, self.config.SMTP_PORT) as server:
                server.login(self.config.EMAIL_USER, self.config.EMAIL_PASSWORD)
                server.send_message(msg)

            logger.info("SMS отправлено на %s через email2sms", to)
            return True

        except Exception as e:
            logger.error("Ошибка отправки SMS: %s", e)
            return False
