from django.db import models

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
    image_tablet = models.ImageField(
        upload_to="leaders/",
        blank=False,
        null=False,
    )
    image_phone = models.ImageField(
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
    damage = models.IntegerField(
        verbose_name="Урон, который наносит карта врага (damage)",
        default=0,
        blank=False,
        null=False,
    )
    hp = models.IntegerField(
        verbose_name="Жизни карты врага (hp)",
        default=0,
        blank=False,
        null=False,
    )
    base_hp = models.IntegerField(
        verbose_name="Дефолтные жизни карты врага (hp)",
        default=0,
        blank=False,
        null=False,
    )
    shield = models.BooleanField(
        verbose_name="щит, есть или нет",
        default=False,
    )
    has_passive = models.BooleanField(
        verbose_name="Есть ли у карты врага пассивная способность (has_passive)",
        default=False,
    )
    has_passive_in_field = models.BooleanField(
        verbose_name="Есть ли у карты врага пассивная способность, которая срабатывает на поле (has_passive_in_field)",
        default=False,
    )
    has_passive_in_deck = models.BooleanField(
        verbose_name="Есть ли у карты врага пассивная способность, которая срабатывает в колоде (has_passive_in_deck)",
        default=False,
    )
    has_passive_in_grave = models.BooleanField(
        verbose_name="Есть ли у карты врага пассивная способность, которая срабатывает в сбросе (has_passive_in_grave)",
        default=False,
    )
    passive_ability = models.ForeignKey(
        EnemyPassiveAbility,
        related_name="enemies",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        default=None,
    )
    value = models.IntegerField(
        verbose_name="Значение для пассивной способности карты врага (value)",
        default=0,
        blank=False,
        null=False,
    )
    timer = models.IntegerField(
        verbose_name="Текущее значение таймера пассивной способности врага (timer)",
        default=0,
        blank=False,
        null=False,
    )
    default_timer = models.IntegerField(
        verbose_name="Дефолтное значение таймера пассивной способности врага (default_timer)",
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
    has_deathwish = models.BooleanField(
        verbose_name="Есть ли завещание у врага (способность после его уничтожения)",
        default=False,
    )
    deathwish = models.ForeignKey(
        Deathwish,
        related_name="enemies",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        default=None,
    )
    deathwish_value = models.IntegerField(
        verbose_name="Значение для завещания врага (deathwish_value)",
        default=0,
        blank=False,
        null=False,
    )

    def __str__(self) -> str:
        return (
            f"{self.pk}:{self.name}, {self.faction}, {self.color}, "
            f"damage {self.damage}, hp {self.hp}, move {self.move.name}, shield {self.shield}"
        )


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
    image_tablet = models.ImageField(
        upload_to="leaders/",
        blank=False,
        null=False,
    )
    image_phone = models.ImageField(
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
    hp = models.IntegerField(
        verbose_name="Жизни карты лидера врагов (hp)",
        default=0,
        blank=False,
        null=False,
    )
    base_hp = models.IntegerField(
        verbose_name="Дефолтные жизни карты лидера врагов (hp)",
        default=0,
        blank=False,
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
    has_passive = models.BooleanField(
        verbose_name="Есть ли у карты врага пассивная способность (has_passive)",
        default=False,
    )
    passive_ability = models.ForeignKey(
        EnemyPassiveAbility,
        related_name="enemy_leaders",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    value = models.IntegerField(
        verbose_name="Значение для пассивной способности карты лидера врага (value)",
        default=0,
        blank=False,
        null=False,
    )
    timer = models.IntegerField(
        verbose_name="Текущее значение таймера пассивной способности лидера врагов (timer)",
        default=0,
        blank=False,
        null=False,
    )
    default_timer = models.IntegerField(
        verbose_name="Дефолтное значение таймера пассивной способности лидера врагов (default_timer)",
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
        return (
            f"{self.pk} - {self.name}, hp {self.hp}, passive {self.has_passive}, "
            f"абилка - {self.ability}, пассивка - {self.passive_ability}"
        )
