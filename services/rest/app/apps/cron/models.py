from django.db import models


class CronTask(models.Model):
    class Meta:
        managed = False
        db_table = "cron_tasks"
        verbose_name = "Периодическая задача"
        verbose_name_plural = "Периодические задачи"

    id = models.AutoField(
        primary_key=True,
    )
    name = models.EmailField(
        unique=True,
        max_length=255,
        verbose_name="Название задачи",
        blank=False,
        null=False,
    )
    schedule = models.CharField(
        max_length=50,
        blank=False,
        null=False,
        verbose_name="Расписание (по крону)",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Включена",
    )

    def __str__(self) -> str:
        return f"Задача {self.name}"
