from django.db import models

from lib.utils.events.event_types import EventType


class Event(models.Model):
    class Meta:
        managed = False
        db_table = "events"
        verbose_name = "Событие"
        verbose_name_plural = "События"

    id = models.AutoField(
        primary_key=True,
    )
    type = models.EmailField(
        unique=True,
        max_length=255,
        verbose_name="Название события",
        blank=False,
        null=False,
        choices=EventType.choices(),
    )
    processing = models.JSONField(
        default=list,
        blank=False,
        null=False,
        verbose_name="Конфиг события",
    )

    def __str__(self) -> str:
        return f"Событие {self.type}"
