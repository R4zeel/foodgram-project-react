from io import BytesIO

from django.db.models import Value, Case, When, BooleanField
from django.http import FileResponse
from rest_framework import viewsets, mixins, filters, permissions
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend

from api.filters import IngredientSearchFilter, RecipeSearchFilter
from api.permissions import IsAuthenticatedOrReadOnly, IsAuthor
from api.paginators import LimitParamPagination
from api.methods import (detail_post_method,
                         detail_delete_method,
                         get_cart_list)
from recipes.models import (Recipe,
                            Ingredient,
                            Tag,
                            FavoriteRecipe,
                            ShoppingCartRecipe,)
from .serializers import (RecipeSerializerForRead,
                          IngredientSerializer,
                          TagSerializer,
                          RecipeSerializerForWrite,
                          FavoriteSerializerForWrite,
                          FavoriteCartSerializer,
                          CartSerializerForWrite)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = IngredientSearchFilter
    ordering_fields = ('name',)
    pagination_class = None


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().annotate(
        is_favorited=Value(False),
        is_in_shopping_cart=Value(False)
    ).order_by('-created_at')
    serializer_class = RecipeSerializerForRead
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = LimitParamPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeSearchFilter
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return self.queryset
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

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticatedOrReadOnly()]
        if self.request.method not in permissions.SAFE_METHODS:
            return [IsAuthor()]
        return [permission() for permission in self.permission_classes]

    @action(
        methods=['GET'],
        detail=False,
        url_path='download_shopping_cart',
        permission_classes=[permissions.IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        result = get_cart_list(self.request.user)
        buffer = BytesIO(str.encode(result))
        return FileResponse(buffer, filename='test.txt', as_attachment=True)


class FavoriteCartViewSet(mixins.CreateModelMixin,
                          mixins.DestroyModelMixin,
                          viewsets.GenericViewSet):
    queryset = Recipe.objects.all()
    serializer_class = FavoriteCartSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'relation_id': self.kwargs['pk']})
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
        return detail_post_method(self, request, self.kwargs['pk'])

    @add_to_favorites.mapping.delete
    def delete_favorite(self, request, pk):
        return detail_delete_method(self, request, self.kwargs['pk'])


class ShoppingCartRecipeViewSet(FavoriteCartViewSet):
    model_name = ShoppingCartRecipe

    def get_queryset(self):
        return Recipe.objects.filter(
            shoppingcartrecipe__user=self.request.user
        )

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
        return detail_post_method(self, request, self.kwargs['pk'])

    @add_to_cart.mapping.delete
    def delete_favorite(self, request, pk):
        return detail_delete_method(self, request, self.kwargs['pk'])
