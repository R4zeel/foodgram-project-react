from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token

from .models import ApiUser, Subscription
from .serializers import (SubscriptionSerializer,
                          ApiUserSerializer,
                          ObtainTokenSerializer)


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


class SubscribeViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer

    def get_queryset(self):
        user = self.request.user
        return user.follower.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
