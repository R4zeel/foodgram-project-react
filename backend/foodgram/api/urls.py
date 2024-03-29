from rest_framework import routers
from django.urls import include, path

from .views import RecipeViewSet

router_v1 = routers.DefaultRouter()
router_v1.register('recipes', RecipeViewSet, basename='recipe')

urlpatterns = [
    path('v1/', include(router_v1.urls)),
]
