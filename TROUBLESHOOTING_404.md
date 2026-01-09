# 404 Not Found - Решено! 🎉

## Проблема
Приложение возвращало 404 ошибку при обращении через Ingress Traefik на `serv.temasuug.ru`.

## Корневые Причины (выявлены)

### 1. **NetworkPolicy блокировал трафик Traefik** (КРИТИЧНАЯ)
- NetworkPolicy в namespace `demo-app` разрешал трафик только на порты 80 и 443
- Приложение Flask слушает на порту **5000**
- Traefik работает в namespace `kube-system` и не мог подключиться к pod на порту 5000
- **Решение**: NetworkPolicy обновлена для разрешения трафика на порт 5000

### 2. **Неправильное использование Ingress**
- K3s использует Traefik 3.5.1 с поддержкой собственного API `IngressRoute`
- Стандартный Kubernetes `Ingress` работает, но `IngressRoute` предпочтительнее
- **Решение**: Добавлен обоих - `Ingress` и `IngressRoute` для максимальной совместимости

### 3. **TLS конфигурация без cert-manager**
- Ingress содержал TLS аннотации для cert-manager, но cert-manager не установлен
- **Решение**: TLS аннотации удалены из основной конфигурации (пока)

## Реализованные Исправления

### 1. Обновлена NetworkPolicy (`k8s/networkpolicy.yaml`)
```yaml
ingress:
  # Разрешить весь входящий трафик на порт 5000
  - from:
      - namespaceSelector: {}
    ports:
      - protocol: TCP
        port: 5000
```

**Ключевые изменения:**
- `namespaceSelector: {}` - позволяет трафик от всех namespaces (включая `kube-system`)
- `port: 5000` - явно разрешен порт где слушает Flask приложение

### 2. Очищена конфигурация Ingress (`k8s/ingress.yaml`)
- Удалены TLS аннотации для cert-manager (временно)
- Удалены force-ssl-redirect аннотации
- Оставлены только базовые параметры маршрутизации

### 3. Добавлен IngressRoute (`k8s/ingressroute.yaml`)
```yaml
apiVersion: traefik.io/v1alpha1
kind: IngressRoute
metadata:
  name: demo-app
  namespace: demo-app
spec:
  entryPoints:
    - web
  routes:
    - match: Host(`serv.temasuug.ru`)
      kind: Rule
      services:
        - name: demo-app
          port: 80
```

## Проверка

### ✅ Локальное тестирование
```bash
# Через nodePort Traefik (32463)
curl -H "Host: serv.temasuug.ru" http://127.0.0.1:32463/
# Status: 200 OK ✓

# Через Ingress IP адрес
curl -H "Host: serv.temasuug.ru" http://178.236.16.81/
# Status: 200 OK ✓
```

### ✅ API endpoints работают
```bash
curl -H "Host: serv.temasuug.ru" http://178.236.16.81/api/health
# {"status":"healthy",...} ✓

curl -H "Host: serv.temasuug.ru" http://178.236.16.81/api/info
# {"environment":"production",...} ✓
```

### ✅ Pod endpoints корректны
```bash
kubectl get endpoints -n demo-app demo-app
# NAME       ENDPOINTS                                         
# demo-app   10.42.0.50:5000,10.42.0.51:5000,10.42.0.52:5000 ✓
```

## Следующие Шаги

### Для HTTPS (опционально)
1. Установить cert-manager:
   ```bash
   helm repo add jetstack https://charts.jetstack.io
   helm install cert-manager jetstack/cert-manager -n cert-manager --create-namespace
   ```

2. Создать ClusterIssuer для Let's Encrypt:
   ```bash
   kubectl apply -f k8s/cert-manager-issuer.yaml
   ```

3. Добавить TLS в Ingress

### Для DNS
1. Добавить A record в DNS зону `temasuug.ru`:
   ```
   serv IN A 178.236.16.81
   ```

2. Тогда можно обращаться по имени:
   ```bash
   curl https://serv.temasuug.ru/
   ```

## Выводы

**Основной урок:** NetworkPolicy может полностью блокировать трафик между namespaces, если неправильно настроен. В production среде нужно тщательно проверять NetworkPolicy при инсталляции Ingress Controller.

**Найденные версии:**
- K3s: 1.34
- Traefik: 3.5.1 (встроен в K3s)
- Flask: 2.3+
- Gunicorn: 22.0.0

**Статус Deployment:**
- ✅ Приложение работает
- ✅ Ingress маршрутизирует трафик
- ✅ Все 3 replicas доступны
- ✅ Health checks работают
- ⏳ HTTPS (требует cert-manager)
- ⏳ DNS (требует DNS записи от пользователя)
