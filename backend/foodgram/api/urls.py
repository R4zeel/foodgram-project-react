from rest_framework import routers
from django.urls import include, path

from .views import RecipeViewSet, IngredientViewSet, TagViewSet, FavoriteRecipeViewSet, ShoppingCartRecipeViewSet

router_v1 = routers.DefaultRouter()
router_v1.register('recipes', RecipeViewSet, basename='recipe')
router_v1.register('recipes', FavoriteRecipeViewSet, basename='favorite')
router_v1.register('recipes', ShoppingCartRecipeViewSet, basename='shopping_cart')
router_v1.register('ingredients', IngredientViewSet, basename='ingredient')
router_v1.register('tags', TagViewSet, basename='tag')

urlpatterns = [
    path('', include(router_v1.urls)),
    path('', include('users.urls')),
]
