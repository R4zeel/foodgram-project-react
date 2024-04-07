from django.contrib.auth import authenticate
from django.db.models import Count, Value, Case, When, BooleanField, F
from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import ApiUser, Subscription


class ApiUserSerializerForRead(serializers.ModelSerializer):
    # is_subscribed = serializers.BooleanField()

    class Meta:
        model = ApiUser
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'username',
            # 'is_subscribed'
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


class SubscriptionSerializer(serializers.ModelSerializer):
    subscriber = serializers.StringRelatedField(
        required=False,
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    subscribed = serializers.PrimaryKeyRelatedField(
        read_only=True
    )

    class Meta:
        model = Subscription
        fields = ('subscriber', 'subscribed')

    def validate(self, attrs):
        attrs['subscriber'] = self.context['request'].user
        attrs['subscribed_id'] = self.context['subscribed_id']
        if self.context['request'].user.id == self.context['subscribed_id']:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя'
                )
        user = self.Meta.model.objects.filter(
            subscriber=self.context['request'].user,
            subscribed=self.context['subscribed_id']
        )
        if self.context['request'].method == 'DELETE':
            if not user.exists():
                raise serializers.ValidationError('Связи не существует')
            return attrs
        if user.exists():
            raise serializers.ValidationError('Связь уже существует')
        return attrs
    
    def to_representation(self, instance):
        return ApiUserSerializerForRead(
            instance=ApiUser.objects.get(
                id=instance.subscribed_id
            )
        ).data