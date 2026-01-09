# K3s CI/CD Demo Application

**Полный пример приложения с CI/CD пайплайном для K3s кластера**

## 🎯 Что это?

Это полнофункциональный пример:
- ✅ **Flask приложение** с REST API
- ✅ **Docker контейнеризация** с multi-stage build
- ✅ **Kubernetes манифесты** (Deployment, Service, Ingress, HPA)
- ✅ **GitHub Actions CI/CD** с тестами и развертыванием
- ✅ **Security best practices** (Network Policy, RBAC, Security Context)
- ✅ **Мониторинг и логирование** endpoints

## 🚀 Быстрый старт (выберите один вариант)

### Вариант 1: Локально на Python
```bash
pip install -r requirements.txt
python backend/src/app.py
# Откройте http://localhost:5000
```

### Вариант 2: Docker
```bash
docker build -f backend/docker/Dockerfile -t demo-app:latest .
docker run -p 5000:5000 demo-app:latest
# Откройте http://localhost:5000
```

### Вариант 3: Docker Compose
```bash
docker-compose -f backend/docker/docker-compose.yaml up
# Откройте http://localhost:5000
```

### Вариант 4: K3s + Локальный Docker Registry (⭐ РЕКОМЕНДУЕТСЯ)
```bash
# Полная локальная настройка одной командой!
bash backend/scripts/setup-local.sh

# Откройте http://localhost:8080
```

### Вариант 5: K3s с внешним registry (GitHub)
```bash
# Обновите image tag в backend/k8s/deployment.yaml
sed -i 's|IMAGE_REGISTRY|ghcr.io|g' backend/k8s/deployment.yaml
sed -i 's|IMAGE_NAME|yourname/tofu|g' backend/k8s/deployment.yaml
sed -i 's|IMAGE_TAG|latest|g' backend/k8s/deployment.yaml

# Примените манифесты
kubectl apply -f backend/k8s/deployment.yaml
kubectl apply -f backend/k8s/ingress.yaml

# Проверьте
kubectl port-forward svc/demo-app 8080:80 -n demo-app
# Откройте http://localhost:80
```

## 📁 Структура проекта

```
tofu/
├── backend/                    # Основное приложение
│   ├── src/                   # Исходный код Python
│   │   ├── __init__.py
│   │   └── app.py
│   ├── tests/                 # Тесты
│   │   ├── __init__.py
│   │   └── test_app.py
│   ├── requirements.txt       # Зависимости Python
│   └── setup.py              # Файл установки
├── k8s/                      # Kubernetes конфигурации
│   ├── deployment.yaml       # Deployment и связанные ресурсы
│   ├── deployment-production.yaml
│   ├── deployment-simple.yaml
│   ├── deployment-working.yaml
│   ├── ingress.yaml          # Ingress и сетевые настройки
│   ├── ingressroute.yaml
│   ├── letsencrypt-issuer.yaml
│   ├── networkpolicy.yaml
│   └── namespace.yaml        # Определение namespace
├── docker/                   # Docker конфигурации
│   ├── Dockerfile           # Основной Dockerfile
│   ├── docker-compose.yaml  # Docker Compose конфигурация
│   └── .dockerignore        # Файлы игнорирования для Docker
├── scripts/                  # Скрипты автоматизации
│   ├── build.sh             # Скрипт сборки
│   ├── build-local.sh
│   ├── cleanup-local.sh
│   ├── deploy.sh            # Скрипт деплоя
│   ├── deploy-local.sh
│   ├── deploy-local-k3s.sh
│   ├── make-local.sh
│   ├── registry.sh
│   ├── setup-local.sh
│   ├── show-local-setup.sh
│   └── test-app-locally.sh
├── docs/                     # Документация
│   ├── README.md            # Главный файл документации
│   ├── README_MAIN.md
│   ├── CI_CD_GUIDE.md
│   ├── CI_CD_HEALTH_CHECK_FIX.md
│   ├── CI_CD_HEALTH_CHECK_RESOLVED.md
│   ├── DNS_HTTPS_SETUP.md
│   ├── DOCUMENTATION_MAP.md
│   ├── GITHUB_ACTIONS_FIX.md
│   ├── K3S_DEPLOYMENT.md
│   ├── LOCAL_QUICKSTART.md
│   ├── LOCAL_SETUP_SUMMARY.md
│   ├── LOCAL_SETUP.md
│   ├── PROJECT_SUMMARY.md
│   ├── QUICKSTART.md
│   ├── SOLUTION_SUMMARY.md
│   ├── TROUBLESHOOTING_404.md
│   ├── TROUBLESHOOTING.md
│   └── .gitignore           # Git ignore для документации
├── configs/                  # Конфигурационные файлы
│   ├── .env.example         # Пример переменных окружения
│   └── .env.local          # Локальные переменные окружения
├── Makefile                 # Make команды
├── LICENSE                  # Лицензия
└── .gitignore              # Основной git ignore
```

