from django.db import models


class News(models.Model):
    class Meta:
        managed = False
        db_table = "news"
        verbose_name = "Новость (главная страница)"
        verbose_name_plural = "Новости (главная страница)"
        ordering = (
            "-priority",
            "-updated_at",
        )

    title = models.CharField(max_length=255, verbose_name="Название")
    text = models.TextField(verbose_name="Текст новости")
    is_active = models.BooleanField(default=True, verbose_name="Активна ли (будет ли показана)")
    priority = models.IntegerField(default=0, verbose_name="Приоритет показа")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def __str__(self) -> str:
        return f"Новость {self.pk}: {self.title}"
