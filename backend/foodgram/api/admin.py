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


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'name',
        'description',
        'image',
        'get_ingredients',
        'get_tag',
        'cook_time'
    )
    filter_horizontal = ('ingredients', 'tag')

    def get_ingredients(self, obj):
        return ' ,'.join(
            [ingredient.name for ingredient in obj.ingredients.all()]
        )

    def get_tag(self, obj):
        return ' ,'.join(
            [tag.name for tag in obj.tag.all()]
        )
