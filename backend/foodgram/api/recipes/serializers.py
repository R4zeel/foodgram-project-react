import base64

from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile
from django.db import transaction
from django.db.utils import IntegrityError
from rest_framework import serializers

from api.base_serializers import ForWriteSeirlizer, FavoriteCartSerializer
from api.users.serializers import ApiUserSerializerForWrite
from recipes.models import (Recipe,
                            Ingredient,
                            Tag,
                            RecipeIngredient,
                            FavoriteRecipe,
                            ShoppingCartRecipe)


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
        model = RecipeIngredient
        fields = ('name', 'measurement_unit')


class TagRecipeSerializerForWrite(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = Tag
        fields = ('id',)


class IngredientRecipeSerializerForWrite(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')

    def create(self, validated_data):
        ingredient = validated_data.pop('id')
        recipe = self.initial_data.pop('recipe')
        recipe_ingredient = RecipeIngredient.objects.create(
            recipe=recipe,
            ingredient_id=ingredient,
            **validated_data
        )
        return recipe_ingredient


class RecipeSerializerForRead(serializers.ModelSerializer):
    image = Base64ImageField()
    ingredients = serializers.SerializerMethodField(
        'get_ingredients_with_amount'
    )
    tags = TagSerializer(many=True)
    author = ApiUserSerializerForWrite(read_only=True)
    is_favorited = serializers.BooleanField(default=False)
    is_in_shopping_cart = serializers.BooleanField(default=False)

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
            'is_favorited',
            'is_in_shopping_cart'
        )

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
    ingredients = IngredientRecipeSerializerForWrite(
        many=True
    )
    tags = TagRecipeSerializerForWrite(
        many=True,
        read_only=True
    )

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

    def validate(self, attrs):
        if not attrs['ingredients']:
            raise serializers.ValidationError(
                'Поле ингредиентов обязательно к заполнению.'
            )
        for item in attrs['ingredients']:
            if not Ingredient.objects.filter(id=item['id']).exists():
                raise serializers.ValidationError(
                    'Ингредиента не существует.'
                )
        for _ in self.initial_data['tags']:
            if not Tag.objects.filter(id=_).exists():
                raise serializers.ValidationError(
                    'Тега не существует.'
                )
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = self.initial_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        # Тут не стал добавлять проверку на уникальность тегов,
        # так как с такой конструкцией при пост запросе одинаковых тегов
        # создаются только уникальные
        try:
            recipe.tags.set(tags)
        except IntegrityError:
            raise serializers.ValidationError(
                'Тэга не существует.'
            )
        for ingredient in ingredients:
            try:
                ingredient['recipe'] = recipe
                recipe_ingredient = IngredientRecipeSerializerForWrite(
                    data=ingredient
                )
                recipe_ingredient.is_valid(raise_exception=True)
                recipe_ingredient.save()
            except IntegrityError:
                raise serializers.ValidationError(
                    'Ингредиенты не должны повторяться.'
                )
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = self.initial_data.pop('tags')
        Recipe.objects.filter(id=instance.pk).update(**validated_data)
        recipe = get_object_or_404(Recipe, id=instance.pk)
        recipe.tags.set(tags)
        RecipeIngredient.objects.filter(recipe=recipe).delete()
        for ingredient in ingredients:
            try:
                ingredient['recipe'] = recipe
                recipe_ingredient = IngredientRecipeSerializerForWrite(
                    data=ingredient
                )
                recipe_ingredient.is_valid(raise_exception=True)
                recipe_ingredient.save()
            except IntegrityError:
                raise serializers.ValidationError(
                    'Ингредиенты не должны повторяться.'
                )
        return recipe

    def to_representation(self, instance):
        return RecipeSerializerForRead(instance=instance).data


class FavoriteCartSerializerForWrite(ForWriteSeirlizer):
    relation = serializers.PrimaryKeyRelatedField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = None
        fields = ('user', 'relation')

    def validate(self, attrs):
        attrs['user'] = self.context['request'].user
        attrs['relation_id'] = self.context['relation_id']
        return super().validate(attrs)

    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except IntegrityError:
            raise serializers.ValidationError('Рецепта не существует')

    def to_representation(self, instance):
        return FavoriteCartSerializer(
            instance=Recipe.objects.get(
                id=instance.relation_id
            )
        ).data


class FavoriteSerializerForWrite(FavoriteCartSerializerForWrite):
    class Meta(FavoriteCartSerializerForWrite.Meta):
        model = FavoriteRecipe


class CartSerializerForWrite(FavoriteCartSerializerForWrite):
    class Meta(FavoriteCartSerializerForWrite.Meta):
        model = ShoppingCartRecipe
