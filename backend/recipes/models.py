from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(verbose_name='Название ингредиента',
                            max_length=256, db_index=True)
    measurement_unit = models.CharField(max_length=50,
                                        verbose_name='Единица измерения')

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50,
                            verbose_name='Тег', unique=True)
    color = models.CharField(max_length=7,
                             verbose_name='Цвет', unique=True)
    slug = models.SlugField(max_length=50,
                            verbose_name='Слаг', unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.slug


class Recipe(models.Model):
    author = models.ForeignKey(User, verbose_name='Автор',
                               on_delete=models.CASCADE,
                               related_name='recipes')
    name = models.CharField(max_length=200, unique=True,
                            verbose_name='Название')
    text = models.TextField(max_length=1500, verbose_name='Описание рецепта')
    tags = models.ManyToManyField(Tag, related_name='recipe',
                                  verbose_name='Теги', through='RecipeTag')
    ingredients = models.ManyToManyField(Ingredient,
                                         through='RecipeIngredient',
                                         verbose_name='Ингредиенты')
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Время приготовления'
    )
    image = models.ImageField(upload_to='recipes/',
                              verbose_name='Изображение')
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='Дата публикации')

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey('Recipe', on_delete=models.CASCADE,
                               verbose_name='Рецепт',
                               related_name='recipe_ingredients')
    ingredient = models.ForeignKey('Ingredient', on_delete=models.CASCADE,
                                   verbose_name='Ингредиент',
                                   related_name='ingredient_recipes')
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество ингредиента',
        validators=[MinValueValidator(1)]
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='prevent_duplicate_ingredients',
            ),
        ]
        verbose_name = 'Информация об ингредиенте в рецепте'
        verbose_name_plural = 'Информация об ингредиентах в рецептах'

    def __str__(self):
        return (f'{self.ingredient}'
                f' {self.amount}{self.ingredient.measurement_unit}'
                f' в {self.recipe}')


class RecipeTag(models.Model):
    recipe = models.ForeignKey('Recipe', on_delete=models.CASCADE,
                               verbose_name='Рецепт')
    tag = models.ForeignKey('Tag', on_delete=models.CASCADE,
                            verbose_name='Тег')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'tag'),
                name='prevent_duplicate_tags',
            ),
        ]
        verbose_name = 'Тег к рецепту'
        verbose_name_plural = 'Теги к рецептам'

    def __str__(self):
        return f'Тег {self.tag} к рецепту "{self.recipe}"'
