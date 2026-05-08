from django.db import models

from apps.accounts.models import User
from apps.products.models import Product
from lib.utils.schemas.products import PurchaseStatus


class Purchase(models.Model):
    class Meta:
        managed = False
        db_table = "purchases"
        verbose_name = "Покупка"
        verbose_name_plural = "Покупки"

    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="purchases",
        null=False,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="purchases",
        null=False,
    )
    status = models.CharField(
        verbose_name="Статус покупки",
        max_length=64,
        choices=PurchaseStatus.choices(),
    )
    amount = models.FloatField(verbose_name="Цена продукта")
    transaction_id = models.CharField(
        verbose_name="ID платежа (транзакции)",
        max_length=128,
        null=True,
        blank=True,
    )
    response_description = models.CharField(
        verbose_name="Описание ответа от платежной системы",
        max_length=2055,
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def __str__(self) -> str:
        return f"{self.pk} - {self.status}"
