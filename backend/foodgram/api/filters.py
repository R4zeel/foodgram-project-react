from django_filters import rest_framework as filters

from recipes.models import Ingredient, Recipe


class IngredientSearchFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeSearchFilter(filters.FilterSet):
    author = filters.NumberFilter(field_name='author', lookup_expr='exact')
    tags = filters.CharFilter(field_name='tags__slug', lookup_expr='exact')
    is_favorited = filters.BooleanFilter(method='get_bool_for_favorite')
    is_in_shopping_cart = filters.BooleanFilter(method='get_bool_for_cart')

    class Meta:
        model = Recipe
        fields = (
            'author',
            'tags__slug',
            'favoriterecipe',
            'shoppingcartrecipe'
        )

    def get_bool_for_cart(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            queryset = queryset.filter(shoppingcartrecipe__user=user)
        return queryset

    def get_bool_for_favorite(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            queryset = queryset.filter(favoriterecipe__user=user)
        return queryset
