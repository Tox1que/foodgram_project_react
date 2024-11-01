from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework.fields import (BooleanField, CharField, CurrentUserDefault,
                                   EmailField, HiddenField, ReadOnlyField)
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import (IntegerField, ModelSerializer,
                                        ValidationError)
from rest_framework.validators import UniqueValidator

from recipes.models import Ingredient, Recipe, RecipeIngredient, RecipeTag, Tag
from users.models import Subscribe

from .fields import CustomIntegerField

User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):
    username = CharField(
        validators=[
            UniqueValidator(queryset=User.objects.all(),
                            message='Это имя пользователя недоступно')
        ]
    )
    email = EmailField(
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message='Пользователь с таким email уже существует')
        ]
    )


class CustomUserSerializer(UserSerializer):
    is_subscribed = BooleanField(read_only=True, default=False)

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed',)


class TagSerializer(ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class RecipeIngredientSerializer(ModelSerializer):
    id = ReadOnlyField(source='ingredient.id')
    name = ReadOnlyField(source='ingredient.name')
    measurement_unit = ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'amount', 'measurement_unit')


class IngredientSerializer(ModelSerializer):
    amount = CustomIntegerField(write_only=True)
    id = IntegerField(read_only=False)

    class Meta:
        model = Ingredient
        fields = ('id', 'amount', 'name', 'measurement_unit')
        read_only_fields = ('name', 'measurement_unit',)


class RecipeGetSerializer(ModelSerializer):
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientSerializer(source='recipe_ingredients',
                                             many=True)
    author = CustomUserSerializer()
    is_in_shopping_cart = BooleanField(read_only=True, default=False)
    is_favorited = BooleanField(read_only=True, default=False)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'text',
                  'image', 'cooking_time',)


class RecipeCreateUpdateSerializer(ModelSerializer):
    author = HiddenField(default=CurrentUserDefault())
    tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                  many=True)
    ingredients = IngredientSerializer(many=True)
    image = Base64ImageField(max_length=None, use_url=True)

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'tags', 'name', 'text', 'image',
                  'cooking_time', 'ingredients',)
        read_only_fields = ('author',)
        extra_kwargs = {
            'name': {
                'validators': [UniqueValidator(
                    queryset=Recipe.objects.all(),
                    message='Рецепт с таким названием уже существует'
                )]
            },
            'cooking_time': {
                'min_value': 1,
                'error_messages': {
                    'min_value':
                    'Время приготовления не должно быть менее 1 минуты!'
                }
            },
        }

    def to_representation(self, instance):
        serializer = RecipeGetSerializer(instance, context=self.context)
        return serializer.data

    def validate_tags(self, value):
        if not value:
            raise ValidationError(
                'Добавьте теги!'
            )
        if len(value) != len(set(value)):
            raise ValidationError('Теги не должны повторяться!')
        return value

    def validate_ingredients(self, value):
        quantity = len(value)
        if quantity == 0:
            raise ValidationError(
                'Добавьте список ингредиентов!'
            )

        cleaned = set()
        try:
            for ingredient in value:
                if int(ingredient['amount']) < 1:
                    raise ValidationError(
                        'Количество ингредиента не должно быть менее 1!')
                cleaned.add(ingredient['id'])
        except (ValueError, TypeError):
            raise ValidationError(
                'Количество ингредиента должно быть целым числом!')

        if quantity != len(cleaned):
            raise ValidationError(
                'Ингредиенты в рецепте не должны повторяться!')
        return value

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        recipe_ingredients = [RecipeIngredient(
            recipe=recipe,
            ingredient=get_object_or_404(Ingredient,
                                         id=ingredient['id']),
            amount=ingredient['amount'])
            for ingredient in ingredients]
        RecipeIngredient.objects.bulk_create(recipe_ingredients)
        return recipe

    def update(self, instance, validated_data):
        if 'tags' in validated_data:
            tags = validated_data.pop('tags')
            RecipeTag.objects.filter(recipe=instance).delete()
            instance.tags.add(*tags)
        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
            RecipeIngredient.objects.filter(recipe=instance).delete()
            new_ingredients = [RecipeIngredient(
                recipe=instance,
                ingredient=get_object_or_404(Ingredient, pk=ingredient['id']),
                amount=ingredient['amount']) for ingredient in ingredients]
            RecipeIngredient.objects.bulk_create(new_ingredients)
        return super().update(instance, validated_data)


class CartFavoriteSerializer(ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'cooking_time', 'image',)
        read_only_fields = ('name', 'cooking_time', 'image',)

    def validate(self, data):
        request = self.context['request']
        if request.method == 'GET':
            attr = request.resolver_match.url_name
            user = request.user
            pk = self.context['view'].kwargs.get('pk')
            attr_msg = {'favorites': 'избранное',
                        'shopping_cart': 'список покупок'}
            if getattr(user, attr).filter(pk=pk).exists():
                raise ValidationError(
                    f'Рецепт уже был добавлен в {attr_msg[attr]}!')
        return data

    def update(self, instance, validated_data):
        request = self.context['request']
        attr = request.resolver_match.url_name
        user = request.user
        if request.method == 'GET':
            getattr(user, attr).add(instance)
        else:
            getattr(user, attr).remove(instance)
        return instance


class SubscriptionsSerializer(ModelSerializer):
    recipes = CartFavoriteSerializer(read_only=True, many=True)
    is_subscribed = BooleanField(read_only=True, default=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count',)


class SubscribeSerializer(ModelSerializer):
    user = HiddenField(default=CurrentUserDefault())

    class Meta:
        model = Subscribe
        fields = ('user', 'author')
        read_only_fields = ('user', 'author',)

    def validate(self, data):
        user = self.context['request'].user
        pk = self.context['view'].kwargs.get('pk')
        if user.pk == pk:
            raise ValidationError(
                'Подписываться на самого себя запрещено!')
        if user.subscriber.filter(author__pk=pk).exists():
            raise ValidationError(
                'Вы уже подписаны на этого пользователя!')
        data['author'] = get_object_or_404(User, pk=pk)
        return data

    def to_representation(self, instance):
        author = instance.author
        serializer = SubscriptionsSerializer(author, context=self.context)
        return serializer.data
