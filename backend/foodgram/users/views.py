from django.db.models import Count, Value, Case, When, BooleanField, F
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, permissions, mixins
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from djoser.views import UserViewSet

from .models import Subscription, ApiUser
from .serializers import (ObtainTokenSerializer,
                          ApiUserSerializerForRead,
                          ApiUserSerializerForWrite,
                          SubscriptionSerializerForWrite,
                          SubscriptionSerializerForRead)


class ApiUserViewSet(UserViewSet):
    queryset = ApiUser.objects.all()

    def get_queryset(self):
        queryset = ApiUser.objects.all().annotate(
            is_subscribed=Case(
                When(
                    subscriptions__user__exact=self.request.user.id,
                    then=Value(True)
                ),
                default=Value(False),
                output_field=BooleanField()
            )
        ).order_by('id')
        return queryset
    
    @action(
    methods=['GET'],
    detail=False,
    url_path='subscriptions'
    )
    def get_subscriptions(self, request):
        subscriptions = self.get_queryset().filter(is_subscribed=True)
        serializer = SubscriptionSerializerForRead(subscriptions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


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


class SubscribeViewSet(mixins.CreateModelMixin,
                       mixins.DestroyModelMixin,
                       viewsets.GenericViewSet):
    queryset = ApiUser.objects.all()
    serializer_class = SubscriptionSerializerForRead
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        queryset = ApiUser.objects.all().annotate(
            is_subscribed=Case(
                When(
                    subscriptions__exact=self.request.user.id,
                    then=Value(True)
                ),
                default=Value(False),
                output_field=BooleanField()
            )
        ).order_by('id')
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.request.method not in permissions.SAFE_METHODS:
            context.update({'subscription_id': self.kwargs['pk']})
        return context
    
    def get_serializer_class(self):
        if self.request.method not in permissions.SAFE_METHODS:
            return SubscriptionSerializerForWrite
        return SubscriptionSerializerForRead
    
    @action(
        methods=['POST'],
        detail=True,
        url_path='subscribe'
    )
    def subscribe(self, request, pk):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @subscribe.mapping.delete
    def unsubscribe(self, request, pk):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        Subscription.objects.filter(
            subscriber=self.request.user,
            subscribed=pk
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
