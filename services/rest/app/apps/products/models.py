from django.db import models

from lib.utils.schemas.products import ProductType


class Product(models.Model):
    class Meta:
        managed = False
        db_table = "products"
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"
        ordering = (
            "-priority",
            "price",
            "-updated_at",
        )

    title = models.CharField(
        max_length=255,
        verbose_name="Название",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активен ли (будет ли показан)",
    )
    priority = models.IntegerField(
        default=0,
        verbose_name="Приоритет показа",
    )
    type = models.CharField(
        default=ProductType.RESOURCE,
        choices=ProductType.choices(),
    )
    price = models.FloatField(verbose_name="Цена продукта")
    data = models.JSONField(
        default=dict,
        blank=False,
        null=False,
        verbose_name="Данные о наградах",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def __str__(self) -> str:
        return f"Новость {self.pk}: {self.title}"
