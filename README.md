# Foodgram

## Описание
Место для обмена полезными и вкусными рецептами.

***

Использованный стек технологий:
- Python
- PostgreSQL
- Django
- Drango REST Framework
- Node Package Manager
- Docker
- Nginx/Gunicorn

***

## Установка
1. Склонируйте содержимое файла `docker-compose.production.yml` на сервер.

2. Создайте файл `.env` с параметрами окружения в той же директории

3. Запустите контейнеры командой:

```
sudo docker compose -f docker-compose.production.yml up -d
```

3. Примените миграции и склонируйте статические файлы для бэкенда командами:

```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/
sudo docker compose -f docker-compose.production.yml exec backend python manage.py csv_import
```

## Примеры запросов

### Просмотр рецептов
Для просмотра списка всех произведений отправьте GET-запрос на `http://127.0.0.1:8000/api/recipes/`.

### 200 Response:
```
Название
Ингредиенты
Автор
Тэги
Время приготовления
Изображение
Способ приготовления
```

### Создание рецептов
Для создания нового отзыва на произведение отправьте POST-запрос на `http://127.0.0.1:8000/api/recipes/` со следующим содержимым:

```
{
  "Ингредиенты": [
    {
      "id": <int>,
      "количество": <int>
    },
  ],
  "Тэги": [
    <id:int>,
  ],
  "Изображение",
  "Название": <str>,
  "Описание": <str>,
  "Время приготовления": <int>
}
```

### Просмотр своей учётной записи пользователя
Для просмотра своей учётной записи отправьте GET-запрос на `http://127.0.0.1:8000/api/users/me/`.

***
