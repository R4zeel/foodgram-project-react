import base64

from django.contrib.auth import authenticate
from django.db.models import Value
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404

from users.models import ApiUser, Subscription
from api.models import (Recipe,
                    Ingredient,
                    Tag,
                    RecipeIngredient,
                    FavoriteRecipe,
                    ShoppingCartRecipe,
                    ApiUser)


class ApiUserSerializerForRead(serializers.ModelSerializer):

    class Meta:
        model = ApiUser
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'username',
            )


class ApiUserSerializerForWrite(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = ApiUser
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'username',
            'password',
        )

    def validate(self, attrs):
        password = attrs.get('password')
        attrs['password'] = make_password(password)
        return attrs


class SetPasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class ObtainTokenSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=128, required=True)
    password = serializers.CharField(max_length=128, required=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        if not email and not password:
            raise serializers.ValidationError(
                'Все поля обязательны к заполнению'
            )
        user = authenticate(
            request=self.context.get('request'),
            email=email,
            password=password
        )
        if not user:
            raise serializers.ValidationError(
                'Введены некорректные данные.'
            )
        attrs['user'] = user
        return attrs
    

class SubscriptionSerializerForWrite(serializers.ModelSerializer):
    user = serializers.StringRelatedField(
        required=False,
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    subscription = serializers.PrimaryKeyRelatedField(
        read_only=True
    )

    class Meta:
        model = Subscription
        fields = ('user', 'subscription')

    def validate(self, attrs):
        attrs['user'] = self.context['request'].user
        attrs['subscription_id'] = self.context['subscription_id']
        if self.context['request'].user.id == self.context['subscription_id']:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя'
                )
        user = self.Meta.model.objects.filter(
            user=self.context['request'].user,
            subscription=self.context['subscription_id']
        )
        if self.context['request'].method == 'DELETE':
            if not user.exists():
                raise serializers.ValidationError('Связи не существует')
            return attrs
        if user.exists():
            raise serializers.ValidationError('Связь уже существует')
        return attrs
    
    def to_representation(self, instance):
        return SubscriptionSerializerForRead(
            instance=ApiUser.objects.annotate(
                is_subscribed=Value(True)
            ).get(
                id=instance.subscription_id
            )
        ).data

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

    # Пробовал реализовать amount через аннотацию на уровне queryset'а во
    #  вьюсете - не работает
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
        recipe = self.Meta.model.objects.filter(
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


class CartSerializerForWrite(FavoriteCartSerializerForWrite):
    class Meta(FavoriteCartSerializerForWrite.Meta):
        model = ShoppingCartRecipe


class SubscriptionSerializerForRead(serializers.ModelSerializer):
    is_subscribed = serializers.BooleanField()
    recipes = FavoriteCartSerializer(many=True)

    class Meta:
        model = ApiUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes'
        )