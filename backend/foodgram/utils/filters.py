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
    tags_slug = filters.CharFilter(field_name='tags__slug', lookup_expr='iexact')
    is_favorited = filters.BooleanFilter(field_name='favoriterecipe')
    is_in_shopping_cart = filters.BooleanFilter(field_name='shoppingcartrecipe')

    class Meta:
        model = Recipe
        fields = ('author', 'tags__slug', 'favoriterecipe', 'shoppingcartrecipe')

