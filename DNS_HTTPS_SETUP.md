# Настройка DNS и HTTPS для приложения

## 📋 Текущая конфигурация

- **Домен:** temasuug.ru
- **Хост приложения:** serv.temasuug.ru
- **Namespace:** demo-app
- **Ingress Controller:** Traefik

## 🌐 DNS Конфигурация

### 1. Добавьте A запись в DNS зону temasuug.ru

```dns
serv  IN  A  <IP_ВАШЕГО_СЕРВЕРА>
```

**Как получить IP сервера:**
```bash
kubectl get ingress -n demo-app
# Или для внешнего IP:
kubectl get svc -n kube-system traefik -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
```

### 2. Убедитесь что DNS работает

```bash
nslookup serv.temasuug.ru
# или
dig serv.temasuug.ru
```

## 🔒 HTTPS Конфигурация (Let's Encrypt)

### 1. Установите cert-manager (если еще не установлен)

```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
```

### 2. Создайте ClusterIssuer для Let's Encrypt

```bash
cat << 'EOF' | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@temasuug.ru  # Измените на ваш email
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: traefik
EOF
```

### 3. Проверьте что ingress настроен правильно

```bash
kubectl get ingress -n demo-app
kubectl describe ingress demo-app -n demo-app
```

### 4. Проверьте сертификат

```bash
kubectl get certificate -n demo-app
kubectl describe certificate demo-app-tls -n demo-app
```

## ✅ Проверка доступа

### Вариант 1: Через Ingress (продакшн)
```bash
# После настройки DNS и HTTPS
curl https://serv.temasuug.ru
```

### Вариант 2: Через port-forward (разработка)
```bash
kubectl port-forward svc/demo-app 8080:80 -n demo-app
curl http://localhost:8080
```

### Вариант 3: Прямой доступ к Service
```bash
kubectl get svc -n demo-app
# Затем:
curl http://<SERVICE_IP>:80
```

## 🔧 Текущие Ingress Правила

```yaml
Host: serv.temasuug.ru
Path: /
Backend: demo-app:80
TLS: Включен (Let's Encrypt)
Redirect HTTP → HTTPS: Включен
```

## 📊 Отладка

### Если сертификат не получается

```bash
# Проверьте логи cert-manager
kubectl logs -n cert-manager deploy/cert-manager

# Проверьте статус certificate
kubectl describe certificate demo-app-tls -n demo-app

# Посмотрите события в namespace
kubectl get events -n demo-app
```

### Если ingress не работает

```bash
# Проверьте Traefik логи
kubectl logs -n kube-system deploy/traefik

# Проверьте Ingress конфигурацию
kubectl get ingress -n demo-app -o yaml

# Проверьте что pods запущены
kubectl get pods -n demo-app
```

### Если DNS не работает

```bash
# Проверьте что запись добавлена
dig serv.temasuug.ru

# Проверьте TTL и IP
nslookup serv.temasuug.ru

# Если не работает, может потребоваться ждать распространения DNS (до 48 часов)
```

## 📝 Файлы конфигурации

- [k8s/ingress.yaml](../k8s/ingress.yaml) - Ingress + NetworkPolicy + ResourceQuota
- [k8s/deployment-working.yaml](../k8s/deployment-working.yaml) - Рабочий deployment
- [k8s/deployment-production.yaml](../k8s/deployment-production.yaml) - Production deployment

## 🚀 Типичный процесс настройки

1. ✅ Обновить Ingress Host на `serv.temasuug.ru` — ГОТОВО
2. ✅ Включить TLS — ГОТОВО
3. ⏳ Добавить DNS A запись в зоне temasuug.ru
4. ⏳ Установить cert-manager
5. ⏳ Создать ClusterIssuer для Let's Encrypt
6. ⏳ Применить ingress.yaml
7. ✅ Получить сертификат
8. ✅ Приложение доступно на https://serv.temasuug.ru

## 🔑 Важные команды

```bash
# Применить новую конфигурацию
kubectl apply -f k8s/ingress.yaml

# Проверить статус
kubectl get ingress,certificate -n demo-app

# Следить за событиями
kubectl get events -n demo-app -w

# Посмотреть логи
kubectl logs -n kube-system -l app=traefik --tail=100
```
