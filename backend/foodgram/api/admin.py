from django.contrib import admin

from .models import Tag, Ingredient, Recipe


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    list_editable = ('name', 'color', 'slug')
    list_display_links = None
    search_fields = ('name', 'color', 'slug')
    list_filter = ('color',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_editable = ('name', 'measurement_unit')
    list_display_links = None
    search_fields = ('name',)
