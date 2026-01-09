# 📖 Полная документация проекта

## Краткое содержание

Этот проект содержит полный пример настройки CI/CD для K3s кластера с Flask приложением, Docker контейнеризацией и GitHub Actions автоматизацией.

---

## 📚 Документация (выбирайте по потребностям)

### 🌟 НОВОЕ: Локальная разработка

#### 1. **[LOCAL_QUICKSTART.md](LOCAL_QUICKSTART.md)** (⭐ НАЧНИТЕ ОТСЮДА!)
   ⏱️ 2 минуты
   - Одна команда: `bash setup-local.sh`
   - Локальный Docker Registry
   - Полная локальная среда
   
   **Для кого:** Хочет быстро запустить всё локально

#### 2. **[LOCAL_SETUP.md](LOCAL_SETUP.md)** 📖
   ⏱️ 20 минут (полный гайд локальной разработки)
   - Детальное объяснение локального setup
   - Пошаговые инструкции
   - Типичные workflows
   - Troubleshooting
   - Рекомендации для k3d и minikube
   
   **Для кого:** Полное понимание локальной разработки

---

### 📚 ОСНОВНАЯ ДОКУМЕНТАЦИЯ

#### 3. **[QUICKSTART.md](QUICKSTART.md)**
   ⏱️ 5-10 минут
   - Запуск приложения локально
   - Docker запуск
   - Docker Compose
   - Быстрое развертывание в K3s
   
   **Для кого:** Новичков, хочет быстро увидеть результат

#### 4. **[README.md](README.md)** (главный файл)
   ⏱️ 10 минут
   - Обзор проекта
   - Структура
   - API endpoints
   - Основные команды
   
   **Для кого:** Общее понимание проекта

#### 5. **[CI_CD_GUIDE.md](CI_CD_GUIDE.md)** 📚
   ⏱️ 20 минут
   - Что такое CI/CD
   - Архитектура решения
   - Объяснение каждого компонента
   - Best practices
   
   **Для кого:** Хочет понять CI/CD концепции

#### 6. **[K3S_DEPLOYMENT.md](K3S_DEPLOYMENT.md)** 🚀
   ⏱️ 15 минут
   - Развертывание в K3s
   - Мониторинг
   - Обновление приложения
   - Troubleshooting
   
   **Для кого:** Развертывание в K3s кластер

#### 7. **[README_MAIN.md](README_MAIN.md)** 📖
   ⏱️ 30 минут (полная документация)
   - Подробная архитектура
   - Все API endpoints с примерами
   - Расширенная конфигурация
   - Интеграция с Prometheus
   - Полный troubleshooting guide
   
   **Для кого:** Полное изучение проекта

---

## 🎯 Рекомендуемый путь обучения

### День 1: Основы
```
1. Прочитайте README.md (5 минут)
2. Запустите QUICKSTART.md (10 минут)
   - python src/app.py
   - docker run demo-app
3. Смотрите API endpoints в браузере
```

### День 2: Docker & Тесты
```
1. Соберите Docker образ (5 минут)
2. Запустите docker-compose (5 минут)
3. Запустите тесты (5 минут)
4. Разберитесь с Dockerfile
```

### День 3: K3s развертывание
```
1. Прочитайте K3S_DEPLOYMENT.md
2. Примените k8s манифесты
3. Проверьте логи и статус
4. Обновите приложение
```

### День 4: CI/CD автоматизация
```
1. Прочитайте CI_CD_GUIDE.md
2. Создайте GitHub репозиторий
3. Настройте KUBECONFIG secret
4. Push в main branch → Watch pipeline
```

### День 5: Advanced topics
```
1. Прочитайте README_MAIN.md (все детали)
2. Настройте мониторинг (Prometheus)
3. Настройте логирование
4. Добавьте свои endpoints
```

---

## 📁 Структура файлов и их назначение

