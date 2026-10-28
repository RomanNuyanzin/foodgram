# Foodgram

**Foodgram** — это веб-приложение для публикации рецептов.  
Пользователи могут регистрироваться, публиковать рецепты, добавлять их в избранное, формировать список покупок, подписываться на авторов и скачивать список ингредиентов для выбранных рецептов.

---

## Автор

**ФИО:** Нуянзин Роман
**GitHub:** [Roman Nuyanzin GitHub](https://github.com/RomanNuyanzin/foodgram)
**Email:** jilberty@bk.ru

---

## Стек технологий

- Python
- Django
- Django REST Framework
- Djoser
- Gunicorn
- React
- PostgreSQL
- Docker
- Docker Compose
- Nginx

---

## Возможности проета

- регистрация и авторизация пользователей;
- публикация, редактирование и удаление рецептов;
- загрузка изображений рецептов;
- добавление рецептов в избранное;
- добавление рецептов в список покупок;
- скачивание списка покупок в формате `.txt`;
- подписка на авторов;
- фильтрация рецептов по тегам;
- смена аватара пользователя;
- короткая ссылка на рецепт;
- административная панель Django.

---

## Структура проекта

```text
foodgram/
├── backend/
├── frontend/
├── infra/
├── data/
├── docs/
└── README.md

---

## Локальное развёртывание проекта через Docker

### 1. Клонировать репозиторий

git clone https://github.com/RomanNuyanzin/foodgram.git

### 2. Создать файл .env

Пример содержимого файла .env:

POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
DB_HOST=db
DB_PORT=5432
SECRET_KEY=secret-key
DEBUG=False
ALLOWED_HOSTS=127.0.0.1,localhost


### 3. Запустить контейнеры

Из директории infra:
docker compose up -d --build

### 4. Выполнить миграции

docker compose exec backend python manage.py migrate

### 5. Собрать статику

docker compose exec backend python manage.py collectstatic --noinput

### 6. Загрузить ингредиенты в базу данных

docker compose exec backend python manage.py load_ingredients

### 7. Создать суперпользователя

docker compose exec backend python manage.py createsuperuser

### Адреса проекта

Локальные адреса проекта:
- Главная страница: http://localhost/foodgram/
- Админ-панель: http://localhost/foodgram/admin/
- API: http://localhost/foodgram/api/
- Документация API: http://localhost/foodgram/api/docs/
- Данные для входа в Django-admin
- Логин: admin@admin.ru
- Пароль: 123admin!!!
- Адрес проекта https://jyhost.zapto.org/foodgram/ - в данный момент не поддерживается

---

### Полезные команды

- Остановить контейнеры

docker compose down

- Перезапустить контейнеры

docker compose up -d

- Посмотреть логи

docker compose logs -f

- Проверить список контейнеров

docker compose ps
