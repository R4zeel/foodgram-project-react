from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from djoser.serializers import UserSerializer

from .models import ApiUser, Follow


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


class FollowSerializer(serializers.ModelSerializer):
    follower = serializers.StringRelatedField(
        required=False,
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    following = serializers.SlugRelatedField(
        slug_field='username',
        queryset=ApiUser.objects.all()
    )

    class Meta:
        model = Follow
        fields = ('follower', 'following')
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=['follower', 'following']
            )
        ]

    def validate(self, attrs):
        if attrs['following'] == self.context['request'].user:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя'
            )
        return attrs
