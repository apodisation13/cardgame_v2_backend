from lib.utils.schemas.base import StrEnumChoices


class LevelDifficulty(StrEnumChoices):
    EASY = "easy"
    NORMAL = "normal"
    HARD = "hard"
