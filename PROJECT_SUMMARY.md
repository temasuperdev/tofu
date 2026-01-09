% K3s CI/CD Complete Learning Project
% 🚀 Полный проект для обучения CI/CD практикам

# ✨ Проект успешно создан!

## 📦 Что было создано

Полнофункциональный проект с примерами CI/CD для K3s кластера:

### 🎯 Ключевые компоненты

**1. Flask Приложение**
- REST API с 6 endpoints
- Health checks для K8s probes
- Prometheus метрики
- Структурированное логирование

**2. Docker**
- Multi-stage Dockerfile
- Оптимизированный размер образа
- Non-root пользователь
- Security best practices

**3. Kubernetes (K3s)**
- Deployment с 3 репликами
- Service и Ingress для доступа
- HPA (автомасштабирование)
- RBAC, NetworkPolicy, Security Context
- ConfigMap, ResourceQuota, PDB

**4. GitHub Actions CI/CD**
- Automated testing
- Docker image building
- Security scanning (Trivy)
- Automated deployment в K3s
- Health checks и verification

**5. Documentation** (5 документов)
- QUICKSTART.md - старт за 5 минут
- README.md - обзор проекта
- K3S_DEPLOYMENT.md - подробный K3s гайд
- CI_CD_GUIDE.md - объяснение CI/CD концепций
- README_MAIN.md - полная документация

---

## 📂 Структура проекта

```
tofu/ (17 файлов)
├── 📚 DOCUMENTATION              (5 документов)
│   ├── README.md                 (главный файл)
│   ├── QUICKSTART.md             (начните отсюда!)
│   ├── K3S_DEPLOYMENT.md         (K3s гайд)
│   ├── CI_CD_GUIDE.md            (CI/CD концепции)
│   └── README_MAIN.md            (полная документация)
│
├── 💻 APPLICATION CODE
│   ├── src/app.py                (Flask приложение)
│   ├── tests/test_app.py         (Unit тесты)
│   └── requirements.txt          (Python зависимости)
│
├── 🐳 DOCKER
│   ├── docker/Dockerfile         (Multi-stage build)
│   ├── docker-compose.yaml       (Docker Compose)
│   └── .dockerignore             (Ignore файлы)
│
├── ☸️  KUBERNETES
│   ├── k8s/deployment.yaml       (Deployment, Service, HPA, RBAC)
│   └── k8s/ingress.yaml          (Ingress, NetworkPolicy, Quotas)
│
├── 🤖 CI/CD
│   └── .github/workflows/ci-cd.yaml (GitHub Actions)
│
└── ⚙️  AUTOMATION SCRIPTS
    ├── Makefile                  (Make команды)
    ├── deploy.sh                 (Скрипт развертывания)
    ├── build.sh                  (Скрипт сборки)
    ├── .gitignore                (Git ignore)
    └── LICENSE                   (MIT)
```

---

## 🚀 Быстрый старт (выберите способ)

### Способ 1️⃣: Локально (2 минуты)
```bash
pip install -r requirements.txt
python src/app.py
open http://localhost:5000
```

### Способ 2️⃣: Docker (3 минуты)
```bash
docker build -f docker/Dockerfile -t demo-app .
docker run -p 5000:5000 demo-app
open http://localhost:5000
```

### Способ 3️⃣: Docker Compose (2 минуты)
```bash
docker-compose up
open http://localhost:5000
```

### Способ 4️⃣: K3s (5 минут)
```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/ingress.yaml
kubectl port-forward svc/demo-app 8080:80 -n demo-app
open http://localhost:8080
```

### Способ 5️⃣: GitHub Actions (автоматически)
```bash
git push origin main
# Pipeline автоматически развернет в K3s
```

---

## 📚 Рекомендуемый путь обучения

### День 1: Основы (30 минут)
```
1. Прочитайте README.md (5 мин)
2. Запустите QUICKSTART.md (10 мин)
3. Изучите API endpoints (10 мин)
4. Запустите тесты (5 мин)
```

### День 2: Контейнеризация (45 минут)
```
1. Разберитесь с Dockerfile (10 мин)
2. Соберите Docker образ (5 мин)
3. Запустите docker-compose (5 мин)
4. Загрузите в registry (10 мин)
5. Изучите best practices (15 мин)
```

### День 3: Kubernetes (60 минут)
```
1. Прочитайте K3S_DEPLOYMENT.md (15 мин)
2. Примените манифесты (10 мин)
3. Проверьте статус (10 мин)
4. Обновите приложение (15 мин)
5. Протестируйте масштабирование (10 мин)
```

