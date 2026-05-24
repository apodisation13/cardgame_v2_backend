from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
import smtplib

from lib.utils.clients.base import BaseClient
from lib.utils.config.base import BaseConfig


logger = logging.getLogger(__name__)


class EmailClient(BaseClient):
    """Клиент для отправки email сообщений"""

    def __init__(self, config: BaseConfig):
        super().__init__(config)

    async def send(self, to: str, message: str, subject: str | None = None) -> bool:
        try:
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
