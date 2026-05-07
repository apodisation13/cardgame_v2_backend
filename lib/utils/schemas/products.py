from lib.utils.schemas.base import StrEnumChoices


class ProductType(StrEnumChoices):
    RESOURCE = "resource"
    AVATAR = "avatar"


class PurchaseStatus(StrEnumChoices):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
