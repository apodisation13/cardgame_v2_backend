from django.db import models

from apps.enemies.models import Enemy, EnemyLeader
from lib.utils.schemas.game import LevelDifficulty


LINE_CHOICES = (
    ("down", "down"),
    ("up", "up"),
    ("right", "right"),
    ("left", "left"),
    (None, None),
)


class Season(models.Model):
    class Meta:
        managed = False
        db_table = "seasons"
        verbose_name = "Сезон"
        verbose_name_plural = "Сезоны"

    name = models.CharField(
        verbose_name="Название сезона",
        max_length=255,
        blank=False,
        null=False,
    )
    description = models.TextField(
        verbose_name="Описание сезона",
        blank=False,
        null=False,
    )
    unlocked = models.BooleanField(
        verbose_name="Открыт ли сезон по умолчанию",
        default=False,
    )

    def __str__(self) -> str:
        return f"{self.name}, {self.description[:30]}"


class Level(models.Model):
    class Meta:
        managed = False
        db_table = "levels"
        verbose_name = "Уровень"
        verbose_name_plural = "Уровни"
        ordering = ("-pk",)

    name = models.CharField(
        verbose_name="Название уровня",
        max_length=255,
        blank=False,
        null=False,
        unique=True,
    )
    starting_enemies_number = models.IntegerField(
        verbose_name="Количество стартоваых врагов",
        default=3,
        blank=False,
        null=False,
    )
    difficulty = models.CharField(
        verbose_name="Сложность уровня",
        choices=LevelDifficulty.choices(),
        blank=False,
        null=False,
        max_length=20,
    )
    unlocked = models.BooleanField(
        verbose_name="Открыт ли уровень по умолчанию",
        default=False,
    )
    x = models.IntegerField(
        default=0,
        verbose_name="Координаты уровня по X в дереве на экране",
    )
    y = models.IntegerField(
        default=0,
        verbose_name="Координаты уровня по Y в дереве на экране",
    )

    season = models.ForeignKey(
        Season,
        on_delete=models.PROTECT,
        related_name="levels",
        blank=False,
        null=False,
    )
    enemy_leader = models.ForeignKey(
        EnemyLeader,
        related_name="levels",
        on_delete=models.PROTECT,
        blank=False,
        null=False,
    )

    enemies = models.ManyToManyField(
        Enemy,
        related_name="levels",
        through="LevelEnemy",
    )
    related_levels = models.ManyToManyField(
        "Level",
        through="LevelRelatedLevels",
        related_name="rel_levels",
    )

    def __str__(self) -> str:
        return (
            f"{self.pk}:{self.name}, появление: {self.starting_enemies_number}, "
            f"сложность {self.difficulty}, врагов {self.number_of_enemies()}, лидер {self.enemy_leader}"
        )

    def number_of_enemies(self) -> int:
        """для админки, чтобы показать это количество"""
        return len(self.l.all())

    def get_related_levels(self) -> list:
        """для админки, чтобы показать краткую информацию"""
        return [(level.id, level.name) for level in self.related_levels.all()]


class LevelRelatedLevels(models.Model):
    class Meta:
        managed = False
        db_table = "level_related_levels"
        verbose_name = "Уровень"
        verbose_name_plural = "Уровни"
        ordering = ("-pk",)
        unique_together = (
            "level",
            "related_level",
        )

    level = models.ForeignKey(
        Level,
        related_name="children",
        on_delete=models.PROTECT,
    )
    related_level = models.ForeignKey(
        Level,
        related_name="l2",
        on_delete=models.PROTECT,
    )
    line = models.CharField(
        verbose_name="Линия соединения в дереве",
        choices=LINE_CHOICES,
        blank=True,
        null=True,
        max_length=16,
    )
    connection = models.CharField(
        verbose_name="Связь в виде строки",
        help_text="Например: (1-5), сохраняется автоматически",
        max_length=16,
        blank=False,
        null=False,
    )

    def save(self, *args, **kwargs) -> None:
        self.connection = f"{self.level.id}-{self.related_level.id}"
        super().save(*args, **kwargs)


class LevelEnemy(models.Model):
    class Meta:
        managed = False
        db_table = "level_enemies"
        verbose_name = "Враг уровня"
        verbose_name_plural = "Враги уровня"

    level = models.ForeignKey(
        Level,
        related_name="l",
        on_delete=models.PROTECT,
    )
    enemy = models.ForeignKey(
        Enemy,
        related_name="l",
        on_delete=models.PROTECT,
    )
