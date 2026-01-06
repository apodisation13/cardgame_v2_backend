from django.db import models

from apps.core.models import Faction, Color


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

    def __str__(self) -> str:
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

    def __str__(self) -> str:
        return f'{self.pk} - {self.name}'


class Leader(models.Model):
    class Meta:
        managed = False
        db_table = "leaders"
        verbose_name = "Карта лидера"
        verbose_name_plural = "Карты лидеров"
        ordering = (
            "faction",
            "-damage",
        )

    name = models.CharField(
        verbose_name="Имя карты (название)",
        max_length=32,
        blank=False,
        null=False,
        unique=True,
    )
    # TODO: работа с картинками!!!
    image = models.ImageField(
        upload_to='leaders/',
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
        related_name='leaders',
        on_delete=models.PROTECT,
        null=False,
    )
    damage = models.IntegerField(
        verbose_name="Урон, который наносит карта лидера (damage)",
        default=0,
        blank=False,
        null=False,
    )
    charges = models.IntegerField(
        verbose_name="Количество зарядов карты лидера (charges)",
        default=1,
        blank=False,
        null=False,
    )
    heal = models.IntegerField(
        verbose_name="На сколько карта лидера лечит (heal)",
        default=0,
        blank=False,
        null=False,
    )
    has_passive = models.BooleanField(
        verbose_name="Есть ли у карты лидера пассивная способность (has_passive)",
        default=False,
    )
    passive_ability = models.ForeignKey(
        PassiveAbility,
        related_name='leaders',
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        default=None,
    )
    value = models.IntegerField(
        verbose_name="Значение для пассивной способности (value)",
        default=0,
        blank=False,
        null=False,
    )
    timer = models.IntegerField(
        verbose_name="Текущее значение таймера пассивной способности (timer)",
        default=0,
        blank=False,
        null=False,
    )
    default_timer = models.IntegerField(
        verbose_name="Дефолтное значение таймера пассивной способности (default_timer)",
        default=0,
        blank=False,
        null=False,
    )
    reset_timer = models.BooleanField(
        verbose_name="Нужно ли сбрасывать таймер на дефолтный после его истечения (reset_timer)",
        default=False,
    )

    def __str__(self) -> str:
        return f'{self.name}, ability {self.ability}, damage {self.damage} charges {self.charges}'


class Card(models.Model):
    class Meta:
        managed = False
        db_table = "cards"
        verbose_name = "Карта"
        verbose_name_plural = "Карты"
        ordering = (
            "-color",
            "-damage",
            "-hp",
            "-charges",
        )

    name = models.CharField(
        verbose_name="Имя карты (название)",
        max_length=32,
        blank=False,
        null=False,
        unique=True,
    )
    # TODO: работа с картинками!!!
    image = models.ImageField(
        upload_to='cards/',
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
        related_name='cards',
        on_delete=models.PROTECT,
    )
    type = models.ForeignKey(
        Type,
        related_name='cards',
        on_delete=models.PROTECT,
    )
    ability = models.ForeignKey(
        Ability,
        related_name='cards',
        on_delete=models.PROTECT,
        null=False,
    )
    damage = models.IntegerField(
        verbose_name="Урон, который наносит карта (damage)",
        default=0,
        blank=False,
        null=False,
    )
    charges = models.IntegerField(
        verbose_name="Количество зарядов карты (charges)",
        default=1,
        blank=False,
        null=False,
    )
    hp = models.IntegerField(
        verbose_name="Жизни карты (hp)",
        default=0,
        blank=False,
        null=False,
    )
    heal = models.IntegerField(
        verbose_name="На сколько карта лечит (heal)",
        default=0,
        blank=False,
        null=False,
    )
    has_passive = models.BooleanField(
        verbose_name="Есть ли у карты пассивная способность (has_passive)",
        default=False,
    )
    has_passive_in_hand = models.BooleanField(
        verbose_name="Есть ли у карты пассивная способность, которая срабатывает в руке (has_passive_in_hand)",
        default=False,
    )
    has_passive_in_deck = models.BooleanField(
        verbose_name="Есть ли у карты пассивная способность, которая срабатывает в колоде (has_passive_in_deck)",
        default=False,
    )
    has_passive_in_grave = models.BooleanField(
        verbose_name="Есть ли у карты пассивная способность, которая срабатывает в сбросе (has_passive_in_grave)",
        default=False,
    )
    passive_ability = models.ForeignKey(
        PassiveAbility,
        related_name='cards',
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        default=None,
    )
    value = models.IntegerField(
        verbose_name="Значение для пассивной способности (value)",
        default=0,
        blank=False,
        null=False,
    )
    timer = models.IntegerField(
        verbose_name="Текущее значение таймера пассивной способности (timer)",
        default=0,
        blank=False,
        null=False,
    )
    default_timer = models.IntegerField(
        verbose_name="Дефолтное значение таймера пассивной способности (default_timer)",
        default=0,
        blank=False,
        null=False,
    )
    reset_timer = models.BooleanField(
        verbose_name="Нужно ли сбрасывать таймер на дефолтный после его истечения (reset_timer)",
        default=False,
    )
    each_tick = models.BooleanField(
        verbose_name="Cрабатывает ли пассивка каждый ход таймера (True) или только когда таймер 0 (False)",
        default=False,
    )

    def __str__(self) -> str:
        return f'{self.pk} {self.name}, hp {self.hp}, ' \
               f'ability {self.ability}, damage {self.damage}, heal {self.heal} '

    # @classmethod
    # def from_db(cls, db, field_names, values):
    #     instance = super().from_db(db, field_names, values)
    #     # здесь мы запоминаем значения, которые были
    #     instance._loaded_values = dict(zip(field_names, values))
    #     return instance
    #
    # def save(self, *args, **kwargs):
    #     # если мы ИЗМЕНЯЕМ карту и мы изменили её ЖИЗНИ, то пересчитываем жизни всех колод с этой картой!
    #     if not self._state.adding and (self.hp - self._loaded_values['hp']):
    #         change_decks_health(card_id=self.id, diff=self.hp - self._loaded_values['hp'])
    #     super().save(*args, **kwargs)
