from django.db.models import Count, Value, Case, When, BooleanField, F
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from djoser.views import UserViewSet

from .models import Subscription, ApiUser
from .serializers import ObtainTokenSerializer


class ApiUserViewSet(UserViewSet):
    queryset = ApiUser.objects.all() # .annotate(
    #     is_subscribed=Case(
    #         When(...),
    #         default=Value(False),
    #         output_field=BooleanField()
    #     )
    # ).order_by('id')


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


# class SubscribeViewSet(viewsets.ModelViewSet):
#     queryset = Subscription.objects.all()
#     serializer_class = SubscriptionSerializerForRead
#     permission_classes = (permissions.AllowAny,)

#     def get_serializer_class(self):
#         if self.request.method not in permissions.SAFE_METHODS:
#             return SubscriptionSerializerForWrite
#         return SubscriptionSerializerForRead

#     def get_queryset(self):
#         user = self.request.user
#         return Subscription.objects.filter(subscriber=user)

#     def perform_create(self, serializer):
#         serializer.save(subscriber=self.request.user)
    
#     @action(
#         methods=['POST'],
#         detail=True,
#         permission_classes=[permissions.IsAuthenticated],
#         url_path='subscribe'
#     )
#     def subscribe(self, request, pk):
#         request.data.update({'subscribed': pk})
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save(subscriber=self.request.user)
#         return Response(serializer.data, status=status.HTTP_201_CREATED)


