from enum import StrEnum


class ProductType(StrEnum):
    RESOURCE = 'resource'
    AVATAR = 'avatar'


class PurchaseStatus(StrEnum):
    PENDING = 'pending'
    SUCCESS = 'success'
    FAILED = 'failed'
