from rest_framework import viewsets
from djoser.views import UserViewSet
from rest_framework_simplejwt.views import TokenViewBase

from .models import ApiUser, Subscription
from .serializers import (SubscriptionSerializer,
                          ApiUserSerializer,
                          ApiTokenObtainSerializer)


class ApiUserViewSet(UserViewSet):
    queryset = ApiUser.objects.all()
    serializer_class = ApiUserSerializer

    def get_queryset(self):
        return self.request.user


class ApiTokenObtainView(TokenViewBase):
    serializer_class = ApiTokenObtainSerializer


class SubscribeViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer

    def get_queryset(self):
        user = self.request.user
        return user.follower.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
