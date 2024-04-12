from rest_framework import serializers

from recipes.models import Recipe


class ForWriteSeirlizer(serializers.ModelSerializer):
    class Meta:
        model = None
        fields = None

    def validate(self, attrs):
        relation = self.Meta.model.objects.filter(
            user=self.context['request'].user,
            relation_id=attrs['relation_id']
        )
        if self.context['request'].method == 'DELETE':
            if not relation.exists():
                raise serializers.ValidationError('Связи не существует')
            return attrs
        if relation.exists():
            raise serializers.ValidationError('Связь уже существует')
        return attrs


class FavoriteCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
