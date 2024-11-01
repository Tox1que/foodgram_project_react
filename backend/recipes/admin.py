from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db.models import Count

from .models import Ingredient, Recipe, RecipeIngredient, RecipeTag, Tag

User = get_user_model()


class RecipeIngredientInLine(admin.TabularInline):
    model = Recipe.ingredients.through
    extra = 1
    autocomplete_fields = ('ingredient',)


class RecipeTagsInLine(admin.TabularInline):
    model = Recipe.tags.through
    extra = 1


class RecipeTagAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'tag',)
    search_fields = ('tag__slug', 'tag__name',)
    list_filter = ('recipe', 'tag',)
    autocomplete_fields = ('recipe',)


class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'ingredient', 'amount')
    search_fields = ('ingredient__name',)
    list_filter = ('recipe', 'ingredient',)
    autocomplete_fields = ('ingredient',)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit',)
    search_fields = ('name',)
    list_filter = ('name',)


class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'color', 'name', 'slug')
    search_fields = ('slug', 'name',)

class RecipeAdmin(admin.ModelAdmin):
    list_display = ['name', 'author', 'is_favorited_count']
    inlines = (RecipeIngredientInLine, RecipeTagsInLine,)
    list_filter = ('name', 'author', 'tags',)
    search_fields = ('author__username', 'author__email', 'tags__slug')
    autocomplete_fields = ('author',)

    def is_favorited_count(self, obj):
        return obj.is_favorited_count

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(is_favorited_count=Count('favorited_by'))
        return queryset


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
admin.site.register(RecipeTag, RecipeTagAdmin)
