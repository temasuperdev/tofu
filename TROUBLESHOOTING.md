# Руководство по решению проблем развертывания

## Проблема: CrashLoopBackOff в K3s через GitHub Actions

### Симптомы
```
Back-off restarting failed container app in pod demo-app-xxx (30s)
Status: CrashLoopBackOff
```

### Возможные причины и решения

## 1. Образ не может быть загружен
**Признак:** `ImagePullBackOff`
```bash
kubectl describe pod <pod-name> -n demo-app
```

**Решение:**
- Проверьте что образ успешно отправлен в GHCR
- Убедитесь что GitHub Actions workflow выполнился успешно (этап build)
- Проверьте что у вас есть доступ к GHCR

## 2. Приложение падает при запуске
**Признак:** `CrashLoopBackOff` сразу после запуска
```bash
kubectl logs -f deployment/demo-app -n demo-app
```

**Распространенные ошибки:**

### Ошибка: "ModuleNotFoundError: No module named 'src'"
**Решение:** 
- Убедитесь что `setup.py` присутствует
- В GitHub Actions установите пакет: `pip install -e .`

### Ошибка: "Failed to bind to port 5000"
**Решение:**
- Проверьте что EXPOSE 5000 в Dockerfile
- Убедитесь что containerPort: 5000 в deployment

### Ошибка: "Permission denied" для /tmp
**Решение:**
- Отключите `readOnlyRootFilesystem: true` в securityContext
- Или добавьте volumeMount для /tmp

## 3. Здоровье проверки (Health Checks) падают
**Признак:** Поды доступны но не готовы
```bash
kubectl get pods -n demo-app
# STATUS: Running, но READY: 0/1
```

**Решение:**
```bash
# Проверьте endpoints вручную
kubectl port-forward svc/demo-app 8080:80 -n demo-app
curl http://localhost:8080/api/health
```

## 4. Service не доступен
**Признак:** Service существует но не отвечает
```bash
kubectl get svc -n demo-app
```

**Решение:**
```bash
# Проверьте endpoints
kubectl get endpoints -n demo-app

# Проверьте selector matching
kubectl get pods -n demo-app -L app
```

## Диагностические команды

### 1. Полная диагностика
```bash
# Проверить все ресурсы
kubectl get all -n demo-app

# Подробно о каждом поде
kubectl describe pods -n demo-app

# Логи всех контейнеров
kubectl logs -n demo-app --all-containers=true --tail=100

# События в namespace
kubectl get events -n demo-app --sort-by='.lastTimestamp'
```

### 2. Проверить образ
```bash
# Проверить что образ есть в GHCR
docker pull ghcr.io/<your-username>/<repo>:<tag>

# Или локально в K3s
crictl images | grep demo-app
```

### 3. Проверить конфигурацию
```bash
# ConfigMap
kubectl get configmap -n demo-app
kubectl describe configmap app-config -n demo-app

# Переменные окружения в поде
kubectl exec -it <pod-name> -n demo-app -- env
```

## Локальное тестирование перед пушем в GitHub

### 1. Протестируйте образ локально
```bash
# Соберите образ
docker build -f docker/Dockerfile -t demo-app:test .

# Запустите контейнер
docker run -p 5000:5000 demo-app:test

# Проверьте что работает
curl http://localhost:5000/api/health
```

### 2. Тестируйте в K3s локально
```bash
# Используйте deployment-simple.yaml для быстрой проверки
kubectl apply -f k8s/deployment-simple.yaml

# Проверьте статус
kubectl get pods -n demo-app

# Если работает - проверьте production deployment
kubectl delete namespace demo-app
kubectl apply -f k8s/deployment-production.yaml
```

## Проверка GitHub Actions workflow

### 1. Посмотрите логи workflow
- GitHub → Actions → Выберите последний запуск
- Разверните каждый шаг (особенно "Build Docker image")

### 2. Проверьте что собрано
```bash
# После успешного build-а в GitHub Actions
docker pull ghcr.io/<owner>/<repo>:latest
docker run -it ghcr.io/<owner>/<repo>:latest bash
```

## Типичные проблемы и быстрые решения

| Проблема | Команда для проверки | Решение |
|----------|---------------------|---------|
| CrashLoopBackOff | `kubectl logs -f pod <name> -n demo-app` | Проверьте логи ошибки и исправьте код |
| ImagePullBackOff | `kubectl describe pod <name> -n demo-app` | Убедитесь что образ в GHCR существует |
| Pending | `kubectl describe pod <name> -n demo-app` | Может не хватать ресурсов или нет узлов |
| Service не доступен | `kubectl get endpoints -n demo-app` | Поды могут быть не готовы |
| Port conflict | `kubectl logs svc/demo-app -n demo-app` | Проверьте что порт 5000 не занят |

## Восстановление после ошибки

### 1. Быстро проверить статус
```bash
bash /root/tofu/deploy-local-k3s.sh
```

### 2. Очистить и переразвернуть
```bash
kubectl delete namespace demo-app
sleep 2
kubectl apply -f k8s/deployment-production.yaml
```

### 3. Следить за прогрессом
```bash
watch 'kubectl get pods -n demo-app'
```

## Полезные команды для отладки

```bash
# Вход в pod для отладки
kubectl exec -it <pod-name> -n demo-app -- bash

# Скопировать файлы из pod
kubectl cp demo-app/<pod-name>:/app/file.txt ./file.txt

# Переаправить порт для локального тестирования  
kubectl port-forward pod/<pod-name> 8080:5000 -n demo-app

# Смотреть логи в реальном времени
kubectl logs -f deployment/demo-app -n demo-app

# Перезагрузить deployment
kubectl rollout restart deployment/demo-app -n demo-app

# Скейлировать вручную
kubectl scale deployment demo-app --replicas=1 -n demo-app
```

## Быстрый чек-лист

- [ ] Dockerfile строится без ошибок
- [ ] Контейнер запускается локально: `docker run -p 5000:5000 image:tag`
- [ ] Health endpoint доступен: `curl http://localhost:5000/api/health`
- [ ] setup.py присутствует в проекте
- [ ] requirements.txt содержит все зависимости
- [ ] GitHub Actions workflow завершился успешно
- [ ] Образ присутствует в GHCR
- [ ] K3s cluster работает: `kubectl cluster-info`
- [ ] Namespace существует: `kubectl get ns demo-app`
- [ ] Deployment создан: `kubectl get deployment -n demo-app`
- [ ] Поды запустились: `kubectl get pods -n demo-app`
- [ ] Service доступен: `kubectl get svc -n demo-app`
