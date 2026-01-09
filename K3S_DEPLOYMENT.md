# K3s Deployment Guide (Русский)

## 🚀 Развертывание в K3s кластер

Это подробное руководство по развертыванию приложения в K3s.

## 📋 Требования

```bash
# K3s установлен и работает
k3s --version

# kubectl установлен
kubectl version --client

# kubeconfig настроен
cat $KUBECONFIG
```

## 🏃 Быстрое развертывание (3 минуты)

### 1. Убедитесь в подключении
```bash
kubectl cluster-info
# Output:
# Kubernetes control plane is running at https://...
# CoreDNS is running at https://...
# Metrics-server is running at https://...
```

### 2. Примените манифесты
```bash
# Обновите image в deployment.yaml если нужно
IMAGE_REGISTRY="ghcr.io"
IMAGE_NAME="yourname/tofu"  # Измените на свое
IMAGE_TAG="latest"

# Применить deployment
sed -e "s|IMAGE_REGISTRY|${IMAGE_REGISTRY}|g" \
    -e "s|IMAGE_NAME|${IMAGE_NAME}|g" \
    -e "s|IMAGE_TAG|${IMAGE_TAG}|g" \
    k8s/deployment.yaml | kubectl apply -f -

# Применить ingress
kubectl apply -f k8s/ingress.yaml

echo "✅ Манифесты применены"
```

### 3. Проверьте статус
```bash
# Ждите, пока pods станут Running (1-2 минуты)
watch kubectl get pods -n demo-app

# Или одноразово
kubectl get pods -n demo-app
kubectl get svc -n demo-app
kubectl get ingress -n demo-app
```

### 4. Доступ к приложению
```bash
# Локальный доступ через port-forward
kubectl port-forward svc/demo-app 8080:80 -n demo-app

# Откройте в браузере: http://localhost:8080
# Или в другом терминале:
curl http://localhost:8080/api/health | jq .
```

---

## 📖 Подробное объяснение

### Что создается в K3s?

#### 1. Namespace
```bash
kubectl get namespace demo-app
# Изолирует приложение от других
```

#### 2. Deployment
```bash
kubectl get deployment -n demo-app
kubectl describe deployment demo-app -n demo-app

# 3 реплики (подов) для высокой доступности
# Каждый под запускает ваше Flask приложение
```

#### 3. Service
```bash
kubectl get svc -n demo-app

# Внутренний сервис для доступа к подам
# Type: ClusterIP (доступен только внутри кластера)
# Port: 80 → targetPort: 5000
```

#### 4. Ingress
```bash
kubectl get ingress -n demo-app
kubectl describe ingress demo-app -n demo-app

# Внешний доступ к приложению
# Использует Traefik (встроен в K3s)
# Host: app.local (измените на свой домен)
```

#### 5. HPA (Horizontal Pod Autoscaler)
```bash
kubectl get hpa -n demo-app
kubectl describe hpa demo-app-hpa -n demo-app

# Автоматически масштабирует pods:
# - Min: 3, Max: 10
# - На основе CPU (70%) и Memory (80%)
```

#### 6. ConfigMap
```bash
kubectl get configmap -n demo-app
kubectl describe configmap app-config -n demo-app

# Хранит переменные окружения
```

#### 7. RBAC (Role-Based Access Control)
```bash
kubectl get serviceaccount -n demo-app
kubectl get role -n demo-app
kubectl get rolebinding -n demo-app

# Определяет права доступа для приложения
```

---

## 🔍 Мониторинг

### Просмотр логов

```bash
# Логи всех подов
kubectl logs -l app=demo-app -n demo-app

# Логи конкретного пода
kubectl logs pod/demo-app-xyz -n demo-app

# Следить за логами (tail -f)
kubectl logs -f deployment/demo-app -n demo-app

# Логи за последний час
kubectl logs deployment/demo-app -n demo-app --since=1h

# Экспортировать логи
kubectl logs deployment/demo-app -n demo-app > logs.txt
```

### Проверка здоровья

```bash
# Health endpoint (для K8s probes)
curl http://localhost:8080/api/health

# Информация о приложении
curl http://localhost:8080/api/info | jq .

# Метрики (Prometheus format)
curl http://localhost:8080/metrics

# Ping
curl http://localhost:8080/api/ping
```

### Статус deployment

```bash
# Текущий статус
kubectl rollout status deployment/demo-app -n demo-app

# История
kubectl rollout history deployment/demo-app -n demo-app

# Описание
kubectl describe deployment demo-app -n demo-app
```

### Информация о подах

```bash
# Все события
kubectl get events -n demo-app

# Описание пода
kubectl describe pod <pod-name> -n demo-app

# Доступ в контейнер
kubectl exec -it pod/<pod-name> -n demo-app -- /bin/bash

# Использование ресурсов
kubectl top pods -n demo-app
kubectl top nodes
```

---

## 🔄 Обновление приложения

### Способ 1: Через kubectl set image (быстрый)
```bash
kubectl set image deployment/demo-app \
  app=ghcr.io/yourname/tofu:new-tag \
  -n demo-app

# Проверить
kubectl rollout status deployment/demo-app -n demo-app
```

