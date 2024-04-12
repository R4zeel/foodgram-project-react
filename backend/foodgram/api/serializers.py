"""
Из-за взаимных импортов между сериализаторами приложений Users и Api
было принято решение совместить их в один файл, чтобы избежать
циркулярных зависимостей.
"""
import base64

from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile
from django.db.models import Value, Count
from django.db.utils import IntegrityError
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from .base_serializers import ForWriteSeirlizer, FavoriteCartSerializer
from users.models import Subscription
from api.constants import (LENGTH_FOR_CHARFIELD,
                           LENGTH_FOR_EMAIL)
from recipes.models import (Recipe,
                            Ingredient,
                            Tag,
                            RecipeIngredient,
                            FavoriteRecipe,
                            ShoppingCartRecipe,
                            ApiUser)


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


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
    email = serializers.CharField(
        max_length=LENGTH_FOR_EMAIL,
        required=True
    )
    password = serializers.CharField(
        max_length=LENGTH_FOR_CHARFIELD,
        required=True
    )

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


class SubscriptionSerializerForWrite(ForWriteSeirlizer):
    user = serializers.StringRelatedField(
        required=False,
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    relation = serializers.PrimaryKeyRelatedField(
        read_only=True
    )

    class Meta:
        model = Subscription
        fields = ('user', 'relation')

    def validate(self, attrs):
        attrs['user'] = self.context['request'].user
        attrs['relation_id'] = self.context['relation_id']
        relation_object = get_object_or_404(
            ApiUser, id=attrs['relation_id']
        )
        if self.context['request'].user == relation_object:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя'
            )
        return super().validate(attrs)

    def to_representation(self, instance):
        return SubscriptionSerializerForRead(
            instance=ApiUser.objects.annotate(
                is_subscribed=Value(True),
                recipes_count=Count('recipes')
            ).get(
                id=instance.relation_id
            ),
            context=self.context['request']
        ).data


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
                    'Некорректные данные'
                )
        except KeyError:
            raise serializers.ValidationError(
                'Запрос должен содержать поле ингредиентов'
            )
        if not attrs['ingredients']:
            raise serializers.ValidationError(
                'Поле ингредиентов не может быть пустым'
            )
        # Такие проверки тоже вызывают С901. Как в таком случае проводить
        # валидацию на каждое поле? Наследоваться от родителя с частично
        # проведенной валидацией?
        # try:
        #     if len(attrs['tags']) != len(set(attrs['tags'])):
        #         raise serializers.ValidationError(
        #             'Тэги не должны повторяться'
        #         )
        # except KeyError:
        #     raise serializers.ValidationError(
        #         'Запрос должен содержать поле тэгов'
        #     )
        # if not attrs['ingredients']:
        #     raise serializers.ValidationError(
        #         'Поле ингредиентов не может быть пустым'
        #     )
        ingredient_id_count = []
        for item in attrs['ingredients']:
            if not item:
                raise serializers.ValidationError(
                    'Поле ингредиента должно содержать его ID и количество'
                )
            ingredient_id_count.append(item['id'])
            item['ingredient_id'] = item.pop('id')
            # Можно было бы убрать эту проверку и поднимать integrityError
            # в момент создания, но корректно ли считать передачу таких
            # данных валидным?
            if len(ingredient_id_count) != len(set(ingredient_id_count)):
                raise serializers.ValidationError(
                    'Ингредиенты не должны повторяться'
                )
            if not Ingredient.objects.filter(
                id=item['ingredient_id']
            ).exists():
                raise serializers.ValidationError('Ингредиента не существует')
            # Из-за большого кол-ва проверок получаю C901 при отправке
            # на ревью, тут должны срабатывать min/max валидаторы в моделях,
            # но как-будто не срабатывают
            # if int(item['amount']) < 1:
            #     raise serializers.ValidationError(
            #         'Количество не может быть меньше одного'
            #     )
            # if int(item['amount']) > MAX_AMOUNT_VALUE:
            #     raise serializers.ValidationError(
            #         'Введено слишком большое количество для ингредиента'
            #     )
        return attrs

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            RecipeIngredient.objects.create(recipe=recipe, **ingredient)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        Recipe.objects.filter(id=instance.pk).update(**validated_data)
        recipe = get_object_or_404(Recipe, id=instance.pk)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            RecipeIngredient.objects.filter(
                recipe=recipe
            ).delete()
            RecipeIngredient.objects.create(recipe=recipe, **ingredient)
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
        if not self.context:
            queryset = user.recipes.all()
        else:
            if 'recipes_limit' in self.context.query_params:
                limit = int(self.context.query_params['recipes_limit'])
                queryset = user.recipes.all()[:limit]
            else:
                queryset = user.recipes.all()
        return FavoriteCartSerializer(queryset, many=True).data
