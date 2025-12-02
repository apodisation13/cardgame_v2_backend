from django.contrib.auth.models import AbstractUser
from django.db import models


class DjangoAuthUser(AbstractUser):
    class Meta:
        db_table = "django_auth_users"
        verbose_name = "Администратор"
        verbose_name_plural = "Администраторы"

    is_active = models.BooleanField(default=True, verbose_name="Активный")

    def __str__(self) -> str:
        return self.username


class User(models.Model):
    class Meta:
        managed = False
        db_table = "users"
        verbose_name = "Пользователь игры"
        verbose_name_plural = "Пользователи игры"

    id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True, max_length=255, verbose_name="Почта пользователя")
    username = models.CharField(max_length=50, blank=False, null=False, verbose_name="Ник пользователя")
    password = models.CharField(max_length=255, blank=False, null=False, verbose_name="Пароль")
    is_active = models.BooleanField(default=True, verbose_name="Активный")

    def __str__(self) -> str:
        return f"Пользователь {self.pk}: {self.username} - {self.email}"
