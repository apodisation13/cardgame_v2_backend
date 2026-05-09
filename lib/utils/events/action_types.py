from enum import StrEnum


class ActionType(StrEnum):
    ADD_RESOURCES = "ActionAddResources"
    SEND_SMS = "ActionSendSms"
    WEBHOOK = "ActionWebhook"
