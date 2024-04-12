from io import BytesIO

from django.db.models import Value, Case, When, BooleanField
from django.http import FileResponse
from rest_framework import viewsets, mixins, filters, permissions
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend

from api.filters import IngredientSearchFilter, RecipeSearchFilter
from api.permissions import IsAuthenticatedOrReadOnly, IsAuthor
from api.paginators import RecipePagination
from api.methods import (detail_post_method,
                         detail_delete_method,
                         get_cart_queryset)
from recipes.models import (Recipe,
                            Ingredient,
                            Tag,
                            FavoriteRecipe,
                            ShoppingCartRecipe,)
from api.serializers import (RecipeSerializerForRead,
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
    queryset = Recipe.objects.all().annotate(
        is_favorited=Value(False),
        is_in_shopping_cart=Value(False)
    ).order_by('-id')
    serializer_class = RecipeSerializerForRead
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = RecipePagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeSearchFilter

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
        if self.request.method == 'PATCH' or self.request.method == 'DELETE':
            return [IsAuthor()]
        return [permission() for permission in self.permission_classes]

    @action(
        methods=['GET'],
        detail=False,
        url_path='download_shopping_cart',
        permission_classes=[permissions.IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        result = get_cart_queryset(self.request.user)
        # Такая конструкция не проходит pep8 при отправке на ревью
        # output_string = ''.join(
        #     [f'{item['ing_name']} - {item['amount']} \n'
        #      for item in queryset]
        # )
        buffer = BytesIO(str.encode(result))
        return FileResponse(buffer, filename='test.txt', as_attachment=True)


class FavoriteCartViewSet(mixins.CreateModelMixin,
                          mixins.DestroyModelMixin,
                          viewsets.GenericViewSet):
    queryset = Recipe.objects.all()
    serializer_class = FavoriteCartSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        try:
            context.update({'relation_id': int(self.kwargs['pk'])})
        except ValueError:
            raise ValueError('Введен некорректный ID')
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
        return detail_post_method(self, request, pk)

    @add_to_cart.mapping.delete
    def delete_favorite(self, request, pk):
        return detail_delete_method(self, request, pk)
