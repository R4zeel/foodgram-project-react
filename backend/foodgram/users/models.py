from django.db import models
from django.core.validators import MaxLengthValidator
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator

from api.constants import (LENGTH_FOR_CHARFIELD,
                           LENGTH_FOR_EMAIL,
                           LEN_ERROR_MESSAGE)


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
        max_length=LENGTH_FOR_EMAIL,
        unique=True,
        verbose_name='Почта'
    )
    password = models.CharField(
        max_length=LENGTH_FOR_CHARFIELD,
        verbose_name='Пароль',
        validators=(
            MaxLengthValidator(
                LENGTH_FOR_CHARFIELD,
                LEN_ERROR_MESSAGE
            ),
        )
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

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

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
    user = models.ForeignKey(
        ApiUser,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик'
    )
    relation = models.ForeignKey(
        ApiUser,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Подписка'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'relation'],
                name='unique subscription'
            )
        ]

    def __str__(self):
        return self.subscription.username