### День 4: CI/CD (60 минут)
```
1. Прочитайте CI_CD_GUIDE.md (20 мин)
2. Разберитесь с GitHub Actions (15 мин)
3. Настройте KUBECONFIG secret (10 мин)
4. Push в GitHub → Watch pipeline (15 мин)
```

### День 5: Advanced (90 минут)
```
1. Прочитайте README_MAIN.md (30 мин)
2. Добавьте мониторинг (Prometheus) (30 мин)
3. Добавьте свои endpoints (20 мин)
4. Настройте logging (10 мин)
```

---

## 🎯 API Endpoints

| Method | Path | Описание |
|--------|------|---------|
| GET | `/` | Главная страница |
| GET | `/api/health` | Health check для K8s |
| GET | `/api/info` | Информация о приложении |
| GET | `/api/ping` | Ping/Pong |
| POST | `/api/message` | Отправить сообщение |
| GET | `/metrics` | Prometheus метрики |

Примеры:
```bash
curl http://localhost:5000/api/health | jq .
curl -X POST http://localhost:5000/api/message \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello K3s!"}'
```

---

## 🛠️ Основные команды

### Python & Тесты
```bash
pip install -r requirements.txt
pytest tests/ -v
pytest tests/ --cov=src
python src/app.py
```

### Docker
```bash
docker build -f docker/Dockerfile -t demo-app:latest .
docker run -p 5000:5000 demo-app:latest
docker-compose up
docker push ghcr.io/username/demo-app:latest
```

### Kubernetes
```bash
kubectl cluster-info
kubectl apply -f k8s/
kubectl get pods -n demo-app
kubectl logs -f deployment/demo-app -n demo-app
kubectl port-forward svc/demo-app 8080:80 -n demo-app
kubectl delete namespace demo-app
```

### Make (Makefile)
```bash
make help        # Список всех команд
make test        # Запустить тесты
make build       # Собрать образ
make deploy      # Развернуть в K3s
make logs        # Посмотреть логи
make clean       # Удалить приложение
```

### Scripts
```bash
bash build.sh                    # Собрать Docker образ
bash deploy.sh                   # Развернуть в K3s
# Или используйте Makefile (удобнее)
```

---

## 🎓 Чему вы научитесь

### Python & Web Framework
- ✅ Flask приложение с REST API
- ✅ Health checks и Prometheus метрики
- ✅ Error handling и logging

### Docker & Containerization
- ✅ Multi-stage Dockerfile builds
- ✅ Оптимизация размера образов
- ✅ Security best practices
- ✅ Docker registry (GHCR)

### Kubernetes (K3s)
- ✅ Deployments и Replicas
- ✅ Services и Ingress
- ✅ ConfigMaps и Secrets
- ✅ Probes (liveness/readiness/startup)
- ✅ HPA (Horizontal Pod Autoscaler)
- ✅ RBAC (Role-Based Access Control)
- ✅ Security Context и Capabilities
- ✅ Network Policy
- ✅ Resource Quotas

### CI/CD & Automation
- ✅ GitHub Actions workflows
- ✅ Automated testing
- ✅ Image building & pushing
- ✅ Security scanning (Trivy)
- ✅ Automated deployment
- ✅ Health checks
- ✅ Slack notifications

### DevOps Practices
- ✅ Infrastructure as Code
- ✅ Continuous Integration
- ✅ Continuous Deployment
- ✅ Monitoring & Logging
- ✅ Troubleshooting

---

## 📖 Документация (где что находится)

| Документ | Содержание | Время | Когда читать |
|----------|-----------|-------|-------------|
| **README.md** | Обзор проекта | 5 мин | Сначала |
| **QUICKSTART.md** | Быстрый старт | 10 мин | После README |
| **K3S_DEPLOYMENT.md** | K3s гайд | 15 мин | Перед развертыванием |
| **CI_CD_GUIDE.md** | CI/CD концепции | 20 мин | Для понимания pipeline |
| **README_MAIN.md** | Полная документация | 30 мин | Для глубокого изучения |
| **DOCUMENTATION_MAP.md** | Карта документации | 10 мин | Для навигации |

---

## 🔍 Troubleshooting

### Pod не запускается?
```bash
kubectl describe pod <pod-name> -n demo-app
kubectl logs <pod-name> -n demo-app
```

### Смотрите [K3S_DEPLOYMENT.md](K3S_DEPLOYMENT.md) раздел "Troubleshooting"

### Нужна полная помощь?
```bash
# 1. Проверьте README_MAIN.md (есть раздел troubleshooting)
# 2. Смотрите логи
# 3. Проверьте статус
# 4. Прочитайте Kubernetes документацию
```

---

## ⚡ Quick Reference