## 📊 API Endpoints

| Endpoint | Метод | Описание |
|----------|-------|---------|
| `/` | GET | Главная страница |
| `/api/health` | GET | Health check (для K8s probes) |
| `/api/info` | GET | Информация о приложении |
| `/api/ping` | GET | Ping/Pong |
| `/api/message` | POST | Отправить сообщение (JSON) |
| `/metrics` | GET | Prometheus метрики |

## 🔄 CI/CD Pipeline

GitHub Actions автоматически:
1. **Тестирует** код при каждом push
2. **Строит** Docker образ
3. **Сканирует** на уязвимости (Trivy)
4. **Развертывает** в K3s (на main branch)
5. **Проверяет** здоровье приложения

Для активации нужно:
1. Push в GitHub репозиторий
2. Установить `KUBECONFIG` secret (Settings → Secrets and variables)
3. Pipeline запустится автоматически

## 🛡️ Security Features

- ✅ Non-root контейнеры
- ✅ Network Policy для ограничения трафика
- ✅ RBAC (Role-Based Access Control)
- ✅ Security Context для ограничения capabilities
- ✅ Resource Quotas
- ✅ Pod Disruption Budget
- ✅ Vulnerability scanning (Trivy)

## 📈 Kubernetes Features

- ✅ Deployment с 3 репликами
- ✅ Service (ClusterIP)
- ✅ Ingress для внешнего доступа
- ✅ HPA (Horizontal Pod Autoscaler) с CPU и памятью
- ✅ Liveness, Readiness, Startup probes
- ✅ Resource requests и limits
- ✅ ConfigMap для конфигурации

## 📝 Примеры использования

### Запуск тестов
```bash
pytest backend/tests/ -v --cov=backend/src
```

### Создание образа
```bash
docker build -f backend/docker/Dockerfile -t demo-app:v1.0 .
```

### Развертывание в K3s
```bash
bash backend/scripts/deploy.sh
# или
make -f backend/Makefile deploy IMAGE_TAG=v1.0
```

### Проверка логов
```bash
kubectl logs -f deployment/demo-app -n demo-app
```

### Доступ к приложению
```bash
kubectl port-forward svc/demo-app 8080:80 -n demo-app
curl http://localhost:8080/api/health
```

## 🧪 Тестирование API

```bash
# Health check
curl http://localhost:5000/api/health | jq

# Info
curl http://localhost:5000/api/info | jq

# Отправить сообщение
curl -X POST http://localhost:5000/api/message \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello K3s!"}'

# Метрики
curl http://localhost:5000/metrics
```

## 🛠️ Полезные команды

