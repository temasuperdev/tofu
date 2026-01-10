# 🔧 Исправление Container Crash ошибки

## ✅ Проблема и решение

### ❌ Ошибка при деплое:
```
Back-off restarting failed container app in pod demo-app-59c4fb4dd7-wsfsz_demo-app
```

### 🔍 Причина найдена:
**Redis недоступен!** Контейнер пытается подключиться к Redis при инициализации и падает.

### ✅ Что было исправлено:

#### 1. **Создан Redis StatefulSet** 🆕
```yaml
# backend/k8s/redis.yaml
- ConfigMap с настройками Redis
- StatefulSet с Redis 7-alpine
- Service для подключения приложения
```

**Особенности Redis конфигурации:**
- Memory limit: 256MB (достаточно для dev/test)
- Persistence: RDB + AOF (данные не теряются)
- Health checks: liveness + readiness probes
- Volume: 1Gi persistent storage

#### 2. **Обновлён ConfigMap в deployment-production.yaml** 🔧
```yaml
# Было:
data:
  APP_VERSION: "1.0.0"
  ENVIRONMENT: "production"

# Стало:
data:
  APP_VERSION: "1.0.0"
  ENVIRONMENT: "production"
  REDIS_URL: "redis://demo-redis.demo-app.svc.cluster.local:6379/0"
  LOG_LEVEL: "INFO"
```

#### 3. **Cache manager уже обрабатывает ошибки Redis** ✅
В `backend/src/utils/cache_manager.py` уже есть fallback:
```python
try:
    app.config['CACHE_TYPE'] = 'redis'
    self.cache = Cache(app)
except Exception as e:
    # Fallback на simple cache (в памяти)
    app.config['CACHE_TYPE'] = 'simple'
    self.cache = Cache(app)
```

## 📊 Файлы созданы/обновлены:

### Новые файлы:
- ✅ `backend/k8s/redis.yaml` - Redis StatefulSet + Service
  - ConfigMap для настройки Redis
  - StatefulSet с 1 репликой
  - PersistentVolumeClaim для данных
  - Health checks (liveness + readiness)

### Обновлены:
- ✅ `backend/k8s/deployment-production.yaml`
  - Добавлен REDIS_URL в ConfigMap
  - Добавлен LOG_LEVEL в ConfigMap

## ✨ Проверка YAML синтаксиса:

```
✅ redis.yaml
   3 документа:
   1. ConfigMap (redis-config)
   2. StatefulSet (demo-redis)
   3. Service (demo-redis)

✅ deployment-production.yaml
   8 документов:
   1. Namespace
   2. ServiceAccount
   3. Role
   4. RoleBinding
   5. ConfigMap (app-config)
   6. Service (demo-app)
   7. Deployment
   8. HorizontalPodAutoscaler
```

## 🚀 Как развернуть Redis:

```bash
# 1. Развернуть Redis
kubectl apply -f backend/k8s/redis.yaml

# 2. Проверить статус Redis pod'а
kubectl get pod -n demo-app -l app=demo-redis
kubectl describe pod -n demo-app -l app=demo-redis

# 3. Проверить что Redis доступен
kubectl exec -n demo-app -it demo-redis-0 -- redis-cli ping
# Ответ: PONG

# 4. Тогда развернуть приложение
kubectl apply -f backend/k8s/deployment-production.yaml

# 5. Проверить статус
kubectl rollout status deployment/demo-app -n demo-app
kubectl get pods -n demo-app
```

## 📈 Architecture:

```
┌─────────────────────────────────────┐
│  K3s Cluster (demo-app namespace)   │
├─────────────────────────────────────┤
│                                      │
│  ┌────────────────────────────────┐ │
│  │  demo-app Deployment (3 pods)  │ │
│  │  ├─ Pod 1 → :5000              │ │
│  │  ├─ Pod 2 → :5000              │ │
│  │  └─ Pod 3 → :5000              │ │
│  └──────────┬─────────────────────┘ │
│             │ (REDIS_URL)           │
│  ┌──────────▼─────────────────────┐ │
│  │  demo-redis StatefulSet (1)    │ │
│  │  ├─ redis-0 → :6379            │ │
│  │  └─ PVC (1Gi) for /data        │ │
│  └────────────────────────────────┘ │
│                                      │
└─────────────────────────────────────┘
```

## ✅ Почему это решит проблему:

1. **Redis будет доступен** - cache_manager подключится успешно
2. **Container не будет crashить** - инициализация будет успешной
3. **Данные сохраняются** - Redis имеет persistent volume
4. **Fallback включен** - если Redis временно недоступен, используется simple cache
5. **Health checks настроены** - Redis pod'ы будут перезагружаться при проблемах

## 🎯 Дальше:

```bash
# 1. Обновить deployment-production.yaml
git add backend/k8s/redis.yaml backend/k8s/deployment-production.yaml

# 2. Коммитить
git commit -m "feat: add Redis StatefulSet and update deployment config"

# 3. Пушить
git push origin main

# 4. GitHub Actions автоматически развернёт оба ресурса
```

## 💡 Если всё ещё падает:

```bash
# Посмотреть логи приложения
kubectl logs -n demo-app -l app=demo-app --tail=100 -f

# Посмотреть события
kubectl get events -n demo-app --sort-by='.lastTimestamp'

# Описать pod
kubectl describe pod -n demo-app <pod-name>

# Проверить health endpoint напрямую
kubectl exec -n demo-app <pod-name> -- curl http://localhost:5000/api/health
```
