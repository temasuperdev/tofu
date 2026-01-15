# Техническая спецификация микросервисного приложения заметок

## 1. Обзор системы

Приложение представляет собой микросервисную систему для управления заметками, состоящую из:
- Frontend: Vue.js одностраничное приложение
- Backend: FastAPI REST API
- Database: PostgreSQL
- Infrastructure: k3s cluster с Traefik ingress controller

## 2. Функциональные требования

### 2.1. Основные функции
- Создание новых заметок
- Чтение списка заметок и отдельных заметок
- Обновление существующих заметок
- Удаление заметок
- Аутентификация и авторизация пользователей
- Поиск и фильтрация заметок

### 2.2. Нефункциональные требования
- Безопасность: HTTPS, защита от XSS/CSRF, валидация входных данных
- Масштабируемость: возможность горизонтального масштабирования
- Отказоустойчивость: репликация базы данных, здоровые проверки
- Производительность: быстрая загрузка интерфейса и ответов API
- Надежность: резервное копирование данных

## 3. Технологический стек

### 3.1. Backend (FastAPI)
- Язык: Python 3.9+
- Фреймворк: FastAPI
- ORM: SQLAlchemy
- Валидация: Pydantic
- Аутентификация: JWT
- Миграции: Alembic
- Тестирование: pytest

### 3.2. Frontend (Vue.js)
- Фреймворк: Vue.js 3
- Состояние: Pinia
- Роутинг: Vue Router
- Стили: Tailwind CSS или SCSS
- HTTP клиент: Axios

### 3.3. База данных
- СУБД: PostgreSQL 13+
- Хранение: Persistent Volumes в k3s
- Миграции: Alembic

### 3.4. Контейнеризация и оркестрация
- Контейнеры: Docker
- Оркестрация: Kubernetes (k3s)
- Сеть: Traefik ingress controller
- CI/CD: GitHub Actions

## 4. Архитектура API

### 4.1. Основные эндпоинты

#### Аутентификация
```
POST /auth/register - регистрация пользователя
POST /auth/login - вход пользователя
POST /auth/logout - выход пользователя
GET /auth/me - получение информации о текущем пользователе
```

#### Заметки
```
GET /api/notes - получить все заметки пользователя
GET /api/notes/{id} - получить конкретную заметку
POST /api/notes - создать новую заметку
PUT /api/notes/{id} - обновить заметку
DELETE /api/notes/{id} - удалить заметку
```

### 4.2. Структура данных

#### Пользователь
```json
{
  "id": "uuid",
  "username": "string",
  "email": "string",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

#### Заметка
```json
{
  "id": "uuid",
  "title": "string",
  "content": "text",
  "user_id": "uuid",
  "created_at": "datetime",
  "updated_at": "datetime",
  "is_public": "boolean"
}
```

## 5. Структура проекта

```
notes-app/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── v1/
│   │   │   │   ├── auth.py
│   │   │   │   ├── notes.py
│   │   │   │   └── users.py
│   │   │   └── __init__.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── note.py
│   │   │   └── __init__.py
│   │   ├── schemas/
│   │   │   ├── user.py
│   │   │   ├── note.py
│   │   │   └── token.py
│   │   ├── database/
│   │   │   ├── session.py
│   │   │   └── __init__.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── __init__.py
│   │   ├── utils/
│   │   │   └── __init__.py
│   │   └── main.py
│   ├── migrations/
│   ├── tests/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── alembic.ini
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── views/
│   │   ├── router/
│   │   ├── store/
│   │   ├── services/
│   │   ├── assets/
│   │   └── App.vue
│   ├── public/
│   ├── tests/
│   ├── package.json
│   ├── Dockerfile
│   └── vue.config.js
├── k8s/
│   ├── namespace.yaml
│   ├── postgres/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   ├── pvc.yaml
│   │   └── secret.yaml
│   ├── backend/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   └── configmap.yaml
│   ├── frontend/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   └── configmap.yaml
│   └── ingress.yaml
├── .github/workflows/
│   ├── ci.yml
│   └── cd.yml
├── docker-compose.yml
├── .gitignore
└── README.md
```

## 6. Безопасность

### 6.1. Аутентификация
- JWT токены с ограниченным сроком действия
- Refresh токены для продления сессии
- Хэширование паролей с помощью bcrypt

### 6.2. Авторизация
- Проверка токенов на каждом защищенном эндпоинте
- Разграничение доступа к заметкам других пользователей

### 6.3. Защита от атак
- Валидация всех входных данных
- Защита от SQL-инъекций через ORM
- Защита от XSS через контекстное экранирование

## 7. Масштабируемость и отказоустойчивость

### 7.1. Масштабируемость
- Stateless backend сервисы для легкого масштабирования
- Горизонтальное масштабирование через Kubernetes ReplicaSets
- Connection pooling для базы данных

### 7.2. Отказоустойчивость
- Репликация PostgreSQL
- Health checks для сервисов
- Backup стратегия для данных

## 8. CI/CD Pipeline

### 8.1. CI этапы
- Запуск юнит-тестов
- Проверка кода (linting)
- Сборка Docker образов
- Запуск интеграционных тестов

### 8.2. CD этапы
- Push образов в registry
- Обновление Kubernetes манифестов
- Zero-downtime деплоймент
- Rollback в случае проблем