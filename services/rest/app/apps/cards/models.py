from django.db import models
from django.db.models import IntegerField, OrderBy
from django.db.models.fields.json import KeyTextTransform
from django.db.models.functions import Cast

from apps.core.models import Color, Faction


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

    def __str__(self) -> str:
        return f"{self.pk} - {self.name}"


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

    def __str__(self) -> str:
        return f"{self.pk} - {self.name}"


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

    def __str__(self) -> str:
        return f"{self.pk} - {self.name}"


class Leader(models.Model):
    class Meta:
        managed = False
        db_table = "leaders"
        verbose_name = "Карта лидера"
        verbose_name_plural = "Карты лидеров"
        ordering = (
            "faction",
            OrderBy(Cast(KeyTextTransform("damage", "data"), IntegerField()), descending=True),
        )

    name = models.CharField(
        verbose_name="Имя карты (название)",
        max_length=32,
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
    unlocked = models.BooleanField(
        verbose_name="Открыта ли карта по умолчанию",
        default=True,
    )
    faction = models.ForeignKey(
        Faction,
        related_name="leaders",
        on_delete=models.PROTECT,
        null=False,
    )
    ability = models.ForeignKey(
        Ability,
        related_name="leaders",
        on_delete=models.PROTECT,
        null=False,
    )
    passive_ability = models.ForeignKey(
        PassiveAbility,
        related_name="leaders",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        default=None,
    )
    data = models.JSONField(
        default=dict,
        blank=False,
        null=False,
        verbose_name="Данные лидера",
    )

    def __str__(self) -> str:
        return f"{self.name}, ability {self.ability}"


class Card(models.Model):
    class Meta:
        managed = False
        db_table = "cards"
        verbose_name = "Карта"
        verbose_name_plural = "Карты"
        ordering = (
            "-color",
            OrderBy(Cast(KeyTextTransform("damage", "data"), IntegerField()), descending=True),
            OrderBy(Cast(KeyTextTransform("hp", "data"), IntegerField()), descending=True),
            OrderBy(Cast(KeyTextTransform("charges", "data"), IntegerField()), descending=True),
        )

    name = models.CharField(
        verbose_name="Имя карты (название)",
        max_length=32,
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
    unlocked = models.BooleanField(
        verbose_name="Открыта ли карта по умолчанию",
        default=True,
    )
    faction = models.ForeignKey(
        Faction,
        related_name="cards",
        on_delete=models.PROTECT,
        null=False,
    )
    color = models.ForeignKey(
        Color,
        related_name="cards",
        on_delete=models.PROTECT,
    )
    type = models.ForeignKey(
        Type,
        related_name="cards",
        on_delete=models.PROTECT,
    )
    ability = models.ForeignKey(
        Ability,
        related_name="cards",
        on_delete=models.PROTECT,
        null=False,
    )
    passive_ability = models.ForeignKey(
        PassiveAbility,
        related_name="cards",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        default=None,
    )
    newly_added = models.BooleanField(
        verbose_name="Добавлена ли карта недавно (для фильтров)",
        default=False,
    )
    data = models.JSONField(
        default=dict,
        blank=False,
        null=False,
        verbose_name="Данные карты",
    )

    def __str__(self) -> str:
        return f"{self.pk} {self.name}, ability {self.ability}"


class Deck(models.Model):
    class Meta:
        managed = False
        db_table = "decks"
        verbose_name = "Колода"
        verbose_name_plural = "Колоды"

    name = models.CharField(
        max_length=255,
        blank=False,
        null=False,
    )
    cards = models.ManyToManyField(
        Card,
        related_name="cards",
        through="CardDeck",
    )
    leader = models.ForeignKey(
        "Leader",
        related_name="decks",
        on_delete=models.CASCADE,
        blank=False,
        null=False,
    )

    def __str__(self) -> str:
        return f"{self.pk}, name {self.name}, {self.leader}"


class CardDeck(models.Model):
    class Meta:
        managed = False
        db_table = "card_decks"
        verbose_name = "Карта в колоде"
        verbose_name_plural = "Карты в колоде"

    card = models.ForeignKey(
        "Card",
        related_name="d",
        on_delete=models.CASCADE,
        null=False,
        blank=False,
    )
    deck = models.ForeignKey(
        "Deck",
        related_name="d",
        on_delete=models.CASCADE,
        null=False,
        blank=False,
    )
