from django.db import models
from django.db.models import OrderBy, IntegerField
from django.db.models.fields.json import KeyTextTransform
from django.db.models.functions import Cast

from apps.core.models import Color, Faction


class Move(models.Model):
    """Способность врага ходить: down, stand, random, stand"""

    class Meta:
        managed = False
        db_table = "moves"
        verbose_name = "Тип хода врага"
        verbose_name_plural = "Типы ходов врагов"

    name = models.CharField(
        max_length=64,
        blank=False,
        null=False,
        unique=True,
    )
    description = models.TextField(
        verbose_name="Описание типа хода врагов",
        blank=False,
        null=False,
    )

    def __str__(self) -> str:
        return f"{self.pk} - {self.name}"


class EnemyPassiveAbility(models.Model):
    """Пассивная способность врагов"""

    class Meta:
        managed = False
        db_table = "enemy_passive_abilities"
        verbose_name = "Пассивная способность врага"
        verbose_name_plural = "Пассивные способности врагов"

    name = models.CharField(
        max_length=64,
        blank=False,
        null=False,
        unique=True,
    )
    description = models.TextField(
        verbose_name="Описание пассивной способности врагов",
        blank=False,
        null=False,
    )

    def __str__(self) -> str:
        return f"{self.pk} - {self.name}"


class EnemyLeaderAbility(models.Model):
    """Способности лидеров врагов"""

    class Meta:
        managed = False
        db_table = "enemy_leader_abilities"
        verbose_name = "Cпособность лидера врага"
        verbose_name_plural = "Cпособности лидеров врагов"

    name = models.CharField(
        max_length=64,
        blank=False,
        null=False,
        unique=True,
    )
    description = models.TextField(
        verbose_name="Описание способности лидера врагов",
        blank=False,
        null=False,
    )

    def __str__(self) -> str:
        return f"{self.pk} - {self.name}"


class Deathwish(models.Model):
    """Модель способности завещание у врага"""

    class Meta:
        managed = False
        db_table = "deathwishes"
        verbose_name = "Завещание врага"
        verbose_name_plural = "Завещания врагов"

    name = models.CharField(
        max_length=64,
        blank=False,
        null=False,
        unique=True,
    )
    description = models.TextField(
        verbose_name="Описание завещания врагов",
        blank=False,
        null=False,
    )

    def __str__(self) -> str:
        return f"{self.pk} - {self.name}"


class Enemy(models.Model):
    class Meta:
        managed = False
        db_table = "enemies"
        verbose_name = "Карта врага"
        verbose_name_plural = "Карты врагов"
        ordering = (
            "-faction",
            "color",
            OrderBy(Cast(KeyTextTransform("hp", "data"), IntegerField()), descending=True),
            OrderBy(Cast(KeyTextTransform("damage", "data"), IntegerField()), descending=True),
        )

    name = models.CharField(
        verbose_name="Имя карты врага (название)",
        max_length=64,
        blank=False,
        null=False,
        unique=True,
    )
    # TODO: работа с картинками!!!
    image_original = models.ImageField(
        upload_to="leaders/",
        blank=False,
        null=False,
    )
    faction = models.ForeignKey(
        Faction,
        related_name="enemies",
        on_delete=models.PROTECT,
        null=False,
    )
    color = models.ForeignKey(
        Color,
        related_name="enemies",
        on_delete=models.PROTECT,
    )
    move = models.ForeignKey(
        Move,
        related_name="enemies",
        on_delete=models.PROTECT,
    )
    passive_ability = models.ForeignKey(
        EnemyPassiveAbility,
        related_name="enemies",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        default=None,
    )
    deathwish = models.ForeignKey(
        Deathwish,
        related_name="enemies",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        default=None,
    )
    data = models.JSONField(
        default=dict,
        blank=False,
        null=False,
        verbose_name="Данные врага",
    )

    def __str__(self) -> str:
        return f"{self.pk}:{self.name}, {self.faction}, {self.color}, move {self.move.name}"


class EnemyLeader(models.Model):
    class Meta:
        managed = False
        db_table = "enemy_leaders"
        verbose_name = "Карта лидера врага"
        verbose_name_plural = "Карты лидеров врагов"

    name = models.CharField(
        verbose_name="Имя карты лидера врага (название)",
        max_length=64,
        blank=False,
        null=False,
        unique=True,
    )
    # TODO: работа с картинками!!!
    image_original = models.ImageField(
        upload_to="leaders/",
        blank=False,
        null=False,
    )
    faction = models.ForeignKey(
        Faction,
        related_name="enemy_leaders",
        on_delete=models.PROTECT,
        null=False,
    )
    ability = models.ForeignKey(
        EnemyLeaderAbility,
        related_name="enemy_leaders",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        default=None,
    )
    passive_ability = models.ForeignKey(
        EnemyPassiveAbility,
        related_name="enemy_leaders",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    data = models.JSONField(
        default=dict,
        blank=False,
        null=False,
        verbose_name="Данные лидера врага",
    )

    def __str__(self) -> str:
        return f"{self.pk} - {self.name}, абилка - {self.ability}, пассивка - {self.passive_ability}"
