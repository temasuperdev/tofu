# Локальный GitHub Actions Runner для приложения Notes

## Обзор
В этом руководстве описан процесс настройки и запуска локального GitHub Actions runner для CI/CD pipeline приложения Notes. Это позволяет запускать процессы сборки, тестирования и деплоя в вашей собственной инфраструктуре.

## Текущая конфигурация

### CI/CD Pipeline
- **Файлы**: `.github/workflows/ci.yml` и `.github/workflows/cd.yml`
- **Текущие runner'ы**: `ubuntu-latest` (GitHub-hosted)
- **Шаги CI**:
  - Тестирование бэкенда с PostgreSQL
  - Тестирование фронтенда
  - Сборка и публикация Docker-образов

### Локальный runner
- **Манифест**: `.github/actions-runner/k8s-manifests/github-actions-runner-dind.yaml`
- **Архитектура**: Docker-in-Docker для поддержки задач с контейнеризацией
- **Тип**: Self-hosted runner для GitHub Actions

## Требования

- Установленный k3s или Kubernetes кластер
- Доступ к командной строке с установленным `kubectl`
- Доступ к GitHub с правами настройки Actions runners
- Docker установлен в системе (для Docker-in-Docker функциональности)

## Шаги настройки

### Шаг 1: Подготовка GitHub токена

1. Перейдите в настройки вашего репозитория: `Settings` → `Actions` → `Runners`
2. Нажмите `New self-hosted runner`
3. Скопируйте токен для регистрации
4. Запишите URL вашего репозитория (например, `https://github.com/your-org/your-repo`)

### Шаг 2: Создание секретов в Kubernetes

Создайте секреты, необходимые для подключения runner к GitHub:

```bash
kubectl create secret generic github-runner-secrets \
  --from-literal=GITHUB_REPO_URL="https://github.com/your-org/your-repo" \
  --from-literal=GITHUB_RUNNER_TOKEN="your-runner-token" \
  --from-literal=GITHUB_RUNNER_NAME="k3s-notes-runner" \
  --namespace=default
```

Замените:
- `your-org/your-repo` - на фактический URL вашего репозитория
- `your-runner-token` - на токен, полученный из GitHub
- `k3s-notes-runner` - произвольное имя runner

### Шаг 3: Развертывание runner в k8s

Примените манифест для запуска Docker-in-Docker runner:

```bash
kubectl apply -f .github/actions-runner/k8s-manifests/github-actions-runner-dind.yaml
```

### Шаг 4: Проверка состояния

Проверьте, что pod запущен успешно:

```bash
kubectl get pods -l app=github-actions-runner-dind
```

Проверьте логи:

```bash
kubectl logs -l app=github-actions-runner-dind -f
```

### Шаг 5: Проверка регистрации в GitHub

1. Перейдите в настройки Actions runners: `Settings` → `Actions` → `Runners`
2. Убедитесь, что ваш runner появился в списке и имеет статус `Online`

## Изменение workflow для использования локального runner

Для использования локального runner измените файлы workflow в `.github/workflows/`:

### Файл: `.github/workflows/ci.yml`

Замените `runs-on: ubuntu-latest` на `runs-on: self-hosted`:

```yaml
name: CI Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test-backend:
    runs-on: self-hosted  # Было: ubuntu-latest
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
    runs-on: self-hosted  # Было: ubuntu-latest

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
    runs-on: self-hosted  # Было: ubuntu-latest
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

### Файл: `.github/workflows/cd.yml`

Аналогично, замените `runs-on: ubuntu-latest` на `runs-on: self-hosted`:

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
    runs-on: self-hosted  # Было: ubuntu-latest
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
    runs-on: self-hosted  # Было: ubuntu-latest
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

## Альтернативный подход: Использование меток

Если вы хотите более гибко управлять runner'ами, можно использовать метки:

1. Добавьте метку при регистрации runner:
   ```bash
   ./config.sh --url ${GITHUB_URL} --token ${RUNNER_TOKEN} --name ${RUNNER_NAME} --labels notes-app-runner
   ```

2. В workflow файлах используйте:
   ```yaml
   runs-on: [self-hosted, notes-app-runner]
   ```

## Мониторинг и обслуживание

### Проверка состояния runner

```bash
kubectl get pods -n default
kubectl describe pod <pod-name>
kubectl logs <pod-name>
```

### Перезапуск runner

```bash
kubectl delete pod -l app=github-actions-runner-dind
```

Kubernetes автоматически пересоздаст pod.

## Устранение неполадок

### Проблема: Runner не регистрируется в GitHub

1. Проверьте корректность токена:
   ```bash
   kubectl get secret github-runner-secrets -o yaml
   ```

2. Проверьте логи pod:
   ```bash
   kubectl logs <pod-name>
   ```

3. Убедитесь, что URL репозитория указан правильно

### Проблема: Ошибки с Docker (в случае использования dind)

1. Проверьте, что privileged режим включен в container specification
2. Убедитесь, что у k3s есть доступ к внешним ресурсам для скачивания образов

### Проблема: Недостаточно ресурсов

Отредактируйте манифест, увеличив значения в разделах `resources.requests` и `resources.limits`.

## Безопасность

- Регулярно обновляйте токены runner
- Используйте network policies для ограничения доступа к runner
- Ограничьте привилегии service accounts
- Периодически проверяйте логи на предмет подозрительной активности

## Удаление runner

Для удаления runner выполните:

```bash
kubectl delete -f .github/actions-runner/k8s-manifests/github-actions-runner-dind.yaml
kubectl delete secret github-runner-secrets
```

## Заключение

Теперь у вас есть полнофункциональный GitHub Actions runner, работающий в вашем локальном k3s кластере, специально настроенный для приложения Notes. Он может выполнять все те же задачи, что и hosted runner, но с дополнительными преимуществами локальной инфраструктуры:

- Более быстрая инициализация по сравнению с cloud экземплярами
- Контроль над вычислительными ресурсами
- Возможность использования внутренней инфраструктуры
- Интеграция с остальными сервисами в кластере
- Упрощение сетевой безопасности и доступа к внутренним ресурсам