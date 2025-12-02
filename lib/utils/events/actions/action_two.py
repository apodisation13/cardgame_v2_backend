from typing import Any

from lib.utils.events.actions.base import ActionBase
from lib.utils.events.uuu import render_template


class SendEmailAction(ActionBase):
    async def execute(self, context: dict[str, Any]) -> bool:
        receiver_template = self.config["receiver"]
        receiver = render_template(receiver_template, context)

        # Логика отправки email
        print(f"Sending email to {receiver}")
        return True
