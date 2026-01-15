# Стратегия тестирования для микросервисного приложения заметок

## 1. Общая стратегия тестирования

Приложение будет протестировано по нескольким уровням:
- Модульное тестирование (Unit tests)
- Интеграционное тестирование (Integration tests)
- E2E тестирование (End-to-end tests)
- Тестирование безопасности
- Нагрузочное тестирование

## 2. Модульное тестирование (Backend)

### 2.1. Инструменты
- pytest для написания тестов
- pytest-mock для мокирования зависимостей
- coverage для измерения покрытия кода

### 2.2. Примеры тестов
```python
# tests/test_models.py
import pytest
from app.models.note import Note
from app.models.user import User

def test_create_note():
    note = Note(title="Test Note", content="Test Content", user_id=1)
    assert note.title == "Test Note"
    assert note.content == "Test Content"
    assert note.user_id == 1

def test_update_note():
    note = Note(title="Original Title", content="Original Content", user_id=1)
    note.title = "Updated Title"
    note.content = "Updated Content"
    assert note.title == "Updated Title"
    assert note.content == "Updated Content"

# tests/test_api.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_note_endpoint():
    response = client.post("/api/notes/", json={
        "title": "Test Note",
        "content": "Test Content"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Note"
    assert data["content"] == "Test Content"
```

### 2.3. Запуск тестов
```bash
# Запуск всех тестов
pytest tests/

# Запуск с измерением покрытия
pytest tests/ --cov=app --cov-report=html

# Запуск только модульных тестов
pytest tests/unit/
```

## 3. Интеграционное тестирование

### 3.1. Тестирование API с реальной базой данных
```python
# conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.session import Base
from app.main import app
from fastapi.testclient import TestClient

@pytest.fixture(scope="session")
def test_db():
    engine = create_engine("sqlite:///./test.db")
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    yield TestingSessionLocal()
    engine.dispose()

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

# tests/integration/test_note_crud.py
def test_full_note_lifecycle(client, test_db):
    # Создание пользователя
    user_response = client.post("/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword"
    })
    assert user_response.status_code == 200
    
    # Аутентификация
    auth_response = client.post("/auth/login", data={
        "username": "test@example.com",
        "password": "testpassword"
    })
    assert auth_response.status_code == 200
    token = auth_response.json()["access_token"]
    
    # Создание заметки
    headers = {"Authorization": f"Bearer {token}"}
    create_response = client.post("/api/notes/", json={
        "title": "Integration Test Note",
        "content": "This is an integration test note",
        "is_public": False
    }, headers=headers)
    assert create_response.status_code == 200
    note_id = create_response.json()["id"]
    
    # Чтение заметки
    read_response = client.get(f"/api/notes/{note_id}", headers=headers)
    assert read_response.status_code == 200
    assert read_response.json()["title"] == "Integration Test Note"
    
    # Обновление заметки
    update_response = client.put(f"/api/notes/{note_id}", json={
        "title": "Updated Integration Test Note",
        "content": "Updated content",
        "is_public": True
    }, headers=headers)
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Updated Integration Test Note"
    
    # Удаление заметки
    delete_response = client.delete(f"/api/notes/{note_id}", headers=headers)
    assert delete_response.status_code == 200
```

## 4. Тестирование Frontend

### 4.1. Инструменты
- Vue Test Utils для тестирования компонентов
- Jest для юнит-тестирования
- Cypress для E2E тестирования

### 4.2. Тестирование компонентов
```javascript
// tests/unit/components/NoteItem.spec.js
import { mount } from '@vue/test-utils'
import NoteItem from '@/components/NoteItem.vue'

describe('NoteItem.vue', () => {
  const mockNote = {
    id: 1,
    title: 'Test Note',
    content: 'Test Content',
    created_at: '2023-01-01T00:00:00Z'
  }

  it('renders note correctly', () => {
    const wrapper = mount(NoteItem, {
      props: { note: mockNote }
    })

    expect(wrapper.find('.note-title').text()).toBe('Test Note')
    expect(wrapper.find('.note-content').text()).toBe('Test Content')
  })

  it('emits delete event when delete button clicked', async () => {
    const wrapper = mount(NoteItem, {
      props: { note: mockNote }
    })

    await wrapper.find('.delete-btn').trigger('click')
    expect(wrapper.emitted('delete')).toBeTruthy()
  })
})
```

