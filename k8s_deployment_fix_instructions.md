# Инструкция по исправлению ошибки деплоя

## Проблема
При попытке деплоя приложения возникает ошибка:
```
Error creating: pods "demo-app-XXXXX-YYYYY" is forbidden: failed quota: demo-app-quota: must specify limits.cpu for: wait-for-redis; limits.memory for: wait-for-redis; requests.cpu for: wait-for-redis; requests.memory for: wait-for-redis
```

## Причина
Ошибка возникает потому, что в файле `backend/k8s/deployment-production.yaml` у initContainer `wait-for-redis` не указаны resource limits и requests, которые требуются настроенной ResourceQuota в namespace.

## Решение
Необходимо добавить ресурсы для initContainer `wait-for-redis` в файле `backend/k8s/deployment-production.yaml`.

### Шаги для исправления:

1. Откройте файл `backend/k8s/deployment-production.yaml`

2. Найдите секцию initContainers (примерно строка 114-138):

```yaml
# InitContainer для ожидания готовности Redis
initContainers:
  - name: wait-for-redis
    image: busybox:1.36
    command: ['sh', '-c']
    args:
      - |
        set -e
        echo "Waiting for Redis to be ready at demo-redis.demo-app.svc.cluster.local:6379..."
        COUNTER=0
        MAX_ATTEMPTS=90  # Увеличиваем до 90 попыток (3 минуты)
        while ! nc -z -w 2 demo-redis.demo-app.svc.cluster.local 6379 2>/dev/null; do
          COUNTER=$((COUNTER + 1))
          if [ $COUNTER -ge $MAX_ATTEMPTS ]; then
            echo "❌ Redis connection timeout after $MAX_ATTEMPTS attempts"
            echo "Debug: Trying DNS resolution..."
            nslookup demo-redis.demo-app.svc.cluster.local || echo "DNS lookup failed"
            exit 1
          fi
          if [ $((COUNTER % 5)) -eq 0 ]; then
            echo "Redis not ready, waiting... (attempt $COUNTER/$MAX_ATTEMPTS)"
          fi
          sleep 2
        done
        echo "✅ Redis is ready! (attempt $COUNTER/$MAX_ATTEMPTS)"
```

3. Добавьте после секции args следующую конфигурацию ресурсов:

```yaml
    args:
      - |
        set -e
        echo "Waiting for Redis to be ready at demo-redis.demo-app.svc.cluster.local:6379..."
        COUNTER=0
        MAX_ATTEMPTS=90  # Увеличиваем до 90 попыток (3 минуты)
        while ! nc -z -w 2 demo-redis.demo-app.svc.cluster.local 6379 2>/dev/null; do
          COUNTER=$((COUNTER + 1))
          if [ $COUNTER -ge $MAX_ATTEMPTS ]; then
            echo "❌ Redis connection timeout after $MAX_ATTEMPTS attempts"
            echo "Debug: Trying DNS resolution..."
            nslookup demo-redis.demo-app.svc.cluster.local || echo "DNS lookup failed"
            exit 1
          fi
          if [ $((COUNTER % 5)) -eq 0 ]; then
            echo "Redis not ready, waiting... (attempt $COUNTER/$MAX_ATTEMPTS)"
          fi
          sleep 2
        done
        echo "✅ Redis is ready! (attempt $COUNTER/$MAX_ATTEMPTS)"
    resources:
      requests:
        cpu: 10m
        memory: 16Mi
      limits:
        cpu: 50m
        memory: 32Mi
```

## Альтернативное решение
Вы можете использовать файл `backend/k8s/deployment-production-fixed.yaml`, который уже содержит правильную конфигурацию с необходимыми resource limits и requests для initContainer.

## Проверка
После внесения изменений примените обновленный манифест:

```bash
kubectl apply -f backend/k8s/deployment-production.yaml
```

Или если используете исправленный файл:

```bash
kubectl apply -f backend/k8s/deployment-production-fixed.yaml
```

## Значения ресурсов
- `requests.cpu: 10m` - минимальное количество CPU, которое будет зарезервировано для контейнера
- `requests.memory: 16Mi` - минимальный объем памяти, который будет зарезервирован для контейнера
- `limits.cpu: 50m` - максимальное количество CPU, которое может использовать контейнер
- `limits.memory: 32Mi` - максимальный объем памяти, который может использовать контейнер

Эти значения минимальны и подходят для initContainer, который просто ждет готовности Redis.