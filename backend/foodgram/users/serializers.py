from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import ApiUser, Subscription


class ApiUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = ApiUser
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'username',
            'password'
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


class SubscriptionSerializerForRead(serializers.ModelSerializer):
    email = serializers.CharField()
    is_subscribed = serializers.BooleanField(default=True)

    class Meta:
        model = Subscription
        fields = (
            'email',
            'is_subscribed'
        )


class SubscriptionSerializerForWrite(serializers.ModelSerializer):
    subscriber = serializers.StringRelatedField(
        required=False,
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Subscription
        fields = ('subscriber', 'subscribed')
        # validators = [
        #     UniqueTogetherValidator(
        #         queryset=Subscription.objects.all(),
        #         fields=['subscriber', 'subscribed']
        #     )
        # ]

    def validate(self, attrs):
        if attrs['subscribed'] == self.context['request'].user:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя'
            )
        return attrs

    def to_representation(self, instance):
        return SubscriptionSerializerForRead(
            instance=self.context['request'].user
        ).data
