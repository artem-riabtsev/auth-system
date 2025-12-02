# Custom Authentication & Authorization System

Проект реализует собственную систему аутентификации и авторизации на Django + DRF + PostgreSQL с JWT токенами согласно ТЗ.

## Схема базы данных

### Основные таблицы:
1. **users_user** - Пользователи
   - `email` (уникальный), `first_name`, `last_name`, `middle_name`
   - `password` (bcrypt хеш), `is_active`, `roles` (ManyToMany)
   
2. **permissions_role** - Роли
   - `name` (Администратор, Менеджер, Пользователь, Гость)
   - `is_default` (роль по умолчанию для новых пользователей)
   
3. **permissions_businesselement** - Бизнес-элементы
   - `code`: `users`, `products`, `stores`, `orders`, `permissions`
   
4. **permissions_permissiontype** - Типы разрешений
   - `code`: `read`, `create`, `update`, `delete`
   
5. **permissions_accessrule** - Правила доступа
   - `scope`: `NONE` (нет доступа), `OWN` (только свои), `ALL` (все)

## Быстрый старт

### Требования
- Python 3.10+
- Docker и Docker Compose

### Установка
```bash
# 1. Клонировать репозиторий
git clone <your-repo>
cd auth_system_project

# 2. Настроить окружение
cp .env.example .env

# 3. Запустить PostgreSQL в Docker
docker-compose up -d

# 4. Установить зависимости
pip install -r requirements.txt

# 5. Применить миграции
python manage.py migrate

# 6. Загрузить тестовые данные
python manage.py load_permissions_data

# 7. Создать суперпользователя
python manage.py createsuperuser

# 8. Запустить сервер
python manage.py runserver
```
## API Endpoints

### Аутентификация
```bash
POST /api/auth/register/ - Регистрация нового пользователя

POST /api/auth/login/ - Вход (получение JWT токенов)

POST /api/auth/logout/ - Выход

GET /api/auth/profile/ - Профиль текущего пользователя

DELETE /api/auth/delete-account/ - Мягкое удаление аккаунта
```

###Проверка прав
```bash
GET /api/permissions/check-permissions/ - Получить все права текущего пользователя

GET /api/permissions/test-permission/ - Тестовый endpoint для проверки права read на users
```


### Админка (только для администраторов)
```bash
GET/POST/PUT/DELETE /api/admin/permissions/roles/ - Управление ролями

GET/POST/PUT/DELETE /api/admin/permissions/elements/ - Управление бизнес-элементами

GET/POST/PUT/DELETE /api/admin/permissions/permission-types/ - Управление типами разрешений

GET/POST/PUT/DELETE /api/admin/permissions/rules/ - Управление правилами доступа
```

### Демонстрационные бизнес-объекты
```bash
GET /api/business/products/ - Список товаров (фильтрация по правам)

GET /api/business/orders/ - Список заказов (фильтрация по правам)

GET /api/business/stores/ - Список магазинов
```

## Тестирование системы

- 401 Unauthorized - если пользователь не аутентифицирован
- 403 Forbidden - если пользователь аутентифицирован, но нет прав
- Фильтрация по scope (OWN/ALL) работает корректно
- Разные роли получают разный доступ к ресурсам

### Примеры тестов:

```bash
# 1. 401 ошибка (без токена)
curl http://localhost:8000/api/business/products/

# 2. 403 ошибка (есть токен, но нет прав)
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/business/stores/

# 3. Успешный доступ
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/business/products/
```

## Роли и права доступа

### Гость
read на products и stores (scope=ALL)

### Пользователь (роль по умолчанию)
read, create, update, delete на users, products, orders (scope=OWN)

### Менеджер
read на все элементы (scope=ALL)
create, update на products и orders (scope=ALL)

### Администратор
Полный доступ ко всем операциям на все элементы (scope=ALL)

## Технологии
- Backend: Django 5.2, Django REST Framework
- Database: PostgreSQL 15 (в Docker)
- Authentication: JWT токены (access/refresh), bcrypt для паролей
- Authorization: Кастомная RBAC система с scope (NONE/OWN/ALL)

## Структура проекта
```bash
auth_system_project/
├── auth_system/          # Настройки Django
├── users/               # Модуль пользователей (аутентификация)
├── permissions/         # Система ролей и разрешений
├── business/           # Mock бизнес-объекты для демонстрации
├── docker-compose.yml  # Конфигурация PostgreSQL
└── requirements.txt    # Зависимости Python
```

## Особенности реализации
- Кастомная модель User с email вместо username
- Bcrypt хеширование паролей (не Django стандартное)
- JWT токены с access/refresh механикой
- Middleware для обработки 401 ошибок
- Мягкое удаление пользователей (is_active=False)
- Автоматическое назначение роли по умолчанию при регистрации