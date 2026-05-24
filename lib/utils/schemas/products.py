from lib.utils.schemas.base import StrEnumChoices


class ProductType(StrEnumChoices):
    RESOURCE = "resource"
    AVATAR = "avatar"


class PurchaseStatus(StrEnumChoices):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"


class PaymentNotificationPaymentStatus(StrEnumChoices):
    PAYED = "PAYED"
    REJECTED = "REJECTED"

    @classmethod
    def processable_states(cls) -> set:
        return {
            cls.PAYED,
            cls.REJECTED,
        }
