from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import SubscribeViewSet, ApiUserViewSet, ApiTokenObtainView

users_router = DefaultRouter()
users_router.register('users', ApiUserViewSet, basename='signup')
users_router.register('subscriptions', SubscribeViewSet, basename='subscription')

urlpatterns = [
    path('', include(users_router.urls)),
    path('auth/token/login/', ApiTokenObtainView.as_view(), name='token')
]
