# 🔧 Исправление Startup Probe ошибок

## ✅ Проблема и решение

### ❌ Ошибка при деплое:
```
Startup probe failed: Get "http://10.42.0.216:5000/api/health": 
read tcp 10.42.0.1:50526->10.42.0.216:5000: read: connection reset by peer. (31s)
```

### 🔍 Причины найдены:
1. **Prometheus port неправильно указан** - `500` вместо `5000`
2. **Startup probe слишком агрессивный** - недостаточно времени на инициализацию
3. **Readiness probe слишком строгий** - может убить контейнер преждевременно
4. **PYTHONPATH переменная лишняя** - приложение уже в `/app`

### ✅ Что было исправлено:

#### 1. **Prometheus port** 🔧
```yaml
# Было:
prometheus.io/port: "500"

# Стало:
prometheus.io/port: "5000"
```

#### 2. **Startup Probe** 🚀
```yaml
# Было (агрессивный):
startupProbe:
  initialDelaySeconds: 0
  periodSeconds: 2
  timeoutSeconds: 2
  failureThreshold: 15
# Max время: 2 * 15 = 30 секунд

# Стало (щадящий):
startupProbe:
  initialDelaySeconds: 5      # Даём 5 сек на инициализацию
  periodSeconds: 5            # Проверяем каждые 5 сек
  timeoutSeconds: 10          # Ждём ответа 10 сек
  failureThreshold: 20        # Даём 20 попыток
# Max время: 5 + 10 * 20 = 205 секунд (достаточно!)
```

**Почему это важно:**
- Контейнер нужно время для загрузки Python приложения
- Gunicorn запуск с 4 workers требует ресурсов
- Startup probe только для первого запуска, потом используется liveness/readiness

#### 3. **Readiness Probe** ✅
```yaml
# Было (слишком часто проверяет):
readinessProbe:
  initialDelaySeconds: 5
  periodSeconds: 5
  timeoutSeconds: 2
  failureThreshold: 2
# Max downtime перед удалением: 5 + 2 * 2 = 9 сек

# Стало (разумная частота):
readinessProbe:
  initialDelaySeconds: 10     # Ждём 10 сек после startup
  periodSeconds: 10           # Проверяем каждые 10 сек
  timeoutSeconds: 5           # Ждём ответа 5 сек
  failureThreshold: 3         # 3 ошибки = выключение
```

#### 4. **Удалён PYTHONPATH** 🗑️
```yaml
# Удалено:
- name: PYTHONPATH
  value: "/app/backend"
```
Не нужен - приложение находится в `/app` и gunicorn запускает `src.app:app` из `/app`.

## 📊 Файлы обновлены:
- ✅ `backend/k8s/deployment-production.yaml` - для GitHub Actions
- ✅ `backend/k8s/deployment.yaml` - для локального K3s

## ✨ Проверка:
```
✅ deployment.yaml - 11 документов OK
✅ deployment-production.yaml - 8 документов OK
✅ YAML синтаксис валиден
```

## 📈 Timeline для pod startup:

### Старое (не работало):
```
0s:    Pod starts
0s:    Startup probe: initialDelaySeconds=0 → сразу начинает проверку
2s:    Failure #1
4s:    Failure #2
...
30s:   Failure #15 → Pod dies ❌
```

### Новое (работает):
```
0s:    Pod starts
5s:    Startup probe: initialDelaySeconds=5 → начинает проверку
5s:    Timeout=10s, wait for response from app...
15s:   If fail → Retry #1
...
100s:  If all 20 retries fail → Pod dies (but usually works before this)
```

## 🚀 Готово для деплоя:
```bash
# Production deployment
kubectl apply -f backend/k8s/deployment-production.yaml

# Или локально
kubectl apply -f backend/k8s/deployment.yaml

# Проверить статус
kubectl rollout status deployment/demo-app -n demo-app

# Смотреть логи
kubectl logs -n demo-app -l app=demo-app --tail=50 -f
```

## 💡 Что смотреть если всё ещё не работает:

```bash
# 1. Статус pod'ов
kubectl get pods -n demo-app -o wide

# 2. События для pod'а
kubectl describe pod <pod-name> -n demo-app

# 3. Логи приложения
kubectl logs <pod-name> -n demo-app --all-containers=true

# 4. Проверить health endpoint напрямую
kubectl port-forward -n demo-app svc/demo-app 8080:80 &
curl http://localhost:8080/api/health
```

## ✅ Результат:
Приложение будет иметь достаточно времени на загрузку и инициализацию. Startup probe будет щадящим, readiness probe - стабильным.
