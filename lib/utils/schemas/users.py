from lib.utils.schemas.base import StrEnumChoices


class UserRole(StrEnumChoices):
    PLAYER = "player"
    DEVELOPER = "developer"
