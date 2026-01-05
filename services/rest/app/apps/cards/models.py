from django.db import models


class Type(models.Model):
    """Тип карты - Unit, Special"""
    class Meta:
        managed = False
        db_table = "types"
        verbose_name = "Тип карты"
        verbose_name_plural = "Типы карт"

    name = models.CharField(
        verbose_name="Название типа",
        max_length=32,
        blank=False,
        null=False,
        unique=True,
    )

    def __str__(self):
        return f'{self.pk} - {self.name}'


class Ability(models.Model):
    """Способность карты"""
    class Meta:
        managed = False
        db_table = "abilities"
        verbose_name = "Способность карты"
        verbose_name_plural = "Способности карт"

    name = models.CharField(
        verbose_name="Название способности",
        max_length=64,
        blank=False,
        null=False,
        unique=True,
    )
    description = models.TextField(
        verbose_name="Описание способности",
        blank=False,
        null=False,
    )

    def __str__(self):
        return f'{self.pk} - {self.name}'


class PassiveAbility(models.Model):
    """Пассивные способности карт и лидеров"""
    class Meta:
        managed = False
        db_table = "passive_abilities"
        verbose_name = "Пассивная способность карты"
        verbose_name_plural = "Пассивные способности карт"

    name = models.CharField(
        verbose_name="Название пассивной способности",
        max_length=64,
        blank=False,
        null=False,
        unique=True,
    )
    description = models.TextField(
        verbose_name="Описание пассивной способности",
        blank=False,
        null=False,
    )

    def __str__(self):
        return f'{self.pk} - {self.name}'
