from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import SubscribeViewSet

users_router = DefaultRouter()
users_router.register('subscriptions', SubscribeViewSet, basename='subscription')

urlpatterns = [
    path('', include('djoser.urls')),
    path('', include(users_router.urls)),
    path('auth/', include('djoser.urls.jwt'))
]