from rest_framework import status
from rest_framework.response import Response
from django.db.models import F, Value
from django.db.models.functions import Concat

from api.models import Recipe


def detail_post_method(self, request, pk):
    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


def detail_delete_method(self, request, pk):
    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    self.model_name.objects.filter(
        user=self.request.user,
        relation=pk
    ).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


def get_cart_queryset(user):
    queryset = Recipe.objects.filter(
        shoppingcartrecipe__user=user,
        id=F('shoppingcartrecipe__relation')
    ).values(
        'name'
    ).annotate(
        amount=F('recipe_ingredients__amount')
    ).annotate(
        ing_name=Concat(
            F('ingredients__name'),
            Value(', '),
            F('ingredients__measurement_unit')
        )
    )
    return queryset
