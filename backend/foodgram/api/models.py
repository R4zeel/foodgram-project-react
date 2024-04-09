from django.db import models
from django.core.validators import MinValueValidator
from colorfield.fields import ColorField

from utils.constants import (LENGTH_FOR_CHARFIELD,
                             LENGTH_FOR_RECIPE_NAME,
                             LENGTH_FOR_TEXTFIELD,
                             MIN_VALIDATOR_VALUE,
                             MIN_VALIDATOR_ERROR_MESSAGE)
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
        verbose_name='Тэги'
        )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=(
            MinValueValidator(
                MIN_VALIDATOR_VALUE,
                MIN_VALIDATOR_ERROR_MESSAGE
            ),
        )
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        max_length=LENGTH_FOR_CHARFIELD,
        verbose_name='Название'
    )
    color = ColorField(default='#FFFFFF')
    slug = models.SlugField(
        verbose_name='Слаг'
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


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

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        # не работает?
        validators=(
            MinValueValidator(
                MIN_VALIDATOR_VALUE,
                MIN_VALIDATOR_ERROR_MESSAGE
            ),
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
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    user = models.ForeignKey(ApiUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.recipe.name


class ShoppingCartRecipe(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    user = models.ForeignKey(ApiUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.recipe.name
