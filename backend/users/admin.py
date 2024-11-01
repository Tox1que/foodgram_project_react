from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .models import Favorite, ShoppingCart, Subscribe

User = get_user_model()


class UserSubscriberInLine(admin.TabularInline):
    model = Subscribe
    extra = 1
    fk_name = 'user'


class UserSubscriptionInLine(admin.TabularInline):
    model = Subscribe
    extra = 1
    fk_name = 'author'


class UserFavoritesThroghInLine(admin.TabularInline):
    model = User.favorites.through
    extra = 1
    verbose_name = 'Избранное'
    verbose_name_plural = 'Избранное'


class UserShoppingCartThroghInLine(admin.TabularInline):
    model = User.shopping_cart.through
    extra = 1
    verbose_name = 'Список покупок'
    verbose_name_plural = 'Списки покупок'


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe',)
    search_fields = ('recipe__name',)
    list_filter = ('user', 'recipe',)


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe',)
    search_fields = ('recipe__name',)
    list_filter = ('user', 'recipe',)

class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author',)
    search_fields = ('user_username',)
    list_filter = ('user', 'author',)

class CustomUserAdmin(UserAdmin):
    inlines = (UserFavoritesThroghInLine, UserShoppingCartThroghInLine,
               UserSubscriberInLine, UserSubscriptionInLine,)
    search_fields = ('username', 'email',)
    list_filter = ('username', 'email',)
    empty_value_display = '-пусто-'


admin.site.register(User, CustomUserAdmin)
admin.site.register(Subscribe, SubscribeAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
