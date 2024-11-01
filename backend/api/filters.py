from django.contrib.auth import get_user_model
from django_filters import AllValuesMultipleFilter, BooleanFilter, FilterSet
from django_filters.filters import CharFilter

from recipes.models import Ingredient, Recipe

User = get_user_model()


class RecipeFilter(FilterSet):
    is_favorited = BooleanFilter(
        field_name='favorited_by',
        method='filter_cart_favorite'
    )
    is_in_shopping_cart = BooleanFilter(
        field_name='cart_users',
        method='filter_cart_favorite'
    )
    tags = AllValuesMultipleFilter(field_name='tags__slug')

    def filter_cart_favorite(self, queryset, name, value):
        user = getattr(self.request, 'user', None)
        lookup = name
        if user.is_anonymous or not value:
            return queryset
        return queryset.filter(**{lookup: user})

    class Meta:
        model = Recipe
        fields = ('author', 'tags',)


class IngredientFilter(FilterSet):
    name = CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Ingredient
        fields = ('name',)
