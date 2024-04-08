from django.db.models import Value, Case, When, BooleanField
from rest_framework.response import Response
from rest_framework import viewsets, mixins, filters, status
from rest_framework.decorators import action
from rest_framework import permissions
from django_filters.rest_framework import DjangoFilterBackend

from .models import Recipe, Ingredient, Tag, FavoriteRecipe, ShoppingCartRecipe
from utils.serializers import (RecipeSerializerForRead,
                          IngredientSerializer,
                          TagSerializer,
                          RecipeSerializerForWrite,
                          FavoriteSerializerForWrite,
                          FavoriteCartSerializer,
                          CartSerializerForWrite)
from .filters import IngredientSearchFilter


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
    permission_classes = (permissions.AllowAny,)

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
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @add_to_favorites.mapping.delete
    def delete_favorite(self, request, pk):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        FavoriteRecipe.objects.filter(
            user=self.request.user,
            recipe=pk
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class ShoppingCartRecipeViewSet(FavoriteCartViewSet):
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
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @add_to_cart.mapping.delete
    def delete_favorite(self, request, pk):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ShoppingCartRecipe.objects.filter(
            user=self.request.user,
            recipe=pk
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
