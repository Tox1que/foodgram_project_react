from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CartFavoriteViewSet, CustomUserViewSet, IngredientViewSet,
                    RecipeViewSet, SubscribeViewSet, TagViewSet)

router = DefaultRouter()
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('ingredients', IngredientViewSet)
router.register('tags', TagViewSet)
router.register('users', CustomUserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
    path('recipes/<int:pk>/favorite/', CartFavoriteViewSet.as_view(
        {'get': 'partial_update', 'delete': 'partial_update'}),
        name='favorites'),
    path('recipes/<int:pk>/shopping_cart/', CartFavoriteViewSet.as_view(
        {'get': 'partial_update', 'delete': 'partial_update'}),
        name='shopping_cart'),
    path('users/<int:pk>/subscribe/',
         SubscribeViewSet.as_view({'get': 'create',
                                   'delete': 'destroy'})),
]
