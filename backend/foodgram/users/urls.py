from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ObtainTokenView, DestroyTokenView

# users_router = DefaultRouter()
# users_router.register('subscriptions', SubscribeViewSet, basename='subscriptions')

urlpatterns = [
    # path('users/', include(users_router.urls)),
    path('', include('djoser.urls')),
    path('auth/token/login/', ObtainTokenView.as_view(), name='token'),
    path('auth/token/logout/', DestroyTokenView.as_view(), name='logout'),
]