```bash
# Makefile команды
make -f backend/Makefile help        # Список всех команд
make -f backend/Makefile test        # Запуск тестов
make -f backend/Makefile build       # Сборка Docker образа
make -f backend/Makefile deploy      # Развертывание в K3s
make -f backend/Makefile logs        # Просмотр логов
make -f backend/Makefile clean       # Удаление приложения

# kubectl команды
kubectl get all -n demo-app                           # Все ресурсы
kubectl describe deployment demo-app -n demo-app      # Описание
kubectl logs -f deployment/demo-app -n demo-app       # Логи
kubectl exec -it <pod-name> -n demo-app -- /bin/bash # Доступ к поду
```

## 🆘 Troubleshooting

```bash
# Pod не стартует?
kubectl describe pod <pod-name> -n demo-app

# Ошибка в логах?
kubectl logs <pod-name> -n demo-app

## 🌐 Доступ через Ingress (K3s)

При развертывании в K3s, приложение автоматически доступно через **Traefik Ingress Controller**:

### Локально
```bash
# Получить Ingress IP адрес
kubectl get ingress -n demo-app

# Или через nodePort (если нет LoadBalancer)
kubectl get svc -n kube-system traefik -o jsonpath='{.spec.ports[0].nodePort}'

# Тестирование
curl -H "Host: serv.temasuug.ru" http://178.236.16.81/
curl -H "Host: serv.temasuug.ru" http://localhost:32463/api/health
```

### Через доменное имя
Чтобы использовать доменное имя `serv.temasuug.ru`:
1. Добавьте A record в DNS зону:
   ```
   serv IN A 178.236.16.81
   ```
2. Тогда можно обращаться как:
   ```bash
   curl http://serv.temasuug.ru/
   ```

### HTTPS (Let's Encrypt)
Для автоматического HTTPS с Let's Encrypt:
1. Установите cert-manager
2. Добавьте TLS в Ingress
3. Смотрите `backend/docs/TROUBLESHOOTING_404.md` для подробностей

## 🐛 Решение проблем

Если получаете ошибки при развертывании в K3s:
- Проверьте `backend/docs/TROUBLESHOOTING_404.md` - полный гайд решения типичных проблем
- Убедитесь что NetworkPolicy разрешает необходимые порты
- Проверьте логи Traefik: `kubectl logs -n kube-system -l app.kubernetes.io/name=traefik`
- Проверьте логи приложения: `kubectl logs -n demo-app -l app=demo-app`

# Проблема с доступом?
kubectl port-forward svc/demo-app 8080:80 -n demo-app
curl http://localhost:8080/api/health

# Удалить всё и начать заново?
kubectl delete namespace demo-app
```

## 📚 Документация

- [SOLUTION_SUMMARY.md](SOLUTION_SUMMARY.md) - Решение 404 ошибки
- [CI_CD_HEALTH_CHECK_FIX.md](CI_CD_HEALTH_CHECK_FIX.md) - **⭐ Исправление CI/CD health check!**
- [TROUBLESHOOTING_404.md](TROUBLESHOOTING_404.md) - Гайд по отладке
- [LOCAL_SETUP.md](LOCAL_SETUP.md) - Локальная разработка с Docker Registry
- [QUICKSTART.md](QUICKSTART.md) - Быстрый старт за 5 минут
- [README_MAIN.md](README_MAIN.md) - Подробная документация
- [K3S_DEPLOYMENT.md](K3S_DEPLOYMENT.md) - K3s гайд
- [CI_CD_GUIDE.md](CI_CD_GUIDE.md) - CI/CD концепции
- [K3s docs](https://docs.k3s.io/)
- [Kubernetes docs](https://kubernetes.io/docs/)

## 🎓 Чему вы научитесь

✅ Создавать и контейнеризировать приложения
✅ Писать Kubernetes манифесты
✅ Настраивать CI/CD с GitHub Actions
✅ Автоматически развертывать приложения
✅ Применять security best practices
✅ Настраивать мониторинг и логирование
✅ Работать с K3s кластером
✅ Использовать kubectl команды

## 📄 Лицензия

MIT License - см. [LICENSE](LICENSE)


---
**Готовы начать? Смотрите [QUICKSTART.md](QUICKSTART.md)!** 🚀