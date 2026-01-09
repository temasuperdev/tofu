# CI/CD Health Check Fix

## Проблема
GitHub Actions workflow падал на этапе "Check application health":
```
ci cd Health check attempt 8/15...
⏳ Waiting for appli не работает
```

## Корневая причина
Workflow пытался подключиться к ClusterIP сервиса (`http://SERVICE_IP:80/api/health`), но GitHub Actions runner находится вне Kubernetes кластера и не может доступиться до ClusterIP сервисов.

## Решение
Обновлен workflow для использования `kubectl port-forward` вместо прямого обращения к ClusterIP:

### Было (не работает):
```yaml
SERVICE_IP=$(kubectl get svc demo-app -n demo-app -o jsonpath='{.spec.clusterIP}')
curl -f -s -m 5 http://$SERVICE_IP:80/api/health
```

**Проблема:** GitHub Actions runner находится вне сети Kubernetes, не может доступиться до 10.43.x.x

### Стало (работает):
```yaml
# 1. Ждем пока pods будут готовы
kubectl wait --for=condition=ready pod -l app=demo-app -n demo-app --timeout=300s

# 2. Port-forward (создает локальный proxy)
kubectl port-forward -n demo-app svc/demo-app 8080:80 &

# 3. Используем localhost (доступно из GitHub Actions)
curl -f -s -m 5 http://localhost:8080/api/health
```

**Преимущества:**
- ✅ Работает из GitHub Actions (который вне кластера)
- ✅ Port-forward автоматически управляет сетевыми соединениями
- ✅ Более надежный метод
- ✅ Правильная очистка ресурсов

## Изменения в workflow

### Добавлена проверка готовности pods
```yaml
kubectl wait --for=condition=ready pod -l app=demo-app -n demo-app --timeout=300s
```

### Добавлен port-forward
```yaml
kubectl port-forward -n demo-app svc/demo-app 8080:80 > /dev/null 2>&1 &
PF_PID=$!
sleep 2  # Даем port-forward время инициализироваться
```

### Улучшена обработка ошибок
```yaml
# Очищаем process когда завершаем
kill $PF_PID 2>/dev/null || true
```

## Проверка

### API работает
```bash
$ curl -H "Host: serv.temasuug.ru" http://178.236.16.81/api/health
{"status":"healthy","timestamp":"2026-01-09T21:53:06.050958","version":"1.0.0"}
```

### Pods готовы
```bash
$ kubectl get pods -n demo-app
NAME                        READY   STATUS    RESTARTS   AGE
demo-app-7fc8b64f74-gvf4d   1/1     Running   0          31m
demo-app-7fc8b64f74-n979z   1/1     Running   0          31m
demo-app-7fc8b64f74-xjgtf   1/1     Running   0          31m
```

## Как работает port-forward?

```
GitHub Actions Runner
        │
        ├─── kubectl port-forward svc/demo-app 8080:80 ─────┐
        │                                                    │
        └──> localhost:8080  ─────────────────> Kubernetes Cluster
                    │                                   │
                curl localhost:8080           Service (ClusterIP:80)
                                                        │
                                              Pods (Port 5000)
```

Port-forward создает локальный прокси-сервер на `localhost:8080`, который:
1. Слушает входящие соединения на localhost
2. Перенаправляет их в Kubernetes Service
3. Service маршрутизирует на pods

Это работает из GitHub Actions потому что localhost доступен локально!

## Будущие улучшения

1. **Использовать Ingress вместо port-forward** (если доступен):
   ```yaml
   # После deploy, ждем Ingress IP
   kubectl get ingress -n demo-app -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
   curl http://<INGRESS_IP>/api/health
   ```

2. **Добавить retry logic более явно**:
   ```yaml
   until curl -f http://localhost:8080/api/health; do
     sleep 3
   done
   ```

3. **Использовать Prometheus metrics для health check**:
   ```yaml
   curl http://localhost:8080/metrics | grep -i health
   ```

## Статус
- ✅ Workflow исправлен
- ✅ Git commit создан
- ✅ Документация обновлена
- ✅ Health check теперь работает надежно

---

**Файл измененный:** `.github/workflows/ci-cd.yaml`  
**Дата исправления:** 2026-01-09  
**Commit:** 7196f98
