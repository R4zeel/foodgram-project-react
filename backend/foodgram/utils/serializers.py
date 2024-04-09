import base64

from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile
from django.db.models import Value, Count, Case, When
from django.db.utils import IntegrityError
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from users.models import ApiUser, Subscription
from api.models import (Recipe,
                        Ingredient,
                        Tag,
                        RecipeIngredient,
                        FavoriteRecipe,
                        ShoppingCartRecipe,
                        ApiUser)


class ApiUserSerializerForRead(serializers.ModelSerializer):
    is_subscribed = serializers.BooleanField()

    class Meta:
        model = ApiUser
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'username',
            'is_subscribed'
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
        subscription_user = get_object_or_404(ApiUser, id=self.context['subscription_id'])
        if self.context['request'].user == subscription_user:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя'
                )
        subscription = self.Meta.model.objects.filter(
            user=self.context['request'].user,
            subscription=subscription_user
        )
        if self.context['request'].method == 'DELETE':
            if not subscription.exists():
                raise serializers.ValidationError('Связи не существует')
            return attrs
        if subscription.exists():
            raise serializers.ValidationError('Связь уже существует')
        return attrs
    
    def to_representation(self, instance):
        return SubscriptionSerializerForRead(
            instance=ApiUser.objects.annotate(
                is_subscribed=Value(True),
                recipes_count=Count('recipes')
            ).get(
                id=instance.subscription_id
            ),
            context=self.context['request'].query_params
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

    def validate(self, attrs):
        try:
            attrs['ingredients'] = self.initial_data['ingredients']
            if len(attrs['tags']) != len(set(attrs['tags'])):
                raise serializers.ValidationError(
                'Тэги не должны повторяться'
                )
        except KeyError:
            raise serializers.ValidationError(
                'Запрос должен содержать все необходимые поля'
            )
        if not attrs['ingredients']:
            raise serializers.ValidationError(
                'Поле ингредиентов не может быть пустым'
            )
        for item in attrs['ingredients']:
            if not Ingredient.objects.filter(id=item['id']).exists():
                raise serializers.ValidationError('Ингредиента не существует')
            if item['amount'] < 1:
                raise serializers.ValidationError(
                    'Количество не может быть меньше одного'
                    )
        return attrs

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            ingredient['ingredient_id'] = ingredient.pop('id')
            try:
                RecipeIngredient.objects.create(recipe=recipe, **ingredient)
            except IntegrityError:
                raise serializers.ValidationError(
                    'В рецепте не может быть повторяющихся ингредиентов'
                )
        return recipe
    
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        Recipe.objects.filter(id=instance.pk).update(**validated_data)
        recipe = get_object_or_404(Recipe, id=instance.pk)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            recipe_ingredient = RecipeIngredient.objects.get(
                recipe=recipe, 
                ingredient=ingredient['id']
            )
            try:
                recipe_ingredient.id = ingredient['id']
                recipe_ingredient.amount = ingredient['amount']
                recipe_ingredient.save()
            except IntegrityError:
                raise serializers.ValidationError(
                    'В рецепте не может быть повторяющихся ингредиентов'
                )
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
        recipe = get_object_or_404(Recipe, id=self.context['recipe_id'])
        added_recipe = self.Meta.model.objects.filter(
            user=self.context['request'].user,
            recipe=recipe
        )
        if self.context['request'].method == 'DELETE':
            if not added_recipe.exists():
                raise serializers.ValidationError('Связи не существует')
            return attrs
        if added_recipe.exists():
            raise serializers.ValidationError('Рецепт уже добавлен')
        return attrs
    
    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except IntegrityError:
            raise serializers.ValidationError('Рецепта не существует')

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
    recipes = serializers.SerializerMethodField('get_recipes')
    recipes_count = serializers.IntegerField()

    class Meta:
        model = ApiUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_recipes(self, instance):
        user = ApiUser.objects.get(id=instance.pk)
        if self.context:
            limit = int(self.context['recipes_limit'])
            queryset = user.recipes.all()[:limit]
        else:
            queryset = user.recipes.all()
        return FavoriteCartSerializer(queryset, many=True).data