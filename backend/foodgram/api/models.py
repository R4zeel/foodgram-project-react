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
    )

    def __str__(self):
        return self.name


# TODO: добавить colorfield для hex кодов
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

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField(verbose_name='Количество',)

    class Meta:
        default_related_name = 'recipe_ingredients'

    def __str__(self):
        return self.ingredient.name


class FavoriteRecipe(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.recipe.name


class ShoppingCartRecipe(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.recipe.name