### Способ 2: Через kubectl patch
```bash
kubectl patch deployment demo-app \
  -n demo-app \
  -p '{"spec":{"template":{"spec":{"containers":[{"name":"app","image":"ghcr.io/yourname/tofu:new-tag"}]}}}}'
```

### Способ 3: Через kubectl apply (рекомендуется)
```bash
# Обновить YAML
sed -i 's|old-tag|new-tag|g' k8s/deployment.yaml

# Применить
kubectl apply -f k8s/deployment.yaml

# Проверить
kubectl rollout status deployment/demo-app -n demo-app
```

### Откат предыдущей версии
```bash
# Откатиться на шаг назад
kubectl rollout undo deployment/demo-app -n demo-app

# Откатиться на конкретную ревизию
kubectl rollout undo deployment/demo-app --to-revision=2 -n demo-app
```

---

## 🧪 Тестирование

### Port Forward
```bash
# В отдельном терминале
kubectl port-forward svc/demo-app 8080:80 -n demo-app

# В другом терминале
curl http://localhost:8080/
```

### Через Service IP внутри кластера
```bash
# Запустить тестовый pod
kubectl run test-pod --image=curlimages/curl -it --rm -n demo-app -- \
  curl http://demo-app.demo-app.svc.cluster.local/api/health
```

### LoadGen для тестирования HPA
```bash
# Создать нагрузку
kubectl run -i --tty load-generator --rm --image=busybox --restart=Never -n demo-app -- \
  /bin/sh -c "while sleep 0.01; do wget -q -O- http://demo-app.demo-app.svc.cluster.local; done"

# В другом терминале смотрите масштабирование
watch kubectl get hpa demo-app-hpa -n demo-app
```

---

## ⚠️ Troubleshooting

### Pod не запускается

```bash
# Смотрите описание
kubectl describe pod <pod-name> -n demo-app

# Смотрите логи
kubectl logs <pod-name> -n demo-app

# Проверьте события
kubectl get events -n demo-app

# Возможные причины:
# - Image pull error → Проверьте registry доступ
# - CrashLoopBackOff → Ошибка в приложении
# - Pending → Нет ресурсов на ноде
```

### Image Pull Error

```bash
# Проверьте image существует
docker pull ghcr.io/yourname/tofu:tag

# Создайте secret для приватного registry
kubectl create secret docker-registry regcred \
  --docker-server=ghcr.io \
  --docker-username=<username> \
  --docker-password=<token> \
  -n demo-app

# Обновите deployment использовать secret
```

### Out of Memory

```bash
# Смотрите использование памяти
kubectl top pods -n demo-app

# Увеличьте лимиты
kubectl set resources deployment demo-app \
  -n demo-app \
  --limits=memory=1Gi,cpu=1 \
  --requests=memory=256Mi,cpu=250m
```

### Service не доступен

```bash
# Проверьте endpoints
kubectl get endpoints -n demo-app

# Проверьте service selector
kubectl get svc demo-app -n demo-app -o yaml | grep selector -A 2

# Проверьте pods label
kubectl get pods -n demo-app --show-labels
```

### Ingress не работает

```bash
# Проверьте ingress
kubectl get ingress -n demo-app
kubectl describe ingress demo-app -n demo-app

# Проверьте traefik работает
kubectl get pods -n kube-system | grep traefik

# Добавьте hosts entry (локально)
echo "127.0.0.1 app.local" | sudo tee -a /etc/hosts
```

---

## 🧹 Очистка

### Удалить namespace (всё приложение)
```bash
kubectl delete namespace demo-app
```

### Удалить отдельные ресурсы
```bash
kubectl delete deployment demo-app -n demo-app
kubectl delete service demo-app -n demo-app
kubectl delete ingress demo-app -n demo-app
```

---

## 📊 Полезные команды

```bash
# Общая информация
kubectl cluster-info
kubectl get nodes
kubectl get namespace

# Ресурсы приложения
kubectl get all -n demo-app
kubectl get pods,svc,ingress -n demo-app

# Мониторинг
kubectl top nodes
kubectl top pods -n demo-app

# Логирование
kubectl logs -f deployment/demo-app -n demo-app
kubectl logs --tail=100 deployment/demo-app -n demo-app

# Отладка
kubectl exec -it pod/<name> -n demo-app -- /bin/bash
kubectl describe pod <name> -n demo-app

# YAML экспорт
kubectl get deployment demo-app -n demo-app -o yaml
kubectl get all -n demo-app -o yaml > backup.yaml
```

---

## 📚 Дополнительные ресурсы

- [K3s documentation](https://docs.k3s.io/)
- [Kubernetes kubectl cheatsheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
- [Traefik Ingress Controller](https://doc.traefik.io/traefik/providers/kubernetes-ingress/)

---

## ✅ Результат

После выполнения этих шагов у вас будет:
- ✅ Запущенное приложение в K3s
- ✅ 3 replicas для высокой доступности
- ✅ Автоматическое масштабирование (HPA)
- ✅ Внешний доступ через Ingress
- ✅ Health checks (liveness/readiness)
- ✅ Логирование и мониторинг
- ✅ Security policies (Network Policy, RBAC)

**Поздравляем! Ваше приложение работает в K3s! 🎉**
