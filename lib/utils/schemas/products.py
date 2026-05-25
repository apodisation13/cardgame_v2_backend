from lib.utils.schemas.base import StrEnumChoices


class ProductType(StrEnumChoices):
    RESOURCE = "resource"
    AVATAR = "avatar"


class PurchaseStatus(StrEnumChoices):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"


class PaymentNotificationPaymentStatus(StrEnumChoices):
    PAYED = "payed"
    PROCESSED = "processed"
    ERROR = "error"

    REJECTED = "rejected"
    CREATED = "created"
    CREATED_ERROR = "created_error"
    REFUNDED = "refunded"

    @classmethod
    def processable_states(cls) -> set:
        return set(cls)

    @classmethod
    def success_states(cls) -> set:
        return {
            cls.PAYED,
            cls.PROCESSED,
        }
