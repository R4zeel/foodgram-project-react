from rest_framework.response import Response
from rest_framework import viewsets, mixins, filters, status
from rest_framework.decorators import action
from rest_framework import permissions
from django_filters.rest_framework import DjangoFilterBackend

from .models import Recipe, Ingredient, Tag
from .serializers import (RecipeSerializerForRead,
                          IngredientSerializer,
                          TagSerializer,
                          RecipeSerializerForWrite)
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

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method not in permissions.SAFE_METHODS:
            return RecipeSerializerForWrite
        return RecipeSerializerForRead

    # TODO: Не работают методы DEL из-за непонятной ошибки Nginx
    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        url_path='favorite'
    )
    def favorites(self, request, pk=None):
        recipe = self.get_object()
        if request.method == 'DELETE':
            recipe.is_favorited = False
            recipe.save()
            return Response('OK', status=status.HTTP_204_NO_CONTENT)
        recipe.is_favorited = True
        recipe.save()
        return Response(
            {
                'id': recipe.id,
                'name': recipe.name,
                'image': recipe.image.url,
                'cooking_time': recipe.cooking_time
            },
            status=status.HTTP_201_CREATED
        )

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        url_path='shopping_cart'
    )
    def shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        if request.method == 'DELETE':
            recipe.is_in_shopping_cart = False
            recipe.save()
            return Response('OK', status=status.HTTP_204_NO_CONTENT)
        recipe.is_in_shopping_cart = True
        recipe.save()
        return Response(
            {
                'id': recipe.id,
                'name': recipe.name,
                'image': recipe.image.url,
                'cooking_time': recipe.cooking_time
            },
            status=status.HTTP_201_CREATED
        )


