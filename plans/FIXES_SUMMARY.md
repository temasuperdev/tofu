# Сводка исправлений для Kubernetes манифестов

## Выполненные изменения

1. **Файл `backend/k8s/deployment-production.yaml`**:
   - Добавлены resource limits и requests для initContainer `wait-for-redis`
   - Теперь содержит:
     ```yaml
     resources:
       requests:
         cpu: 10m
         memory: 16Mi
       limits:
         cpu: 50m
         memory: 32Mi
     ```

2. **Файл `backend/k8s/deployment-production-fixed.yaml`**:
   - Уже содержал правильную конфигурацию с resource limits для initContainer

3. **Файлы `backend/k8s/deployment.yaml`, `backend/k8s/deployment-simple.yaml`, `backend/k8s/deployment-working.yaml`**:
   - Не содержат initContainers, поэтому не требовали изменений

## Результат

Все deployment файлы теперь соответствуют требованиям ResourceQuota и содержат необходимые resource limits для всех контейнеров, включая initContainers. Ошибка деплоя больше не должна возникать.

## Рекомендации

Для деплоя приложения рекомендуется использовать обновленный файл:
```bash
kubectl apply -f backend/k8s/deployment-production.yaml
```

Или альтернативно:
```bash
kubectl apply -f backend/k8s/deployment-production-fixed.yaml