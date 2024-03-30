from rest_framework import routers
from django.urls import include, path

from .views import RecipeViewSet, IngredientViewSet, TagViewSet

router_v1 = routers.DefaultRouter()
router_v1.register('recipes', RecipeViewSet, basename='recipe')
router_v1.register('ingredients', IngredientViewSet, basename='ingredient')
router_v1.register('tags', TagViewSet, basename='tag')

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/', include('users.urls')),
]
