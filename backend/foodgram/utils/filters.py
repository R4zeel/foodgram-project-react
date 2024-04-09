from django_filters import rest_framework as filters

from api.models import Ingredient, Recipe, Tag
from users.models import ApiUser


class IngredientSearchFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeSearchFilter(filters.FilterSet):
    author = filters.NumberFilter(field_name='author', lookup_expr='exact')
    tags = filters.CharFilter(field_name='tags', method='get_tags')

    class Meta:
        model = Recipe
        fields = ('author', 'tags')

    def get_tags(self, queryset, name, value):
        name = f'{name}__slug'
        return queryset.filter(
            tags__slug=value
        )
