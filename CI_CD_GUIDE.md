# 📚 CI/CD практики для K3s - Полное руководство

## Введение: Что такое CI/CD?

**CI/CD (Continuous Integration / Continuous Deployment)** - это набор практик, которые:
- **CI (Continuous Integration)**: Автоматически интегрирует код, запускает тесты
- **CD (Continuous Deployment)**: Автоматически развертывает приложение в production

## 🎯 Основные концепции

### 1. Source Control (Git)
```
Developer Code → Push → GitHub → Webhook
```

### 2. Automated Testing
```
Code → Run Tests → Code Coverage → Report
```

### 3. Build & Package
```
Code → Docker Build → Image Registry → Store
```

### 4. Security Scanning
```
Docker Image → Vulnerability Scan → CVE Report → Alert
```

### 5. Deployment
```
Image → K8s Manifests → Apply → Health Check → Monitor
```

---

## 🏗️ Архитектура нашего решения

```
┌─────────────────────────────────────────────────────────┐
│                  GitHub Repository                       │
│               (Source Code Control)                      │
└───────────────┬─────────────────────────────────────────┘
                │ Push Event
                ▼
┌─────────────────────────────────────────────────────────┐
│              GitHub Actions Workflow                      │
│  ┌──────────────┬────────────────┬──────────────┐        │
│  │   1. TEST    │  2. BUILD      │  3. SECURITY │        │
│  │              │                │              │        │
│  │ - Unit tests │ - Docker image │ - Trivy scan │        │
│  │ - Coverage   │ - Push to GHCR │ - CVE report │        │
│  └──────────────┴────────────────┴──────────────┘        │
│                     │                                     │
│              ┌──────▼───────────┐                        │
│              │ 4. DEPLOY (main) │                        │
│              │ - kubectl apply  │                        │
│              │ - Wait rollout   │                        │
│              └──────┬───────────┘                        │
│                     │                                     │
│              ┌──────▼──────────┐                         │
│              │ 5. VERIFY       │                         │
│              │ - Health check  │                         │
│              │ - Integration   │                         │
│              │ - Slack alert   │                         │
│              └─────────────────┘                         │
└─────────────────────────────────────────────────────────┘
                     │
┌────────────────────▼──────────────────────────────────┐
│             K3s Kubernetes Cluster                    │
│  ┌──────────────────────────────────────────────────┐ │
│  │          demo-app Namespace                      │ │
│  │  ┌──────────────────────────────────────────┐   │ │
│  │  │ Deployment (Replicas: 3)                 │   │ │
│  │  │ ├─ Container Image: ghcr.io/...          │   │ │
│  │  │ ├─ Liveness Probe: /api/health           │   │ │
│  │  │ ├─ Readiness Probe: /api/health          │   │ │
│  │  │ └─ Resources: CPU/Memory limits          │   │ │
│  │  │                                          │   │ │
│  │  │ Service: demo-app (ClusterIP)            │   │ │
│  │  │ HPA: Auto-scale (CPU/Memory based)       │   │ │
│  │  │ Ingress: External access                 │   │ │
│  │  └──────────────────────────────────────────┘   │ │
│  └──────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────┘
```

---

## 📋 Как использовать этот проект

### Шаг 1: Структура проекта
```
tofu/
├── src/               # Исходный код приложения
├── tests/             # Unit тесты
├── docker/            # Dockerfile
├── k8s/               # Kubernetes манифесты
├── .github/workflows/ # GitHub Actions
├── Makefile           # Команды
└── deploy.sh          # Скрипт развертывания
```

### Шаг 2: Локальная разработка
```bash
# Установить зависимости
pip install -r requirements.txt

# Запустить приложение
python src/app.py

# Запустить тесты
pytest tests/ -v
```

### Шаг 3: Docker контейнеризация
```bash
# Собрать образ
docker build -f docker/Dockerfile -t demo-app:latest .

# Запустить контейнер
docker run -p 5000:5000 demo-app:latest

# Отправить в registry
docker push ghcr.io/username/tofu:latest
```

### Шаг 4: Kubernetes развертывание
```bash
# Применить манифесты
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/ingress.yaml

# Проверить статус
kubectl get pods -n demo-app
kubectl logs -f deployment/demo-app -n demo-app
```