### Файлы для быстрого редактирования

**Добавить новый endpoint:**
- Отредактируйте [src/app.py](src/app.py)
- Добавьте тест в [tests/test_app.py](tests/test_app.py)
- Push → GitHub Actions автоматически развернет

**Изменить конфигурацию приложения:**
- Отредактируйте [k8s/deployment.yaml](k8s/deployment.yaml) (ConfigMap)
- `kubectl apply -f k8s/deployment.yaml`

**Добавить новую версию в K3s:**
- Обновите image tag
- `kubectl set image deployment/demo-app app=ghcr.io/user/tofu:new-tag -n demo-app`

**Посмотреть логи:**
- `kubectl logs -f deployment/demo-app -n demo-app`

**Доступ к приложению:**
- `kubectl port-forward svc/demo-app 8080:80 -n demo-app`
- `curl http://localhost:8080`

---

## 🎉 Что дальше?

После освоения проекта:

1. **Расширьте приложение**
   - Добавьте database (PostgreSQL)
   - Добавьте authentication (JWT)
   - Добавьте кэширование (Redis)

2. **Расширьте Kubernetes**
   - Добавьте мониторинг (Prometheus + Grafana)
   - Добавьте логирование (ELK stack)
   - Добавьте сетевые политики

3. **Расширьте CI/CD**
   - Добавьте load testing
   - Добавьте performance testing
   - Добавьте canary deployments

4. **Настройте production**
   - SSL/TLS certificates
   - Backup & Recovery
   - Disaster Recovery

---

## 📄 Файлы проекта

### Документация (5 файлов, 90KB)
- 📄 README.md (7.3 KB)
- 📄 QUICKSTART.md (3.2 KB)
- 📄 K3S_DEPLOYMENT.md (10.8 KB)
- 📄 CI_CD_GUIDE.md (16 KB)
- 📄 README_MAIN.md (19.1 KB)

### Код (2 файла, 12KB)
- 🐍 src/app.py (8.5 KB) - Flask приложение
- 🧪 tests/test_app.py (2.8 KB) - Unit тесты

### Docker (2 файла, 1.5 KB)
- 🐳 docker/Dockerfile (1.2 KB)
- 📝 docker-compose.yaml (950 B)

### Kubernetes (2 файла, 15 KB)
- ☸️ k8s/deployment.yaml (9.5 KB)
- ☸️ k8s/ingress.yaml (5.2 KB)

### GitHub Actions (1 файл, 8 KB)
- 🤖 .github/workflows/ci-cd.yaml (8 KB)

### Конфигурация (5 файлов, 3 KB)
- ⚙️ requirements.txt (67 B)
- ⚙️ Makefile (2.1 KB)
- ⚙️ deploy.sh (3.5 KB)
- ⚙️ build.sh (545 B)

**Итого: 17 файлов, ~140 KB** (Production-ready код)

---

## ✅ Результат

После выполнения всех шагов у вас будет:

- ✅ Работающее Flask приложение
- ✅ Dockerized контейнер
- ✅ K3s развертывание
- ✅ Автоматический CI/CD
- ✅ Масштабируемая архитектура
- ✅ Security best practices
- ✅ Мониторинг и логирование
- ✅ Production-ready setup

---

## 🚀 Начните прямо сейчас

### Вариант 1: Быстрый старт (5 минут)
```bash
cat QUICKSTART.md
python src/app.py
# Откройте http://localhost:5000
```

### Вариант 2: Полное обучение (5 дней)
```bash
# День 1
cat README.md
# День 2
cat K3S_DEPLOYMENT.md
# День 3
cat CI_CD_GUIDE.md
# День 4-5
cat README_MAIN.md
```

### Вариант 3: Сразу развернуть
```bash
# Убедитесь K3s работает
kubectl cluster-info

# Развернуть
kubectl apply -f k8s/

# Проверить
kubectl port-forward svc/demo-app 8080:80 -n demo-app
open http://localhost:8080
```

---

## 📞 Помощь

**Есть вопрос?**
1. Смотрите [DOCUMENTATION_MAP.md](DOCUMENTATION_MAP.md) - там карта всей документации
2. Проверьте раздел Troubleshooting в соответствующем документе
3. Смотрите логи: `kubectl logs -f deployment/demo-app -n demo-app`

---

## 📄 Лицензия

MIT License - используйте свободно!

---

## 🎊 Поздравляем!

Вы готовы к современному DevOps с K3s, Docker и CI/CD! 

**Начните с [README.md](README.md) или [QUICKSTART.md](QUICKSTART.md)** 🚀

---

*Проект создан: 9 января 2026*
*Версия: 1.0.0*
