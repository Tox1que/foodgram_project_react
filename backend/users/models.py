from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.db.models import CheckConstraint, F, Q, UniqueConstraint


class UserManager(BaseUserManager):
    def create_user(self, username, first_name,
                    last_name, email, password=None):
        if not email:
            raise ValueError('Укажите ваш email адрес')
        if not first_name:
            raise ValueError('Укажите имя')
        if not first_name:
            raise ValueError('Укажите фамилию')
        if not password:
            raise ValueError('Введите пароль')
        user = self.model(
            username=username,
            first_name=first_name, last_name=last_name,
            email=self.normalize_email(email)
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, first_name,
                         last_name, email, password=None):
        user = self.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractUser):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(max_length=254, unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    shopping_cart = models.ManyToManyField(
        'recipes.Recipe', blank=True, through='ShoppingCart',
        verbose_name='Список покупок', related_name='cart_users'
    )
    favorites = models.ManyToManyField(
        'recipes.Recipe', blank=True, through='Favorite',
        verbose_name='Избранное', related_name='favorited_by'
    )
    recipes_count = models.PositiveSmallIntegerField(
        default=0, verbose_name='Количество рецептов пользователя', blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    objects = UserManager()

    def __str__(self):
        return self.username

    class Meta:
        ordering = ['-id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Subscribe(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Подписчики', related_name='subscriber'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Подписки', related_name='subscription'
    )
    created = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} подписан на {self.author}'

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('user', 'author'),
                name='prevent_duplicate_subscriptions'
            ),
            CheckConstraint(
                check=~Q(user=F('author')),
                name='prevent_self_subscribe',
            ),
        ]
        ordering = ['-created']
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'


class Favorite(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        'recipes.Recipe', on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    def __str__(self):
        return f'{self.recipe} в избранном у {self.user}'

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('user', 'recipe'),
                name='prevent_duplicates_in_favorites'
            ),
        ]
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        'recipes.Recipe', on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    def __str__(self):
        return f'{self.recipe} в списке покупок {self.user}'

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('user', 'recipe'),
                name='prevent_duplicates_in_cart'
            ),
        ]
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
