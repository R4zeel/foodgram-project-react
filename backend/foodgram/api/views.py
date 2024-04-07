from django.db.models import Count, Value
from rest_framework.response import Response
from rest_framework import viewsets, mixins, filters, status
from rest_framework.decorators import action
from rest_framework import permissions
from django_filters.rest_framework import DjangoFilterBackend

from .models import Recipe, Ingredient, Tag, FavoriteRecipe
from .serializers import (RecipeSerializerForRead,
                          IngredientSerializer,
                          TagSerializer,
                          RecipeSerializerForWrite,
                          FavoriteSerializerForWrite,
                          FavoriteCartSerializer)
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
    queryset = Recipe.objects.all() # .annotate(amount=Count('recipe_ingredients__amount')).order_by('name')
    serializer_class = RecipeSerializerForRead
    permission_classes = (permissions.AllowAny,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method not in permissions.SAFE_METHODS:
            return RecipeSerializerForWrite
        return RecipeSerializerForRead
    

class FavoriteRecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = FavoriteCartSerializer

    def get_queryset(self):
        return Recipe.objects.filter(favoriterecipe__user=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'recipe_id': self.kwargs['pk']})
        return context
    
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
