from rest_framework import viewsets

from .models import Recipe


class RecipeViewSet(viewsets.ModelViewSet):
    queryet = Recipe.objects.all()
