from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token

from .models import ApiUser, Subscription
from .serializers import (SubscriptionSerializer,
                          ApiUserSerializer,
                          ObtainTokenSerializer,
                          SetPasswordSerializer)


class ApiUserViewSet(viewsets.ModelViewSet):
    queryset = ApiUser.objects.all()
    serializer_class = ApiUserSerializer
    permission_classes = (AllowAny,)

    @action(
        methods=['GET'],
        detail=False,
        url_path='',
        permission_classes=(AllowAny,)
    )
    def users_list(self, request):
        users = ApiUser.objects.all()
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)

    @action(
        methods=['POST'],
        detail=False,
    )
    def user_create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=(IsAuthenticated,),
        url_path='me'
    )
    def self_user_detail(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(
        methods=['GET'],
        detail=False,
    )
    def user_detail(self, request, pk=None):
        user = get_object_or_404(ApiUser, id=pk)
        serializer = self.get_serializer(data=user)
        return Response(serializer.data)

    # TODO: Срабатывает ошибка Nginx, метод не работает
    @action(
        methods=['POST'],
        detail=False,
        permission_classes=(AllowAny,),
        url_path='set_password'
    )
    def reset_password(self, request):
        serializer = SetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.request.user.set_password(
            serializer.data['new_password']
        )
        self.request.user.save()
        return Response('OK', status=status.HTTP_204_NO_CONTENT)


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
    serializer_class = SubscriptionSerializer

    def get_queryset(self):
        user = self.request.user
        return user.follower.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
