from rest_framework import status
from rest_framework.response import Response
from django.db.models import F, Sum

from recipes.models import Recipe
from users.models import Subscription


def detail_post_method(self, request, pk):
    try:
        int(pk)
    except ValueError:
        if self.model_name == Subscription:
            return Response(
                'Пользователь не найден',
                status=status.HTTP_404_NOT_FOUND
            )
        return Response(
            'Введён некорректный ID',
            status=status.HTTP_400_BAD_REQUEST,
        )
    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


def detail_delete_method(self, request, pk):
    try:
        int(pk)
    except ValueError:
        if self.model_name == Subscription:
            return Response(
                'Пользователь не найден',
                status=status.HTTP_404_NOT_FOUND
            )
        return Response(
            'Введён некорректный ID',
            status=status.HTTP_400_BAD_REQUEST,
        )
    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    self.model_name.objects.filter(
        user=self.request.user,
        relation=pk
    ).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


def get_cart_list(user):
    queryset = Recipe.objects.filter(
        shoppingcartrecipe__user=user,
        id=F('shoppingcartrecipe__relation')
    ).values(
        'ingredients__name',
        'ingredients__measurement_unit'
    ).annotate(
        amount=Sum('recipe_ingredients__amount')
    )
    output = {}
    for item in queryset:
        output[item['ingredients__name']] = (
            str(
                item['amount']
            ) + item['ingredients__measurement_unit']
        )
    output_str = ''
    for key, value in output.items():
        output_str += ' '.join((key, value, '\n'))
    return output_str
