from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    class Meta:
        managed = False
        db_table = 'users'

    email = models.EmailField("email", unique=True)
    is_active = models.BooleanField("active", default=True)

    def __str__(self):
        return self.email or self.username