### Шаг 5: Автоматизация с GitHub Actions
```bash
# Push в GitHub
git push origin main

# Pipeline автоматически:
# 1. Запустит тесты
# 2. Соберет Docker образ
# 3. Сканирует на уязвимости
# 4. Развернет в K3s
# 5. Проверит здоровье
```

---

## 🔑 Ключевые файлы и их роль

### 1. Flask Приложение ([src/app.py](src/app.py))
```python
# Endpoints для различных целей
GET  /              → Главная страница
GET  /api/health    → Для K8s probes (liveness/readiness)
GET  /api/info      → Информация о приложении
POST /api/message   → Обработка сообщений
GET  /metrics       → Prometheus метрики
```

**Зачем:**
- Демонстрирует рабочее Flask приложение
- Включает health checks для K8s
- Предоставляет метрики для мониторинга

### 2. Tests ([tests/test_app.py](tests/test_app.py))
```python
# Unit тесты для всех endpoints
test_health_check()
test_info_endpoint()
test_message_endpoint()
test_metrics_endpoint()
```

**Зачем:**
- Проверяет корректность кода
- Генерирует отчеты покрытия
- Предотвращает регрессии

### 3. Dockerfile ([docker/Dockerfile](docker/Dockerfile))
```dockerfile
# Multi-stage build для минимального размера
FROM python:3.11-slim as builder
FROM python:3.11-slim

# Best practices:
# - Non-root user
# - Minimal base image
# - Security scanning
```

**Зачем:**
- Контейнеризирует приложение
- Оптимизирует размер образа
- Реализует security best practices

### 4. Kubernetes Deployment ([k8s/deployment.yaml](k8s/deployment.yaml))
```yaml
Deployment:
  - 3 replicas для высокой доступности
  - Health probes (liveness, readiness, startup)
  - Resource requests/limits
  - Security context
  - RBAC (Role-Based Access Control)

HPA:
  - Auto-scaling на CPU/Memory
  - Min: 3 pods, Max: 10 pods

Service:
  - ClusterIP для внутреннего доступа
  
ConfigMap:
  - Конфигурация приложения
```

**Зачем:**
- Определяет как приложение работает в K8s
- Обеспечивает высокую доступность
- Автоматическое масштабирование

### 5. Ingress & Security ([k8s/ingress.yaml](k8s/ingress.yaml))
```yaml
Ingress:
  - Внешний доступ к приложению
  - Поддержка HTTPS/TLS

NetworkPolicy:
  - Ограничение трафика между подами
  - Только необходимый трафик разрешен

ResourceQuota:
  - Ограничение ресурсов namespace
  - Предотвращение overprovisioning

PodDisruptionBudget:
  - Минимум доступных подов при обновлениях
```

**Зачем:**
- Безопасный внешний доступ
- Сетевая безопасность
- Управление ресурсами

### 6. GitHub Actions ([.github/workflows/ci-cd.yaml](.github/workflows/ci-cd.yaml))
```yaml
Workflow:
  - Test: Запуск unit тестов
  - Build: Сборка Docker образа
  - Security: Сканирование с Trivy
  - Deploy: Развертывание в K3s
  - Verify: Проверка здоровья
```

**Зачем:**
- Полная автоматизация процесса
- Непрерывная интеграция и доставка
- Безопасность на каждом шаге

---

## 🛠️ Лучшие практики

### 1. Code Quality
✅ Unit тесты для всех функций
✅ Code coverage (>80%)
✅ Linting и formatting
✅ Type hints где возможно

### 2. Security
✅ Non-root контейнеры
✅ Minimal base images
✅ Vulnerability scanning
✅ Security context в K8s
✅ Network policies
✅ RBAC

### 3. Reliability
✅ Health checks (liveness/readiness)
✅ Graceful shutdown
✅ Resource limits
✅ Auto-scaling
✅ PodDisruptionBudget

### 4. Observability
✅ Структурированное логирование
✅ Prometheus метрики
✅ Tracing (опционально)
✅ Alerts (опционально)

### 5. DevOps
✅ Infrastructure as Code
✅ CI/CD automation
✅ Multi-environment support
✅ Easy rollback

---

## 📊 Примеры использования