```
tofu/
│
├── 📄 README.md                    ← ГЛАВНЫЙ файл, начните с него
├── 📄 QUICKSTART.md                ← Быстрый старт (5 минут)
├── 📄 K3S_DEPLOYMENT.md            ← Развертывание в K3s
├── 📄 CI_CD_GUIDE.md               ← CI/CD практики и концепции
├── 📄 README_MAIN.md               ← Полная подробная документация
├── 📄 DOCUMENTATION_MAP.md         ← Этот файл (навигация)
│
├── 📂 src/
│   └── app.py                      ← Flask приложение
│
├── 📂 tests/
│   └── test_app.py                 ← Unit тесты
│
├── 📂 docker/
│   └── Dockerfile                  ← Multi-stage Docker
│
├── 📂 k8s/
│   ├── deployment.yaml             ← K8s Deployment + Service + HPA + RBAC
│   └── ingress.yaml                ← Ingress + NetworkPolicy + ResourceQuota
│
├── 📂 .github/workflows/
│   └── ci-cd.yaml                  ← GitHub Actions pipeline
│
├── 📄 requirements.txt              ← Python зависимости
├── 📄 docker-compose.yaml          ← Docker Compose конфиг
├── 📄 Makefile                     ← Удобные команды
├── 📄 deploy.sh                    ← Скрипт развертывания
├── 📄 build.sh                     ← Скрипт сборки Docker образа
├── 📄 .dockerignore                ← Что исключить из Docker
└── 📄 LICENSE                      ← MIT лицензия
```

---

## 🚀 Быстрые команды

```bash
# Запустить локально
python src/app.py

# Docker
docker build -f docker/Dockerfile -t demo-app:latest .
docker run -p 5000:5000 demo-app:latest

# Docker Compose
docker-compose up

# Тесты
pytest tests/ -v

# K3s (после обновления image tag)
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/ingress.yaml

# Логи
kubectl logs -f deployment/demo-app -n demo-app

# Port forward
kubectl port-forward svc/demo-app 8080:80 -n demo-app

# Make команды
make help
make test
make build
make deploy
```

---

## 🎓 Что вы изучите

### Python & Flask
- ✅ Создание REST API
- ✅ Health checks для K8s
- ✅ Структурированное логирование
- ✅ Prometheus метрики

### Docker
- ✅ Multi-stage builds
- ✅ Оптимизация образов
- ✅ Security best practices
- ✅ .dockerignore

### Kubernetes (K3s)
- ✅ Deployments с репликами
- ✅ Services и Ingress
- ✅ ConfigMaps и Secrets
- ✅ Probes (liveness, readiness, startup)
- ✅ HPA (автомасштабирование)
- ✅ RBAC и ServiceAccounts
- ✅ NetworkPolicy и Security Context
- ✅ Resource Quotas и PDB

### CI/CD & GitHub Actions
- ✅ Automated testing
- ✅ Docker image building
- ✅ Image registry (GHCR)
- ✅ Security scanning (Trivy)
- ✅ Automated deployment
- ✅ Health checks
- ✅ Rollback capability

### DevOps Practices
- ✅ Infrastructure as Code (IaC)
- ✅ Continuous Integration
- ✅ Continuous Deployment
- ✅ Automated testing
- ✅ Security scanning
- ✅ Monitoring & Logging
- ✅ Troubleshooting

---

## 💡 Практические примеры

### Пример 1: Локальное развитие
```bash
# Terminal 1: Запустить приложение
python src/app.py

# Terminal 2: Тестировать API
curl http://localhost:5000/api/health
curl -X POST http://localhost:5000/api/message -d '{"message": "Hello"}'
```

### Пример 2: Docker разработка
```bash
# Собрать и запустить
docker build -f docker/Dockerfile -t myapp:v1 .
docker run -p 5000:5000 myapp:v1
```

### Пример 3: K3s деплой
```bash
# Обновить image tag и применить
sed -i 's/IMAGE_TAG/v1/g' k8s/deployment.yaml
kubectl apply -f k8s/

# Смотреть статус
watch kubectl get pods -n demo-app
```

