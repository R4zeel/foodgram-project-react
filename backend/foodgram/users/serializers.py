from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from rest_framework_simplejwt.serializers import TokenObtainSerializer
from rest_framework_simplejwt.tokens import AccessToken
from djoser.serializers import UserSerializer

from .models import ApiUser, Subscription


class ApiUserSerializer(UserSerializer):
    class Meta:
        model = ApiUser
        fields = ('id', 'email', 'first_name', 'last_name', 'username', 'role')


class ApiTokenObtainSerializer(TokenObtainSerializer):
    email = serializers.CharField(required=True)
    token_class = AccessToken

    class Meta:
        model = ApiUser
        fields = ('email',)

    def validate(self, attrs):
        data = super().validate(attrs)
        access = self.get_token(self.user)
        data["auth_token"] = str(access)
        return data


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
