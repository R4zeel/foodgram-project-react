from django_filters import rest_framework as filters

from recipes.models import Ingredient, Recipe


class IngredientSearchFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeSearchFilter(filters.FilterSet):
    author = filters.NumberFilter(field_name='author', lookup_expr='exact')
    tags = filters.CharFilter(method='get_tags')
    is_favorited = filters.BooleanFilter(method='get_bool_for_favorite')
    is_in_shopping_cart = filters.BooleanFilter(method='get_bool_for_cart')

    class Meta:
        model = Recipe
        fields = (
            'author',
            'tags',
            'favoriterecipe',
            'shoppingcartrecipe'
        )

    def get_tags(self, queryset, name, value):
        tags = self.request.query_params.getlist('tags')
        queryset = Recipe.objects.filter(tags__slug__in=tags).distinct()
        return queryset

    def get_bool_for_cart(self, queryset, name, value):
        user = self.request.user
        if not user.is_authenticated:
            return queryset
        # Тут должен был стоять distinct на прошлом ревью, почему-то
        # отправилась неактуальная версия
        if value and user.is_authenticated:
            queryset = queryset.filter(
                shoppingcartrecipe__user=user
            ).distinct()
        return queryset

    def get_bool_for_favorite(self, queryset, name, value):
        user = self.request.user
        if not user.is_authenticated:
            return queryset
        if value and user.is_authenticated:
            queryset = queryset.filter(
                favoriterecipe__user=user
            ).distinct()
        return queryset
