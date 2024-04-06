from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator

from api.constants import LENGTH_FOR_CHARFIELD


class ApiUser(AbstractUser):

    class UserRoles(models.TextChoices):
        USER = 'user', 'Пользователь'
        MODERATOR = 'moderator', 'Модератор'
        ADMIN = 'admin', 'Администратор'

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username',)

    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        max_length=LENGTH_FOR_CHARFIELD,
        unique=True,
        verbose_name='Имя пользователя',
        validators=[username_validator]
    )
    email = models.EmailField(
        max_length=LENGTH_FOR_CHARFIELD,
        unique=True,
        verbose_name='Почта'
    )
    password = models.CharField(
        max_length=LENGTH_FOR_CHARFIELD,
        verbose_name='Пароль',
    )
    first_name = models.CharField(
        max_length=LENGTH_FOR_CHARFIELD,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=LENGTH_FOR_CHARFIELD,
        verbose_name='Фамилия'
    )
    role = models.CharField(
        max_length=LENGTH_FOR_CHARFIELD,
        verbose_name='Роль'
    )

    @property
    def is_admin(self):
        return (self.role == 'admin'
                or self.is_superuser
                or self.is_staff)

    @property
    def is_moderator(self):
        return self.role == 'moderator'

    def __str__(self):
        return self.username


class Subscription(models.Model):
    subscriber = models.ForeignKey(
        ApiUser,
        on_delete=models.CASCADE,
        related_name='subscriber'
    )
    subscribed = models.ForeignKey(
        ApiUser,
        on_delete=models.CASCADE,
        related_name='subscribed'
    )

    def __str__(self):
        return self.subscribed.username
