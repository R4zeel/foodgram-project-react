import base64

from rest_framework import serializers
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework.validators import UniqueTogetherValidator

from .models import (Recipe, 
                    Ingredient,
                    Tag,
                    RecipeIngredient,
                    FavoriteRecipe,
                    InShoppingCartRecipe,
                    User)
from users.serializers import ApiUserSerializer


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class RecipeSerializerForRead(serializers.ModelSerializer):
    image = Base64ImageField()
    ingredients = serializers.SerializerMethodField(
        'get_ingredients_with_amount'
    )
    tags = TagSerializer(many=True)
    author = ApiUserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    # TODO: аннотация?
    def get_ingredients_with_amount(self, validated_data):
        recipe = get_object_or_404(Recipe, pk=validated_data.id)
        ingredients = recipe.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            'recipe_ingredients__amount'
        )
        for item in ingredients:
            item['amount'] = item.pop('recipe_ingredients__amount')
        return ingredients


class RecipeSerializerForWrite(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def create(self, validated_data):
        ingredients = self.initial_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            ingredient['ingredient_id'] = ingredient.pop('id')
            RecipeIngredient.objects.create(recipe=recipe, **ingredient)
        return recipe

    def to_representation(self, instance):
        return RecipeSerializerForRead(instance=instance).data

    

class FavoriteCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')



class FavoriteCartSerializerForWrite(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
        )

    class Meta:
        model = None
        fields = ('recipe', 'user',)

    def validate(self, attrs):
        attrs['user'] = self.context['request'].user
        attrs['recipe_id'] = self.context['recipe_id']
        recipe = FavoriteRecipe.objects.filter(
            user=self.context['request'].user,
            recipe=self.context['recipe_id']
        )
        if self.context['request'].method == 'DELETE':
            if not recipe.exists():
                raise serializers.ValidationError('Связи не существует')
            return attrs
        if recipe.exists():
            raise serializers.ValidationError('Рецепт уже добавлен')
        return attrs

    def to_representation(self, instance):
        return FavoriteCartSerializer(
            instance=Recipe.objects.get(
                id=instance.recipe_id
                )
            ).data
    

class FavoriteSerializerForWrite(FavoriteCartSerializerForWrite):
    class Meta(FavoriteCartSerializerForWrite.Meta):
        model = FavoriteRecipe