### 4.3. E2E тестирование с Cypress
```javascript
// cypress/e2e/notes.cy.js
describe('Notes Application', () => {
  beforeEach(() => {
    cy.visit('/')
  })

  it('should allow creating a new note', () => {
    cy.intercept('POST', '/api/notes/').as('createNote')
    
    cy.get('[data-cy=new-note-form]').within(() => {
      cy.get('[data-cy=title-input]').type('My New Note')
      cy.get('[data-cy=content-textarea]').type('This is the content of my note.')
      cy.get('[data-cy=submit-btn]').click()
    })
    
    cy.wait('@createNote').then((interception) => {
      expect(interception.response.statusCode).to.eq(200)
    })
    
    cy.contains('My New Note').should('be.visible')
  })

  it('should allow viewing existing notes', () => {
    cy.intercept('GET', '/api/notes/*').as('getNotes')
    
    cy.visit('/notes')
    cy.wait('@getNotes')
    
    cy.get('[data-cy=note-item]').should('have.length.greaterThan', 0)
  })
})
```

## 5. Тестирование безопасности

### 5.1. Проверка авторизации
```python
# tests/security/test_auth.py
def test_unauthorized_access_to_protected_endpoint():
    response = client.get("/api/notes/")
    assert response.status_code == 401

def test_access_to_other_users_note():
    # Создаем двух пользователей
    user1_response = client.post("/auth/register", json={
        "username": "user1",
        "email": "user1@example.com",
        "password": "password1"
    })
    user2_response = client.post("/auth/register", json={
        "username": "user2",
        "email": "user2@example.com",
        "password": "password2"
    })
    
    # Пользователь 1 создает заметку
    auth1_response = client.post("/auth/login", data={
        "username": "user1@example.com",
        "password": "password1"
    })
    token1 = auth1_response.json()["access_token"]
    
    note_response = client.post("/api/notes/", json={
        "title": "Private Note",
        "content": "Private Content"
    }, headers={"Authorization": f"Bearer {token1}"})
    note_id = note_response.json()["id"]
    
    # Пользователь 2 пытается получить доступ к заметке пользователя 1
    auth2_response = client.post("/auth/login", data={
        "username": "user2@example.com", 
        "password": "password2"
    })
    token2 = auth2_response.json()["access_token"]
    
    access_response = client.get(f"/api/notes/{note_id}", headers={"Authorization": f"Bearer {token2}"})
    assert access_response.status_code == 403
```

## 6. Нагрузочное тестирование

### 6.1. Использование k6
```javascript
// load-tests/notes-api.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '5m', target: 100 }, // Ramp-up to 100 users over 5 minutes
    { duration: '10m', target: 100 }, // Stay at 100 users for 10 minutes
    { duration: '5m', target: 0 },   // Ramp-down to 0 users over 5 minutes
  ],
};

export default function () {
  const baseUrl = 'https://serv.temasuug.ru/api';
  const token = __ENV.AUTH_TOKEN; // Pass token as environment variable
  
  const headers = {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  };
  
  // Test note creation
  const createPayload = JSON.stringify({
    title: `Load Test Note ${Date.now()}`,
    content: 'This is a load test note',
    is_public: false
  });
  
  const createParams = {
    headers: headers,
  };
  
  const createResponse = http.post(`${baseUrl}/notes/`, createPayload, createParams);
  check(createResponse, {
    'create note status is 200': (r) => r.status === 200,
  });
  
  sleep(1);
  
  // Test note retrieval
  const getResponse = http.get(`${baseUrl}/notes/`, { headers });
  check(getResponse, {
    'get notes status is 200': (r) => r.status === 200,
  });
  
  sleep(1);
}
```

## 7. Тестирование в CI/CD

### 7.1. GitHub Actions для тестирования
```yaml
# .github/workflows/test.yml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
        options: --health-cmd="pg_isready" --health-interval=10s --health-timeout=5s --health-retries=5

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r backend/requirements.txt
        pip install pytest pytest-cov

    - name: Run backend tests
      run: |
        cd backend
        pytest tests/ --cov=app --cov-report=xml
        coverage report

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./backend/coverage.xml
        flags: backend
        name: backend

  frontend-tests:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'
        cache-dependency-path: frontend/package-lock.json

    - name: Install dependencies
      run: npm ci
      working-directory: frontend

    - name: Run unit tests
      run: npm run test:unit
      working-directory: frontend

    - name: Run linting
      run: npm run lint
      working-directory: frontend

  e2e-tests:
    runs-on: ubuntu-latest
    timeout-minutes: 15

    steps:
    - uses: actions/checkout@v3

    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'

    - name: Install dependencies
      run: npm ci
      working-directory: frontend

    - name: Run Cypress tests
      uses: cypress-io/github-action@v5
      with:
        install: false
        working-directory: frontend
        browser: chrome
        headless: true
      env:
        CYPRESS_baseUrl: http://localhost:3000
```

## 8. Метрики качества тестирования

### 8.1. Показатели
- Покрытие кода: не менее 80% для backend
- Покрытие UI компонентов: не менее 70% для frontend
- Время выполнения тестов: не более 10 минут для всего набора
- Частота сбоев тестов: стремиться к 0%

### 8.2. Отчеты
- Автоматические отчеты о покрытии в CI/CD
- Генерация HTML отчетов для ручного анализа
- Интеграция с системами управления качеством кода