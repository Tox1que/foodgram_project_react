![foodgram workflow](https://github.com/Tox1que/foodgram-project-react/actions/workflows/main.yml/badge.svg)


# Описание сервиса:

Приложение «Продуктовый помощник»: сайт, на котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Сервис «Список покупок» позволит пользователям создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

### Технологии:
- Python,
- Django,
- Django REST framework,
- Gunicorn,
- Nginx,
- Docker,
- PostgreSQL.


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
Установите docker-compose, в этом вам поможет [официальная документация](https://docs.docker.com/compose/install/).

Скопируйте подготовленные файлы docker-compose.yaml и nginx.conf из вашего проекта на сервер в home/<ваш_username>/docker-compose.yaml и home/<ваш_username>/nginx.conf соответственно. 

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
