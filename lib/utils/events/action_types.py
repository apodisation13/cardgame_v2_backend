from enum import StrEnum


class ActionType(StrEnum):
    ADD_RESOURCES = "ActionAddResources"
    UPDATE_PURCHASE_STATUS = "ActionUpdatePurchaseStatus"
    SEND_SERVICE_TG = "ActionSendServiceTg"
    SEND_SMS = "ActionSendSms"
