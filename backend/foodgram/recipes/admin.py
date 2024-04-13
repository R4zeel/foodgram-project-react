from django.contrib import admin

from .models import Tag, Ingredient, Recipe


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    search_fields = ('name', 'color', 'slug')
    list_filter = ('color',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'name',
        'text',
        'image',
        'get_ingredients',
        'get_tags',
        'cooking_time',
        'get_favorites_count',
        'created_at'
    )
    filter_horizontal = ('tags', 'id')

    @admin.display(description='Ингредиенты')
    def get_ingredients(self, obj):
        return ' ,'.join(
            [ingredient.name for ingredient in obj.ingredients.all()]
        )

    @admin.display(description='Тэги')
    def get_tags(self, obj):
        return ' ,'.join(
            [tag.name for tag in obj.tags.all()]
        )

    @admin.display(description='Добавлений в избранное')
    def get_favorites_count(self, obj):
        return obj.favoriterecipe_set.all().count()
