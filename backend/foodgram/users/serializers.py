from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from djoser.serializers import UserSerializer

from .models import ApiUser, Subscription


class ApiUserSerializer(UserSerializer):
    class Meta:
        model = ApiUser
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'role'
        )


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
