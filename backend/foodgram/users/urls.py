from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (SubscribeViewSet,
                    ApiUserViewSet,
                    ObtainTokenView,
                    DestroyTokenView)

users_router = DefaultRouter()
users_router.register('users', ApiUserViewSet, basename='user')
users_router.register('subscriptions', SubscribeViewSet, basename='subscription')

urlpatterns = [
    path('', include(users_router.urls)),
    path('auth/token/login/', ObtainTokenView.as_view(), name='token'),
    path('auth/token/logout/', DestroyTokenView.as_view(), name='logout')
]
