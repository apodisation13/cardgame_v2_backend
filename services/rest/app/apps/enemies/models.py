from django.db import models


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

    def __str__(self):
        return f'{self.pk} - {self.name}'


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

    def __str__(self):
        return f'{self.pk} - {self.name}'


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

    def __str__(self):
        return f'{self.pk} - {self.name}'


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

    def __str__(self):
        return f'{self.pk} - {self.name}'
