# Тарелка — сервис доставки еды

Учебный проект на Django: главная страница, каталог с фильтром категорий, карточка блюда, регистрация и вход, профиль с историей заказов, корзина/оформление и панель управления заказами. Django Admin доступна по адресу `/admin/`.

## Запуск

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
py manage.py migrate
py manage.py createsuperuser
py manage.py runserver
```

После первой миграции в меню автоматически появятся демонстрационные блюда и категории. Добавляйте и редактируйте их через `/admin/`. Чтобы открыть панель заказов `/dashboard/`, администратор должен иметь флаг «Статус персонала».

## Страницы и возможности

| Страница | URL | Доступ |
|---|---|---|
| Главная | `/` | Всем |
| Вход | `/login/` | Всем |
| Регистрация | `/register/` | Гостям |
| Каталог и фильтр категорий | `/menu/` | Всем |
| Детали блюда | `/menu/<slug>/` | Всем |
| Корзина и оформление | `/checkout/` | Оформление — после входа |
| Профиль и заказы | `/profile/` | Авторизованным |
| Управление заказами | `/dashboard/` | Персоналу |
| Админка Django | `/admin/` | Суперпользователям |

Корзина хранится в сессии. Стоимость и количество блюд фиксируются в заказе при оформлении. Для локальной разработки используется SQLite.

## Схема бизнес-логики

```mermaid
flowchart TD
    A[Гость открывает меню] --> B[Выбирает категорию или блюдо]
    B --> C[Открывает страницу блюда]
    C --> D[Добавляет блюдо в корзину]
    D --> E{Вошёл в аккаунт?}
    E -- Нет --> F[Вход или регистрация]
    F --> G[Корзина сохраняется в сессии]
    E -- Да --> G
    G --> H[Указывает адрес и телефон]
    H --> I[Сервер проверяет корзину и цены]
    I --> J[Создаёт заказ и позиции в транзакции]
    J --> K[Очищает корзину, показывает заказ в профиле]
    K --> L[Сотрудник меняет статус заказа]
    L --> M[Клиент видит актуальный статус в профиле]
```

## ER-диаграмма

```mermaid
erDiagram
    AUTH_USER ||--o{ ORDER : places
    CATEGORY ||--o{ PRODUCT : contains
    ORDER ||--|{ ORDER_ITEM : includes
    PRODUCT ||--o{ ORDER_ITEM : references

    AUTH_USER {
        int id PK
        string username
        string email
        string first_name
        boolean is_staff
    }
    CATEGORY {
        int id PK
        string name
        string slug UK
        string description
    }
    PRODUCT {
        int id PK
        int category_id FK
        string name
        string slug UK
        text description
        int price
        string weight
        string image_url
        boolean is_available
        boolean is_popular
    }
    ORDER {
        int id PK
        int user_id FK
        string status
        string address
        string phone
        string comment
        int total
        datetime created_at
    }
    ORDER_ITEM {
        int id PK
        int order_id FK
        int product_id FK
        int quantity
        int price
    }
```
