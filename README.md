# Custom Auth System (Test Assignment for Effective Mobile)

Реализация Backend-приложения с кастомной системой аутентификации (JWT) и авторизации (RBAC) без использования стандартных средств Django Auth.

## Стек технологий
- Python 3
- Django + Django Rest Framework (DRF)
- JWT (библиотека `pyjwt`)
- Bcrypt (для хеширования паролей)

## Архитектура безопасности
Реализована модель RBAC (Role-Based Access Control):
1. **CustomUser**: Пользователь с привязкой к Роли.
2. **Role**: Группа прав (например, Admin, User).
3. **Resource**: Объекты системы (например, 'reports').
4. **Permission**: Связь Роль-Ресурс с флагами CRUD (Create, Read, Update, Delete).

## Функционал
- **Регистрация/Логин**: Выдача JWT токенов.
- **Logout**: Инвалидация токенов через метку времени (`last_logout`).
- **Soft Delete**: "Мягкое" удаление аккаунта (флаг `is_deleted`).
- **Middleware-like Decorator**: Кастомный декоратор `@require_auth` для проверки прав доступа к эндпоинтам.

## Установка и запуск

1. **Клонирование и установка зависимостей:**
   ```bash
   pip install -r requirements.txt
   ```
## Применение миграций:

```Bash
python manage.py migrate
```
## Инициализация тестовых данных:
(Создает роли, права и админа admin@example.com / admin123)

```Bash
python manage.py init_data
```
## Запуск сервера:
```Bash
python manage.py runserver
```
## Тестирование
Для проверки доступен пользователь:
Email: admin@example.com
Pass: admin123
Эндпоинт для теста прав: GET /api/reports/ (требует Bearer Token).