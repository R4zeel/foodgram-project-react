from django.db import models
from django.contrib.auth import get_user_model

from .constants import LENGTH_FOR_CHARFIELD, LENGTH_FOR_TEXTFIELD

User = get_user_model()


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
        )
    name = models.CharField(
        verbose_name='Название',
        max_length=LENGTH_FOR_TEXTFIELD
        )
    image = models.ImageField()
    description = models.TextField(
        verbose_name='Описание',
        max_length=LENGTH_FOR_TEXTFIELD
        )
    ingredients = models.ForeignKey(
        'Ingredient',
        on_delete=models.CASCADE,
        verbose_name='Ингредиенты'
        )
    tag = models.ForeignKey(
        'Tag',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Тэг'
        )
    cook_time = models.TimeField(verbose_name='Время приготовления')


class Tag(models.Model):
    name = models.CharField(
        max_length=LENGTH_FOR_CHARFIELD,
        verbose_name='Название'
    )
    color = models.CharField(
        max_length=LENGTH_FOR_CHARFIELD,
        verbose_name='Цвет'
    )
    slug = models.SlugField(
        verbose_name='Слаг'
    )


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=LENGTH_FOR_CHARFIELD
        )
    measure = models.CharField(
        verbose_name='Единица измерения',
        max_length=LENGTH_FOR_CHARFIELD
        )