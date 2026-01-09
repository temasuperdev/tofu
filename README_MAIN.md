# K3s CI/CD Demo Application

**Полный пример приложения с CI/CD пайплайном для K3s кластера**

## 📋 Содержание

- [Архитектура](#архитектура)
- [Структура проекта](#структура-проекта)
- [Требования](#требования)
- [Быстрый старт](#быстрый-старт)
- [Локальное тестирование](#локальное-тестирование)
- [CI/CD Pipeline](#cicd-pipeline)
- [Развертывание в K3s](#развертывание-в-k3s)
- [Мониторинг и логирование](#мониторинг-и-логирование)
- [Troubleshooting](#troubleshooting)

## 🏗️ Архитектура

```
┌─────────────────────────────────────────────────────────┐
│                    GitHub / GitLab                        │
│            (Push code → Trigger CI/CD)                    │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│               GitHub Actions                             │
│  ┌──────────────┬────────────────┬──────────────┐        │
│  │   Testing    │  Build Image   │   Security   │        │
│  └──────────────┴────────────────┴──────────────┘        │
│                     │                                     │
│              ┌──────▼───────┐                            │
│              │Push to GHCR  │                            │
│              └──────┬───────┘                            │
│                     │                                     │
│              ┌──────▼───────────────────┐               │
│              │Deploy to K3s Cluster     │               │
│              │- Apply Manifests         │               │
│              │- Health Check            │               │
│              └──────────────────────────┘               │
└───────────────────────────────────────────────────────┘
                     │
┌────────────────────▼──────────────────────────────────┐
│             K3s Kubernetes Cluster                    │
│  ┌──────────────────────────────────────────────────┐ │
│  │           demo-app Namespace                     │ │
│  │  ┌──────────────────────────────────────────┐   │ │
│  │  │ Deployment (3 Replicas)                 │   │ │
│  │  │ ├─ Pod 1 → Service → Ingress            │   │ │
│  │  │ ├─ Pod 2                                │   │ │
│  │  │ └─ Pod 3                                │   │ │
│  │  │                                          │   │ │
│  │  │ HPA (Auto-scaling)                      │   │ │
│  │  └──────────────────────────────────────────┘   │ │
│  └──────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────┘
```

## 📁 Структура проекта

```
tofu/
├── .github/
│   └── workflows/
│       └── ci-cd.yaml          # GitHub Actions workflow
├── docker/
│   └── Dockerfile              # Multi-stage Dockerfile
├── k8s/
│   ├── deployment.yaml         # Deployment, Service, HPA, RBAC
│   └── ingress.yaml            # Ingress, NetworkPolicy, ResourceQuota
├── src/
│   └── app.py                  # Flask приложение
├── tests/
│   └── test_app.py             # Unit тесты
├── requirements.txt            # Python зависимости
├── README.md                   # Документация
└── .dockerignore               # Docker ignore rules
```

## 📦 Требования

### Для локальной разработки:
- Python 3.11+
- pip / conda
- Docker (для создания образа)
- kubectl (для работы с K8s)

### Для K3s кластера:
- K3s кластер (v1.24+)
- Traefik (по умолчанию в K3s) или другой ingress controller
- Registry доступ (GHCR, Docker Hub и т.д.)

## 🚀 Быстрый старт

### 1. Клонируйте репозиторий
```bash
git clone <ваш-репозиторий>
cd tofu
```

### 2. Установите зависимости
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

pip install -r requirements.txt
pip install pytest pytest-cov  # для тестирования
```

### 3. Запустите приложение локально
```bash
export APP_VERSION=1.0.0
export ENVIRONMENT=development
python src/app.py
```

Приложение будет доступно по адресу `http://localhost:5000`

### 4. Откройте в браузере
- Главная страница: [http://localhost:5000](http://localhost:5000)
- Health Check: [http://localhost:5000/api/health](http://localhost:5000/api/health)
- Info: [http://localhost:5000/api/info](http://localhost:5000/api/info)
- Metrics: [http://localhost:5000/metrics](http://localhost:5000/metrics)

## 🧪 Локальное тестирование

### Запуск тестов
```bash
# Установите тестовые зависимости
pip install pytest pytest-cov

# Запустите тесты
pytest tests/ -v

# С покрытием кода
pytest tests/ -v --cov=src --cov-report=html
```

### Построение Docker образа локально
```bash
docker build -f docker/Dockerfile -t demo-app:latest .
```

### Запуск контейнера локально
```bash
docker run -d \
  -e APP_VERSION=1.0.0 \
  -e ENVIRONMENT=development \
  -p 5000:5000 \
  --name demo-app \
  demo-app:latest

# Проверка
curl http://localhost:5000/api/health

# Остановка
docker stop demo-app
docker rm demo-app
```

## 🔄 CI/CD Pipeline

### Этапы Pipeline:

#### 1. **Testing** (На каждый commit)
- Запуск unit тестов
- Проверка покрытия кода
- Upload результатов в Codecov

```bash
pytest tests/ -v --cov=src --cov-report=xml
```

#### 2. **Build & Push** (На каждый commit)
- Построение Docker образа с multi-stage optimization
- Push в GitHub Container Registry (GHCR)
- Кэширование layers для ускорения

```bash
docker build -f docker/Dockerfile -t ghcr.io/yourname/tofu:sha .
docker push ghcr.io/yourname/tofu:sha
```

#### 3. **Security Scanning** (На каждый commit)
- Сканирование Docker образа с Trivy
- Поиск уязвимостей (CVE)
- Upload в GitHub Security tab

#### 4. **Deploy to K3s** (Только на main branch)
- Настройка kubectl конфигурации
- Создание namespace
- Применение Kubernetes манифестов
- Проверка health приложения

#### 5. **Post-Deploy Verification** (После успешного деплоя)
- Интеграционные тесты
- Проверка логов
- Отправка уведомления в Slack

### Настройка GitHub Actions Secrets

Для работы CI/CD пайплайна необходимо установить следующие secrets в GitHub:

```bash
# Settings → Secrets and variables → Actions
KUBECONFIG              # Base64 закодированный kubeconfig файл
SLACK_WEBHOOK           # Webhook URL для Slack уведомлений (опционально)
```

**Как получить KUBECONFIG:**
```bash
# На K3s хосте
cat /etc/rancher/k3s/k3s.yaml | base64

# На Mac/Linux
cat ~/.kube/config | base64 | pbcopy  # Mac
cat ~/.kube/config | base64 | xclip   # Linux

# На Windows (PowerShell)
$content = [System.IO.File]::ReadAllText("$env:USERPROFILE\.kube\config")
[Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($content)) | Set-Clipboard
```

## 🚢 Развертывание в K3s

### Вариант 1: Автоматический деплой через CI/CD

1. Убедитесь, что `KUBECONFIG` secret установлен в GitHub
2. Сделайте commit и push в main branch
3. GitHub Actions автоматически запустит pipeline
4. Приложение будет развернуто в K3s

### Вариант 2: Ручное развертывание

```bash
# 1. Установите kubeconfig
export KUBECONFIG=~/.kube/config

# 2. Проверьте подключение к K3s
kubectl cluster-info
kubectl get nodes

# 3. Создайте namespace
kubectl create namespace demo-app

# 4. Обновите image tag в deployment.yaml
sed -e "s|IMAGE_REGISTRY|ghcr.io|g" \
    -e "s|IMAGE_NAME|yourname/tofu|g" \
    -e "s|IMAGE_TAG|latest|g" \
    k8s/deployment.yaml | kubectl apply -f -

# 5. Примените ingress конфигурацию
kubectl apply -f k8s/ingress.yaml

# 6. Проверьте статус развертывания
kubectl rollout status deployment/demo-app -n demo-app
```

### Проверка развертывания

```bash
# Статус deployment'а
kubectl get deployment -n demo-app
kubectl describe deployment demo-app -n demo-app

# Статус подов
kubectl get pods -n demo-app
kubectl describe pod <pod-name> -n demo-app

# Логи приложения
kubectl logs -f deployment/demo-app -n demo-app

# Доступ к сервису
kubectl port-forward svc/demo-app 8080:80 -n demo-app
# Откройте http://localhost:8080

# Проверка health
curl http://localhost:8080/api/health
```

### Обновление приложения

```bash
# Способ 1: Через kubectl set image
kubectl set image deployment/demo-app \
  app=ghcr.io/yourname/tofu:new-tag \
  -n demo-app

# Способ 2: Через kubectl patch
kubectl patch deployment demo-app \
  -n demo-app \
  -p '{"spec":{"template":{"spec":{"containers":[{"name":"app","image":"ghcr.io/yourname/tofu:new-tag"}]}}}}'

# Способ 3: Отката предыдущей версии
kubectl rollout undo deployment/demo-app -n demo-app
```

## 📊 Мониторинг и логирование

### Встроенные endpoints

| Endpoint | Метод | Описание |
|----------|-------|---------|
| `/` | GET | Главная страница с информацией |
| `/api/health` | GET | Health check для K8s probes |
| `/api/info` | GET | Информация о приложении |
| `/api/ping` | GET | Простой ping/pong |
| `/api/message` | POST | Отправка сообщения (JSON) |
| `/metrics` | GET | Prometheus метрики |

### Пример использования API

```bash
# Health check
curl http://localhost:5000/api/health

# Получить информацию
curl http://localhost:5000/api/info | jq .

# Отправить сообщение
curl -X POST http://localhost:5000/api/message \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello K3s!"}'

# Получить метрики
curl http://localhost:5000/metrics
```

### Логирование в K8s

```bash
# Логи одного пода
kubectl logs pod-name -n demo-app

# Логи всех подов
kubectl logs -l app=demo-app -n demo-app

# Следящий режим (tail)
kubectl logs -f deployment/demo-app -n demo-app --all-containers

# Логи за последний час
kubectl logs deployment/demo-app -n demo-app --since=1h

# Экспорт логов
kubectl logs deployment/demo-app -n demo-app > app-logs.txt
```

### Интеграция с Prometheus (опционально)

Приложение предоставляет метрики в формате Prometheus на `/metrics` endpoint.

```yaml
# ServiceMonitor для Prometheus Operator
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: demo-app
  namespace: demo-app
spec:
  selector:
    matchLabels:
      app: demo-app
  endpoints:
    - port: http
      path: /metrics
```

## ⚙️ Продвинутые конфигурации

### 1. Автоматическое масштабирование (HPA)

HPA настроена на основе CPU и памяти:

```bash
# Проверьте статус HPA
kubectl get hpa -n demo-app
kubectl describe hpa demo-app-hpa -n demo-app

# Генерируйте нагрузку для тестирования
kubectl run -i --tty load-generator --rm --image=busybox --restart=Never -- /bin/sh -c "while sleep 0.01; do wget -q -O- http://demo-app.demo-app; done"

# Наблюдайте за масштабированием
watch kubectl get hpa demo-app-hpa -n demo-app
```

### 2. Network Policy

Network Policy ограничивает входящий и исходящий трафик:
- Входящий трафик: только от ingress controller и внутри namespace
- Исходящий трафик: DNS для резолвинга и трафик между подами

### 3. Resource Quota

Ограничивает ресурсы namespace:
- CPU: 5 request / 10 limit
- Memory: 5Gi request / 10Gi limit
- Pods: максимум 20

### 4. Pod Disruption Budget

Гарантирует минимум 2 доступных пода при обновлениях кластера.

## 🔍 Troubleshooting

### Проблема: Pod не стартует

```bash
# Проверьте статус и ошибки
kubectl describe pod <pod-name> -n demo-app

# Смотрите логи
kubectl logs <pod-name> -n demo-app

# Проверьте ресурсы
kubectl top pods -n demo-app
kubectl top nodes
```

### Проблема: Image pull error

```bash
# Проверьте доступ к registry
kubectl get secret -n demo-app  # ImagePullSecret

# Создайте secret для приватного registry
kubectl create secret docker-registry regcred \
  --docker-server=ghcr.io \
  --docker-username=<username> \
  --docker-password=<token> \
  -n demo-app
```

### Проблема: Здоровье приложения не проходит

```bash
# Проверьте health endpoint напрямую
kubectl port-forward pod/<pod-name> 5000 -n demo-app
curl localhost:5000/api/health

# Увеличьте initialDelaySeconds в deployment
kubectl patch deployment demo-app \
  -n demo-app \
  --type='json' \
  -p='[{"op": "replace", "path": "/spec/template/spec/containers/0/livenessProbe/initialDelaySeconds", "value":30}]'
```

### Проблема: Ingress не работает

```bash
# Проверьте Ingress
kubectl get ingress -n demo-app
kubectl describe ingress demo-app -n demo-app

# Проверьте Traefik
kubectl get pods -n kube-system | grep traefik

# Обновите ingress хост
kubectl patch ingress demo-app -n demo-app --type merge -p '{"spec":{"rules":[{"host":"app.local"}]}}'
```

### Проблема: Out of Memory

```bash
# Увеличьте лимиты
kubectl set resources deployment demo-app \
  -n demo-app \
  --limits=memory=1Gi,cpu=1 \
  --requests=memory=256Mi,cpu=250m
```

## 📚 Дополнительные ресурсы

### Документация
- [K3s официальная документация](https://docs.k3s.io/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

### Полезные команды

```bash
# Удаление всего приложения
kubectl delete namespace demo-app

# Просмотр всех ресурсов
kubectl get all -n demo-app

# Debug pod
kubectl exec -it <pod-name> -n demo-app -- /bin/bash

# Port forward на локальную машину
kubectl port-forward svc/demo-app 8080:80 -n demo-app

# Проверка RBAC
kubectl auth can-i get pods --as=system:serviceaccount:demo-app:demo-app
```

## 📝 Лучшие практики

1. **Security**:
   - Используйте non-root user в контейнере
   - Ограничивайте capabilities
   - Используйте Network Policy
   - Регулярно сканируйте образы на уязвимости

2. **Reliability**:
   - Настраивайте liveness и readiness probes
   - Используйте HPA для автомасштабирования
   - Имплементируйте graceful shutdown
   - Используйте PDB для высокой доступности

3. **Performance**:
   - Multi-stage Docker build для меньшего размера образа
   - Правильная установка resource requests/limits
   - Кэширование Docker layers
   - Используйте persistent volume при необходимости

4. **Observability**:
   - Логируйте структурированно
   - Предоставляйте метрики
   - Используйте distributed tracing
   - Настраивайте alerts

## 🤝 Вклад в проект

1. Fork репозиторий
2. Создайте feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit изменения (`git commit -m 'Add some AmazingFeature'`)
4. Push в branch (`git push origin feature/AmazingFeature`)
5. Откройте Pull Request

## 📄 Лицензия

Этот проект лицензирован под MIT License - смотрите файл [LICENSE](LICENSE) для деталей.

---

**Happy Deploying! 🚀**
