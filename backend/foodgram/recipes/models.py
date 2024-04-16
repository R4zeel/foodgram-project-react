from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from colorfield.fields import ColorField

from api.constants import (LENGTH_FOR_CHARFIELD,
                           LENGTH_FOR_RECIPE_NAME,
                           LENGTH_FOR_TEXTFIELD,
                           MIN_VALIDATOR_VALUE,
                           MIN_VALIDATOR_ERROR_MESSAGE,
                           MAX_AMOUNT_VALUE,
                           MAX_VALIDATOR_ERROR_MESSAGE)
from users.models import ApiUser


class Recipe(models.Model):
    author = models.ForeignKey(
        ApiUser,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='recipes'
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=LENGTH_FOR_RECIPE_NAME
    )
    image = models.ImageField()
    text = models.TextField(
        verbose_name='Описание',
        max_length=LENGTH_FOR_TEXTFIELD
    )
    ingredients = models.ManyToManyField(
        'Ingredient',
        through='RecipeIngredient',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        'Tag',
        verbose_name='Тэги',
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления',
        validators=(
            MinValueValidator(
                MIN_VALIDATOR_VALUE,
                MIN_VALIDATOR_ERROR_MESSAGE
            ),
        )
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        max_length=LENGTH_FOR_CHARFIELD,
        verbose_name='Название'
    )
    color = ColorField(default='#FFFFFF', unique=True)
    slug = models.SlugField(
        verbose_name='Слаг',
        unique=True
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name

    def clean(self):
        # Тут отдельно поднимать исключение судя по всему не нужно,
        # статускод 500 больше не выбрасывается
        self.color = self.color.lower()


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=LENGTH_FOR_CHARFIELD
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=LENGTH_FOR_CHARFIELD
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'name',
                    'measurement_unit'
                ],
                name='unique ingredients for a recipe'
            )
        ]

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
        validators=(
            MinValueValidator(
                MIN_VALIDATOR_VALUE,
                MIN_VALIDATOR_ERROR_MESSAGE
            ),
            MaxValueValidator(
                MAX_AMOUNT_VALUE,
                MAX_VALIDATOR_ERROR_MESSAGE
            )
        )
    )

    class Meta:
        default_related_name = 'recipe_ingredients'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique ingredient'
            )
        ]

    def __str__(self):
        return self.ingredient.name


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(ApiUser, on_delete=models.CASCADE)
    relation = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    def __str__(self):
        return self.relation.name

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'relation'],
                name='unique favorite'
            )
        ]


class ShoppingCartRecipe(models.Model):
    user = models.ForeignKey(ApiUser, on_delete=models.CASCADE)
    relation = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    def __str__(self):
        return self.relation.name

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'relation'],
                name='unique cart'
            )
        ]
