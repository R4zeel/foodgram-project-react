from rest_framework import viewsets

from .models import ApiUser, Subscription
from .serializers import SubscriptionSerializer


class SubscribeViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer

    def get_queryset(self):
        user = self.request.user
        return user.follower.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
