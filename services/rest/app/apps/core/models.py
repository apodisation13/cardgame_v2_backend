from django.db import models


class Faction(models.Model):
    """Модель фракции - пока Neutral, Soldiers, Animals, Monsters"""
    class Meta:
        managed = False
        db_table = "factions"
        verbose_name = "Фракция карты"
        verbose_name_plural = "Фракции карт"

    name = models.CharField(
        verbose_name="Название фракции",
        max_length=32,
        blank=False,
        null=False,
        unique=True,
    )

    def __str__(self) -> str:
        return f'{self.pk} - {self.name}'


class Color(models.Model):
    """Модель цвета карты - Bronze, Silver, Gold"""
    class Meta:
        managed = False
        db_table = "colors"
        verbose_name = "Цвет карты"
        verbose_name_plural = "Цвета карт"

    name = models.CharField(
        verbose_name="Название цвета",
        max_length=32,
        blank=False,
        null=False,
        unique=True,
    )

    def __str__(self) -> str:
        return f'{self.pk} - {self.name}'


class GameConstants(models.Model):
    """Различные игровые данные"""
    class Meta:
        managed = False
        db_table = "game_constants"
        verbose_name = "Различные данные игры"
        verbose_name_plural = "Различные данные игры"

    data = models.JSONField(
        verbose_name="Данные с игровыми константами",
        default=dict,
    )

    def __str__(self) -> str:
        return str(self.pk)
