from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import ApiUser, Subscription


class ApiUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApiUser
        fields = ('id', 'email', 'first_name', 'last_name', 'username', 'role')


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
            raise serializers.ValidationError('Введены некорректные данные')
        attrs['user'] = user
        return attrs


class SubscriptionSerializer(serializers.ModelSerializer):
    subscriber = serializers.StringRelatedField(
        required=False,
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    subscribed = serializers.SlugRelatedField(
        slug_field='username',
        queryset=ApiUser.objects.all()
    )

    class Meta:
        model = Subscription
        fields = ('subscriber', 'subscribed')
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=['subscriber', 'subscribed']
            )
        ]

    def validate(self, attrs):
        if attrs['subscribed'] == self.context['request'].user:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя'
            )
        return attrs
