from django.shortcuts import get_object_or_404
from django.core import exceptions as django_exceptions
from django.db.models import Value, Count
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework.settings import api_settings
from djoser.serializers import SetPasswordSerializer

from api.base_serializers import ForWriteSeirlizer, FavoriteCartSerializer
from users.models import Subscription, ApiUser
from api.constants import (LENGTH_FOR_CHARFIELD,
                           LENGTH_FOR_EMAIL)


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
    password = serializers.CharField(
        write_only=True,
        max_length=LENGTH_FOR_CHARFIELD
    )

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
        try:
            validate_password(password)
        except django_exceptions.ValidationError as error:
            pass_error = serializers.as_serializer_error(error)
            raise serializers.ValidationError(
                {
                    "password": pass_error[api_settings.NON_FIELD_ERRORS_KEY]
                }
            )
        attrs['password'] = make_password(password)
        return attrs


class SetPasswordSerializer(SetPasswordSerializer):
    new_password = serializers.CharField(
        max_length=LENGTH_FOR_CHARFIELD,
    )


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
