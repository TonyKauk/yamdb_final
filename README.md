![example workflow](https://github.com/tonykauk/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)

**http://51.250.20.145/redoc/**

# api_yamdb
## Описание
Проект **YaMDb** собирает отзывы пользователей на различные произведения.

## Технологии
- Проект написан на Python 3.8.9
- Использовался Django Framework 2.2.16
- При запуске преокта на сервере используется Gunicorn 20.0.4
- Описаны инструкции для упаковки проекта в контейнеры с примененим Docker

## Запуск проекта

Сборка и запуск контейнеров:
```docker-compose up -d --build```

Выполнение миграций:
```docker-compose exec web python manage.py migrate```

Создание суперползователя:
```docker-compose exec web python manage.py createsuperuser```

Сбор статики:
```docker-compose exec web python manage.py collectstatic --no-input```

Для проверки перейдите по адресу **http://localhost/**

## Автор
Антон Милов

### Алгоритм регистрации пользователей

    1. Пользователь отправляет POST-запрос на добавление нового пользователя с параметрами `email` и `username` на эндпоинт `/api/v1/auth/signup/`.
    2. **YaMDB** отправляет письмо с кодом подтверждения (`confirmation_code`) на адрес  `email`.
    3. Пользователь отправляет POST-запрос с параметрами `username` и `confirmation_code` на эндпоинт `/api/v1/auth/token/`, в ответе на запрос ему приходит `token` (JWT-токен).
    4. При желании пользователь отправляет PATCH-запрос на эндпоинт `/api/v1/users/me/` и заполняет поля в своём профайле (описание полей — в документации).


## Paths

Запросы к API начинаются с `/api/v1/`

**/auth/signup/**

* Получить код подтверждения на переданный `email`.
* Права доступа: Доступно без токена.
  
                email:
                  type: string
                username:
                  type: string

**/auth/token/**

* Получение JWT-токена в обмен на username и confirmation code.
* Права доступа: Доступно без токена.

                username:
                  type: string
                confirmation_code:
                  type: string
                  writeOnly: true

**/categories/**
  
    get:
* Получить список всех категорий
* Права доступа: Доступно без токена.   
    
    
    post:
* Создать категорию
* Права доступа: Администратор.

      required:
      - name
      - slug

**/categories/{slug}/**
  
    delete:
* Удалить категорию
* Права доступа: Администратор.


**/genres/**


    get:
* Получить список всех жанров
* Права доступа: Доступно без токена.   


    post:
* Добавить жанр
* Права доступа: Администратор.

      required:
      - name
      - slug
      

**/genres/{slug}/**


    delete:
* Удалить жанр
* Права доступа: Администратор.


**/titles/**


    get:
* Получить список всех объектов
* Права доступа: Доступно без токена. 


    post:
* Добавить новое произведение
* Права доступа: Администратор.


      required:
        - name
        - year
        - genre
        - category
      properties:
        name:
          type: string
          title: Название
        year:
          type: integer
          title: Год выпуска
        description:
          type: string
          title: Описание
        genre:
          type: array
          items:
            type: string
            title: Slug жанра
        category:
          type: string
          title: Slug категории
          


**/titles/{titles_id}/**


    get:
* Информация о произведении
* Права доступа: Доступно без токена. 


    patch:
* Обновить информацию о произведении
* Права доступа: Администратор.


    delete:
* Удалить произведение
* Права доступа: Администратор.


**/titles/{title_id}/reviews/**


    get:
* Получить список всех отзывов
* Права доступа: Доступно без токена. 


    post:
* Добавить новый отзыв
* Права доступа: Аутентифицированные пользователи.


      required:
          - text
          - score


**/titles/{title_id}/reviews/{review_id}/**


    get:
* Получить отзыв по id для указанного произведения
* Права доступа: Доступно без токена. 


    patch:
* Частично обновить отзыв по id
* Права доступа: Автор отзыва, модератор или администратор.


    delete:
* Удалить отзыв по id
* Права доступа: Автор отзыва, модератор или администратор.


**/titles/{title_id}/reviews/{review_id}/comments/**


    get:
* Получить список всех комментариев к отзыву по id
* Права доступа: Доступно без токена. 


    post:
* Добавить новый комментарий для отзыва
* Права доступа: Аутентифицированные пользователи.


      required:
        - text


**/titles/{title_id}/reviews/{review_id}/comments/{comment_id}/**


    get:
* Получить комментарий для отзыва по id
* Права доступа: Доступно без токена. 


    patch:
* Частично обновить комментарий к отзыву по id
* Права доступа: Автор отзыва, модератор или администратор.


    delete:
* Удалить комментарий к отзыву по id
* Права доступа: Автор отзыва, модератор или администратор.


**/users/**


    get:
* Получить список всех пользователей
* Права доступа: Администратор. 


    post:
* Добавить нового пользователя
* Права доступа: Администратор. 


      required:
      - username
      - email


**/users/{username}/**


    get:
* Получить пользователя по username
* Права доступа: Администратор. 


    patch:
* Изменить данные пользователя по username
* Права доступа: Администратор. 


    delete:
* Удалить пользователя по username
* Права доступа: Администратор. 


**/users/me/**


    get:
* Получить данные своей учетной записи
* Права доступа: Любой авторизованный пользователь. 


    patch:
* Изменить данные своей учетной записи
* Права доступа: Любой авторизованный пользователь. 
