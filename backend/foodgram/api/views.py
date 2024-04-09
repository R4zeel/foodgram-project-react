from django.db.models import Value, Case, When, BooleanField
from rest_framework import viewsets, mixins, filters, permissions
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from django_filters.rest_framework import DjangoFilterBackend

from .models import Recipe, Ingredient, Tag, FavoriteRecipe, ShoppingCartRecipe
from utils.filters import IngredientSearchFilter, RecipeSearchFilter
from utils.methods import detail_post_method, detail_delete_method
from utils.permissions import IsAuthenticatedAuthorOrReadOnly
from utils.serializers import (RecipeSerializerForRead,
                              IngredientSerializer,
                              TagSerializer,
                              RecipeSerializerForWrite,
                              FavoriteSerializerForWrite,
                              FavoriteCartSerializer,
                              CartSerializerForWrite)


class ListViewSet(mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet):
    permission_classes = (permissions.AllowAny,)
    pagination_class = None


class IngredientViewSet(ListViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = IngredientSearchFilter
    ordering_fields = ('name',)


class TagViewSet(ListViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializerForRead
    permission_classes = (IsAuthenticatedAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeSearchFilter
    pagination_class = LimitOffsetPagination
    search_fields = ('author', 'tags')

    def get_queryset(self):
        queryset = Recipe.objects.all().annotate(
            is_favorited=Case(
                When(
                    favoriterecipe__user__exact=self.request.user.id,
                    then=Value(True)
                ),
                default=Value(False),
                output_field=BooleanField()
            ),
            is_in_shopping_cart=Case(
                When(
                    shoppingcartrecipe__user__exact=self.request.user.id,
                    then=Value(True)
                ),
                default=Value(False),
                output_field=BooleanField()
            )
        ).order_by('id')
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method not in permissions.SAFE_METHODS:
            return RecipeSerializerForWrite
        return RecipeSerializerForRead


class FavoriteCartViewSet(mixins.CreateModelMixin,
                          mixins.DestroyModelMixin,
                          viewsets.GenericViewSet):
    queryset = Recipe.objects.all()
    serializer_class = FavoriteCartSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'recipe_id': self.kwargs['pk']})
        return context


class FavoriteRecipeViewSet(FavoriteCartViewSet):
    model_name = FavoriteRecipe

    def get_queryset(self):
        return Recipe.objects.filter(favoriterecipe__user=self.request.user)
    
    def get_serializer_class(self):
        if self.request.method not in permissions.SAFE_METHODS:
            return FavoriteSerializerForWrite
        return FavoriteCartSerializer

    @action(
        methods=['POST'],
        detail=True,
        url_path='favorite'
    )
    def add_to_favorites(self, request, pk):
        return detail_post_method(self, request, pk)
    
    @add_to_favorites.mapping.delete
    def delete_favorite(self, request, pk):
        return detail_delete_method(self, request, pk)
    

class ShoppingCartRecipeViewSet(FavoriteCartViewSet):
    model_name = ShoppingCartRecipe

    def get_queryset(self):
        return Recipe.objects.filter(shoppingcartrecipe__user=self.request.user)
    
    def get_serializer_class(self):
        if self.request.method not in permissions.SAFE_METHODS:
            return CartSerializerForWrite
        return FavoriteCartSerializer

    @action(
        methods=['POST'],
        detail=True,
        url_path='shopping_cart'
    )
    def add_to_cart(self, request, pk):
        return detail_post_method(self, request, pk)
    
    @add_to_cart.mapping.delete
    def delete_favorite(self, request, pk):
        return detail_delete_method(self, request, pk)