### Пример 4: CI/CD автоматизация
```bash
# Просто push в main
git add .
git commit -m "Update feature"
git push origin main

# GitHub Actions сделает всё остальное:
# - Тесты
# - Build
# - Security scan
# - Deploy в K3s
# - Health check
```

---

## 🔍 API Reference

```
GET  /                    → Главная страница с информацией
GET  /api/health          → Health check для K8s (JSON)
GET  /api/info            → Информация о приложении
GET  /api/ping            → Простой ping/pong
POST /api/message         → Отправить сообщение (JSON body)
GET  /metrics             → Prometheus метрики
```

---

## 🛠️ Команды по категориям

### Разработка
```bash
pip install -r requirements.txt
python src/app.py
pytest tests/ -v
pytest tests/ --cov=src
```

### Docker
```bash
docker build -f docker/Dockerfile -t demo-app:latest .
docker run -p 5000:5000 demo-app:latest
docker-compose up
docker tag demo-app:latest ghcr.io/user/demo-app:latest
docker push ghcr.io/user/demo-app:latest
```

### Kubernetes
```bash
kubectl cluster-info
kubectl create namespace demo-app
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/ingress.yaml
kubectl get pods -n demo-app
kubectl logs -f deployment/demo-app -n demo-app
kubectl port-forward svc/demo-app 8080:80 -n demo-app
kubectl rollout status deployment/demo-app -n demo-app
kubectl delete namespace demo-app
```

### GitHub Actions
```bash
git push origin main  # Автоматически запустит pipeline
# Смотрите результаты в GitHub → Actions
```

### Make (Makefile)
```bash
make help        # Список всех команд
make install     # Установить зависимости
make test        # Запустить тесты
make build       # Собрать Docker образ
make deploy      # Развернуть в K3s
make clean       # Удалить приложение
make logs        # Просмотреть логи
```

---

## ⚡ FAQ (Часто задаваемые вопросы)

### Q: Где начать?
A: Смотрите [QUICKSTART.md](QUICKSTART.md) - займет 5 минут

### Q: Как развернуть в K3s?
A: Смотрите [K3S_DEPLOYMENT.md](K3S_DEPLOYMENT.md)

### Q: Как работает CI/CD?
A: Смотрите [CI_CD_GUIDE.md](CI_CD_GUIDE.md)

### Q: Где полная документация?
A: Смотрите [README_MAIN.md](README_MAIN.md)

### Q: Как обновить приложение?
A: Смотрите раздел "Обновление приложения" в [K3S_DEPLOYMENT.md](K3S_DEPLOYMENT.md)

### Q: Почему pod не запускается?
A: Смотрите раздел "Troubleshooting" в [K3S_DEPLOYMENT.md](K3S_DEPLOYMENT.md)

---

## 🚀 Следующие шаги

После успешного развертывания:

1. **Добавить database** (PostgreSQL)
2. **Настроить monitoring** (Prometheus + Grafana)
3. **Добавить authentication** (JWT)
4. **Настроить logging** (ELK stack)
5. **Добавить caching** (Redis)
6. **Настроить backup** (Velero)
7. **Настроить load testing** (k6, Locust)

---

## 📞 Поддержка

Если у вас есть вопросы:
1. Проверьте [README_MAIN.md](README_MAIN.md) (troubleshooting раздел)
2. Смотрите логи: `kubectl logs -f deployment/demo-app -n demo-app`
3. Проверьте статус: `kubectl describe deployment demo-app -n demo-app`

---

## 📄 Лицензия

MIT - смотрите [LICENSE](LICENSE)

---

## 🎉 Результат

После выполнения всех шагов у вас будет:
- ✅ Работающее Flask приложение
- ✅ Docker контейнер
- ✅ K3s развертывание
- ✅ GitHub Actions CI/CD
- ✅ Автоматическое масштабирование
- ✅ Health checks
- ✅ Логирование и мониторинг
- ✅ Security best practices

**Готовы начать? → [QUICKSTART.md](QUICKSTART.md)** 🚀
