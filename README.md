![foodgram workflow](https://github.com/Tox1que/foodgram/actions/workflows/main.yml/badge.svg?event=push)


# Описание сервиса:

Приложение «Продуктовый помощник»: сайт, на котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Сервис «Список покупок» позволит пользователям создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## Технологии
[![Python](https://img.shields.io/badge/Python-3776AB?logo=python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-092E20?&logo=django)](https://www.djangoproject.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-grey?logo=postgresql)](https://www.postgresql.org/)
[![Django REST Framework](https://img.shields.io/badge/Django_REST_Framework-grey?logo=django)](https://www.django-rest-framework.org/)
[![Gunicorn](https://img.shields.io/badge/Gunicorn-grey?logo=gunicorn)](https://gunicorn.org/)
[![nginx](https://img.shields.io/badge/nginx-grey?logo=nginx)](https://nginx.org/)
[![Docker](https://img.shields.io/badge/Docker-grey?logo=docker)](https://www.docker.com/)
[![Docker Compose](https://img.shields.io/badge/Docker_Compose-grey?logo=docker)](https://docs.docker.com/compose/)
[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-grey?logo=githubactions)](https://github.com/features/actions)


## Как запустить проект на удалённом сервере:
Добавьте в Secrets GitHub Actions следующие переменные окружения:
```
USER=<имя пользователя для подключения к серверу>
HOST=<IP-адрес вашего сервера>
SSH_KEY=<приватный ключ с компьютера, имеющего доступ к боевому серверу>
PASSPHRASE=<если при создании ssh-ключа вы использовали фразу-пароль>
SECRET_KEY=<секретный ключ проекта>
ALLOWED_HOSTS=<список хостов (указывать через пробел)>
DEBUG=<1 - для значения True, 0 - для значения False>
DB_NAME=<имя базы данных>
POSTGRES_USER=<логин для подключения к базе данных>
POSTGRES_PASSWORD=<пароль для подключения к БД>
DB_HOST=<название сервиса (контейнера)>
DB_PORT=<порт для подключения к БД>
DOCKER_USERNAME=<DockerHub имя пользователя>
DOCKER_PASSWORD=<DockerHub пароль>
TELEGRAM_TO=<ID вашего телеграм-аккаунта>
TELEGRAM_TOKEN=<токен вашего бота>
```
Установите docker:
```
sudo apt install docker.io
```
Установите docker-compose, в этом вам поможет [официальная документация](https://docs.docker.com/compose/install/standalone/).

Скопируйте подготовленные файлы docker-compose.yaml и nginx.conf из вашего проекта (директория infra) на сервер в home/<ваш_username>/docker-compose.yaml и home/<ваш_username>/nginx.conf соответственно.

При пуше в ветку main код автоматически деплоится на сервер.

Создайте и примените миграции:
```
sudo docker-compose exec backend python manage.py makemigrations
sudo docker-compose exec backend python manage.py migrate --noinput
```
Соберите статику:
```
sudo docker-compose exec backend python manage.py collectstatic --no-input
```
Наполните базу данных содержимым файла ingredients.csv:
```
sudo docker-compose exec backend python manage.py load_data
```
Создайте суперпользователя:
```
sudo docker-compose exec backend python manage.py createsuperuser
```
В админ-зоне добавьте теги к рецептам.
