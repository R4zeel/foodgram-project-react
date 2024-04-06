from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token

from .models import Subscription, ApiUser
from .serializers import (SubscriptionSerializerForRead,
                          SubscriptionSerializerForWrite,
                          ObtainTokenSerializer,)


class ObtainTokenView(ObtainAuthToken):
    serializer_class = ObtainTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = ObtainTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response(
            {'auth_token': str(token)}
        )


class DestroyTokenView(APIView):
    def post(self, request, *args, **kwargs):
        user = request.user
        Token.objects.filter(user=user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscribeViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializerForRead

    def get_serializer_class(self):
        if self.request.method not in permissions.SAFE_METHODS:
            return SubscriptionSerializerForWrite
        return SubscriptionSerializerForRead

    def create(self, request, *args, **kwargs):
        request.data.update({'subscribed': kwargs['user_id']})
        return super(SubscribeViewSet, self).create(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        return user.subscribed.all()

    def perform_create(self, serializer):
        serializer.save(subscriber=self.request.user)

