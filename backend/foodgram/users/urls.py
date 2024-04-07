from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ObtainTokenView, DestroyTokenView, SubscribeViewSet, ApiUserViewSet

users_router = DefaultRouter()
users_router.register('users', ApiUserViewSet, basename='users')
users_router.register('users', SubscribeViewSet, basename='subscriptions')


urlpatterns = [
    path('', include(users_router.urls)),
    path('auth/token/login/', ObtainTokenView.as_view(), name='token'),
    path('auth/token/logout/', DestroyTokenView.as_view(), name='logout'),
]