### Сценарий 1: Локальная разработка
```bash
1. Clone репозиторий
2. pip install -r requirements.txt
3. python src/app.py
4. Открыть http://localhost:5000
5. Изменить код
6. pytest tests/ -v
7. Commit & Push
```

### Сценарий 2: Развертывание в K3s
```bash
1. Убедиться, что K3s работает: kubectl cluster-info
2. Обновить image tag в k8s/deployment.yaml
3. kubectl apply -f k8s/
4. Ждать rollout: kubectl rollout status...
5. kubectl port-forward svc/demo-app 8080:80
6. Протестировать: curl http://localhost:8080
```

### Сценарий 3: Автоматический CI/CD
```bash
1. Push в main branch
2. GitHub Actions автоматически:
   - Запускает тесты
   - Собирает Docker образ
   - Сканирует на уязвимости
   - Развертывает в K3s
   - Проверяет здоровье
3. Приложение обновлено в production
```

---

## 🔍 Мониторинг и Troubleshooting

### Проверить статус
```bash
# Pods
kubectl get pods -n demo-app
kubectl describe pod <pod-name> -n demo-app

# Deployment
kubectl get deployment -n demo-app
kubectl describe deployment demo-app -n demo-app

# Logs
kubectl logs deployment/demo-app -n demo-app
kubectl logs -f pod/<pod-name> -n demo-app
```

### Проверить здоровье
```bash
# Port forward
kubectl port-forward svc/demo-app 8080:80 -n demo-app

# Health check
curl http://localhost:8080/api/health

# Info
curl http://localhost:8080/api/info | jq .

# Metrics
curl http://localhost:8080/metrics
```

### Отладка
```bash
# Exec в pod
kubectl exec -it pod/<pod-name> -n demo-app -- /bin/bash

# События
kubectl get events -n demo-app

# Ресурсы
kubectl top pods -n demo-app
kubectl top nodes
```

---

## 📈 Расширение проекта

### Добавить Database
```yaml
# Добавить PostgreSQL в k8s/
apiVersion: v1
kind: Service
metadata:
  name: postgres
spec:
  # ...
```

### Добавить Monitoring
```yaml
# Установить Prometheus + Grafana
helm install prometheus prometheus-community/kube-prometheus-stack
```

### Добавить CI/CD Provider
```yaml
# GitLab CI, ArgoCD, Tekton и т.д.
```

### Добавить Load Testing
```bash
# k6, locust, Apache JMeter
```

---

## 📚 Дополнительные ресурсы

### Официальная документация
- [K3s](https://docs.k3s.io/)
- [Kubernetes](https://kubernetes.io/docs/)
- [Docker](https://docs.docker.com/)
- [GitHub Actions](https://docs.github.com/en/actions)

### Инструменты
- [kubectl](https://kubernetes.io/docs/reference/kubectl/)
- [Docker CLI](https://docs.docker.com/engine/reference/commandline/cli/)
- [Helm](https://helm.sh/)
- [ArgoCD](https://argoproj.github.io/argo-cd/)

### Best Practices
- [12 Factor App](https://12factor.net/)
- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

---

## ✅ Чек-лист для запуска

### Локально
- [ ] Python 3.11+ установлен
- [ ] pip install -r requirements.txt
- [ ] python src/app.py работает
- [ ] pytest tests/ проходят
- [ ] curl http://localhost:5000 работает

### Docker
- [ ] Docker установлен
- [ ] docker build успешен
- [ ] docker run работает
- [ ] curl http://localhost:5000 работает

### K3s
- [ ] K3s кластер работает
- [ ] kubectl cluster-info работает
- [ ] kubectl apply -f k8s/ успешен
- [ ] kubectl get pods -n demo-app показывает running pods
- [ ] kubectl port-forward работает

### GitHub Actions
- [ ] GitHub репозиторий создан
- [ ] KUBECONFIG secret добавлен
- [ ] Push в main branch
- [ ] GitHub Actions workflow успешен
- [ ] Приложение развернуто в K3s

---

## 🎓 Заключение

Этот проект демонстрирует:
✅ Современные CI/CD практики
✅ Kubernetes best practices
✅ Docker оптимизацию
✅ Security-first подход
✅ Infrastructure as Code
✅ Полную автоматизацию

Используйте его как шаблон для ваших собственных проектов!

---

**Happy DevOps! 🚀**
