from rest_framework import status
from rest_framework.response import Response


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
        recipe=pk
    ).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
