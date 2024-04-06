from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (SubscribeViewSet,
                    ObtainTokenView,
                    DestroyTokenView,)

users_router = DefaultRouter()
users_router.register('(?P<user_id>\d+)/subscribe', SubscribeViewSet, basename='subscriptions')

urlpatterns = [
    path('', include('djoser.urls')),
    path('users/', include(users_router.urls)),
    path('auth/token/login/', ObtainTokenView.as_view(), name='token'),
    path('auth/token/logout/', DestroyTokenView.as_view(), name='logout'),
]
