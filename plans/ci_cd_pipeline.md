# CI/CD Pipeline для микросервисного приложения заметок

## 1. Общая архитектура CI/CD

```
[GitHub Repository] 
    ↓ (Push/PR)
[GitHub Actions] 
    ↓ (Build & Test)
[Container Registry] 
    ↓ (Deploy)
[Kubernetes Cluster]
```

## 2. GitHub Actions Workflow

### 2.1. CI Pipeline (.github/workflows/ci.yml)

```yaml
name: CI Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test-backend:
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

    - name: Run linting
      run: |
        pip install flake8 black mypy
        flake8 backend/
        black --check backend/
        mypy backend/

    - name: Run backend tests
      run: |
        cd backend
        pytest tests/ --cov=app --cov-report=xml

    - name: Upload coverage reports to Codecov
      uses: codecov/codecov-action@v3

  test-frontend:
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

    - name: Run linting
      run: npm run lint
      working-directory: frontend

    - name: Run unit tests
      run: npm run test:unit
      working-directory: frontend

    - name: Build frontend
      run: npm run build
      working-directory: frontend

  build-and-push:
    needs: [test-backend, test-frontend]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
    - uses: actions/checkout@v3

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2

    - name: Login to Container Registry
      uses: docker/login-action@v2
      with:
        registry: ghcr.io
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}

    - name: Build and push backend image
      uses: docker/build-push-action@v4
      with:
        context: ./backend
        file: ./backend/Dockerfile
        push: true
        tags: |
          ghcr.io/${{ github.repository }}/backend:${{ github.sha }}
          ghcr.io/${{ github.repository }}/backend:latest
        cache-from: type=gha
        cache-to: type=gha,mode=max

    - name: Build and push frontend image
      uses: docker/build-push-action@v4
      with:
        context: ./frontend
        file: ./frontend/Dockerfile
        push: true
        tags: |
          ghcr.io/${{ github.repository }}/frontend:${{ github.sha }}
          ghcr.io/${{ github.repository }}/frontend:latest
        cache-from: type=gha
        cache-to: type=gha,mode=max
```

### 2.2. CD Pipeline (.github/workflows/cd.yml)

```yaml
name: CD Pipeline

on:
  workflow_run:
    workflows: ["CI Pipeline"]
    types:
      - completed
    branches: [main]

jobs:
  deploy-staging:
    runs-on: ubuntu-latest
    if: ${{ github.event.workflow_run.conclusion == 'success' }}

    steps:
    - uses: actions/checkout@v3

    - name: Setup kubectl
      uses: azure/setup-kubectl@v3
      with:
        version: 'latest'

    - name: Set up kubeconfig
      run: |
        mkdir -p ~/.kube
        echo "${{ secrets.KUBECONFIG_STAGING }}" | base64 -d > ~/.kube/config
        chmod 600 ~/.kube/config

    - name: Update backend deployment
      run: |
        kubectl set image deployment/backend-deployment backend=ghcr.io/${{ github.repository }}/backend:${{ github.sha }} -n staging
        kubectl rollout status deployment/backend-deployment -n staging

    - name: Update frontend deployment
      run: |
        kubectl set image deployment/frontend-deployment frontend=ghcr.io/${{ github.repository }}/frontend:${{ github.sha }} -n staging
        kubectl rollout status deployment/frontend-deployment -n staging

    - name: Run smoke tests
      run: |
        # Add health check and basic functionality tests
        sleep 30
        curl -f http://staging.serv.temasuug.ru/health || exit 1

  deploy-production:
    needs: deploy-staging
    runs-on: ubuntu-latest
    if: success() && contains(github.event.head_commit.message, '[deploy]')
    environment: production

    steps:
    - uses: actions/checkout@v3

    - name: Setup kubectl
      uses: azure/setup-kubectl@v3
      with:
        version: 'latest'

    - name: Set up kubeconfig
      run: |
        mkdir -p ~/.kube
        echo "${{ secrets.KUBECONFIG_PROD }}" | base64 -d > ~/.kube/config
        chmod 600 ~/.kube/config

    - name: Update backend deployment
      run: |
        kubectl set image deployment/backend-deployment backend=ghcr.io/${{ github.repository }}/backend:${{ github.sha }} -n production
        kubectl rollout status deployment/backend-deployment -n production

    - name: Update frontend deployment
      run: |
        kubectl set image deployment/frontend-deployment frontend=ghcr.io/${{ github.repository }}/frontend:${{ github.sha }} -n production
        kubectl rollout status deployment/frontend-deployment -n production

    - name: Run production smoke tests
      run: |
        sleep 30
        curl -f https://serv.temasuug.ru/health || exit 1

    - name: Notify deployment
      run: |
        # Send notification to Slack/Teams about successful deployment
        curl -X POST -H 'Content-type: application/json' \
        --data '{"text":"Production deployment successful: ${{ github.sha }}"}' \
        ${{ secrets.SLACK_WEBHOOK_URL }}
```

## 3. Контейнеризация

### 3.1. Backend Dockerfile

```dockerfile
# Multi-stage build for backend
FROM python:3.9-slim as builder

WORKDIR /app

COPY backend/requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

FROM python:3.9-slim as runtime

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*

COPY backend/ .

EXPOSE 8000

CMD ["gunicorn", "app.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

### 3.2. Frontend Dockerfile

```dockerfile
# Multi-stage build for frontend
FROM node:18-alpine as builder

WORKDIR /app

COPY frontend/package*.json ./
RUN npm ci --only=production

COPY frontend/ .
RUN npm run build

FROM nginx:alpine as runtime

COPY --from=builder /app/dist /usr/share/nginx/html
COPY frontend/nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

## 4. Стратегии деплоя

### 4.1. Blue-Green Deployment
- Поддерживает две идентичные среды: blue и green
- Переключение трафика между версиями без простоев
- Возможность быстрого отката

### 4.2. Canary Deployment
- Постепенное направление трафика на новую версию
- Начинается с 5% трафика, увеличивается до 100%
- Мониторинг метрик во время деплоя

## 5. Тестирование в CI/CD

### 5.1. Юнит-тесты
- Backend: pytest для тестирования бизнес-логики
- Frontend: Jest + Vue Test Utils для компонентов

### 5.2. Интеграционные тесты
- Тестирование API endpoints с реальной базой данных
- E2E тесты с Cypress для пользовательских сценариев

### 5.3. Тесты безопасности
- Проверка уязвимостей в зависимостях
- Сканирование контейнеров на наличие CVE

## 6. Мониторинг и оповещения

### 6.1. Метрики
- Время отклика API
- Количество ошибок
- Потребление ресурсов

### 6.2. Логирование
- Централизованное логирование через Fluentd/Elasticsearch
- Структурированные логи в формате JSON

### 6.3. Алертинг
- SLA деградация
- Высокий уровень ошибок
- Проблемы с производительностью