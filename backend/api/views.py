from django.contrib.auth import get_user_model
from django.db.models import Exists, OuterRef, Sum
from django.db.models.query import Prefetch
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   UpdateModelMixin)
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.viewsets import (GenericViewSet, ModelViewSet,
                                     ReadOnlyModelViewSet)

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from users.models import Subscribe

from .filters import IngredientFilter, RecipeFilter
from .permissions import IsAuthorOrReadOnly
from .serializers import (CartFavoriteSerializer, CustomUserSerializer,
                          IngredientSerializer, RecipeCreateUpdateSerializer,
                          RecipeGetSerializer, SubscribeSerializer,
                          SubscriptionsSerializer, TagSerializer)

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    serializer_class = CustomUserSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = User.objects.all()
        if user.is_anonymous:
            return queryset
        return queryset.annotate(
            is_subscribed=Exists(
                user.subscriber.filter(author=OuterRef('pk')))
        )

    @action(['get', 'put', 'patch', 'delete'], detail=False,
            permission_classes=[IsAuthenticated])
    def me(self, request, *args, **kwargs):
        return super().me(request, *args, **kwargs)

    @action(permission_classes=[IsAuthenticated],
            detail=False, methods=['get'])
    def subscriptions(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.filter(
            subscription__user=self.request.user
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = SubscriptionsSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = SubscriptionsSerializer(queryset, many=True)
        return Response(serializer.data)


class RecipeViewSet(ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        queryset = (Recipe.objects.all().prefetch_related('tags').
                    prefetch_related(
                        Prefetch('recipe_ingredients',
                                 queryset=RecipeIngredient.objects.
                                 select_related('ingredient'))))
        user = self.request.user
        if user.is_anonymous:
            return queryset.prefetch_related('author')

        subqueryset = User.objects.annotate(is_subscribed=Exists(
            Subscribe.objects.filter(user=user,
                                     author=OuterRef('pk')))).all()
        queryset = queryset.prefetch_related(
            Prefetch('author', queryset=subqueryset)
        )
        return queryset.annotate(
            is_in_shopping_cart=Exists(
                Recipe.objects.filter(
                    cart_users=user, pk=OuterRef('pk'))),
            is_favorited=Exists(
                Recipe.objects.filter(
                    pk=OuterRef('pk'),
                    favorited_by=user)))

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeGetSerializer
        return RecipeCreateUpdateSerializer

    @action(permission_classes=[IsAuthenticated], detail=False)
    def download_shopping_cart(self, request):
        user = request.user
        qs = RecipeIngredient.objects.filter(recipe__cart_users=user)
        RecipeIngredient.objects.select_related(
            'recipe', 'ingredient').filter(recipe__cart_users=user)
        data = qs.values_list('ingredient__name',
                              'ingredient__measurement_unit'
                              ).annotate(total=Sum('amount'))
        ingredients = [f'{name} - {amount}{str(unit)} \n'
                       for name, unit, amount in data]
        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = ('attachment;'
                                           'filename="Ingredients.txt"')
        response.writelines(ingredients)
        return response


class UpdateViewSet(UpdateModelMixin, GenericViewSet):

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        if request.method == 'DELETE':
            return Response(status=status.HTTP_204_NO_CONTENT)
        return response


class CartFavoriteViewSet(UpdateViewSet):
    queryset = Recipe.objects.all()
    serializer_class = CartFavoriteSerializer


class CreateDestroyViewSet(CreateModelMixin,
                           DestroyModelMixin, GenericViewSet):

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        assert lookup_url_kwarg in self.kwargs, (
            (self.__class__.__name__, lookup_url_kwarg)
        )
        user = self.request.user
        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = get_object_or_404(queryset, user=user,
                                author__pk=filter_kwargs['pk'])
        return obj


class SubscribeViewSet(CreateDestroyViewSet):
    queryset = Subscribe.objects.all()
    serializer_class = SubscribeSerializer
    permission_classes = (IsAuthenticated,)


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None
