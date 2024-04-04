from requests.models import Response
from rest_framework import viewsets, mixins, filters
from rest_framework.exceptions import APIException
from rest_framework.pagination import PageNumberPagination
from rest_framework import permissions
from django_filters.rest_framework import DjangoFilterBackend

from .models import Recipe, Ingredient, Tag
from .serializers import RecipeSerializerForRead,IngredientSerializer, TagSerializer, RecipeSerializerForWrite
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

