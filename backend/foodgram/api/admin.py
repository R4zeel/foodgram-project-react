from django.contrib import admin

from .models import Tag, Ingredient, Recipe


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    list_editable = ('name', 'color', 'slug')
    list_display_links = None


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measure')
    list_editable = ('name', 'measure')
    list_display_links = None
