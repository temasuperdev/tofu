# 🔧 Исправление ошибки Ingress YAML

## ✅ Проблема и решение

### ❌ Ошибка при деплое:
```
error parsing backend/k8s/ingress.yaml: error converting YAML to JSON: yaml: line 5: did not find expected key
```

### 🔍 Причины найдены:
1. **Неправильный indent на строке 45**
   - Было: ` namespace: demo-app` (1 пробел)
   - Стало: `  namespace: demo-app` (2 пробела)

2. **Неправильно форматированная аннотация rate-limit**
   - Была многострочная YAML структура в аннотации (не поддерживается)
   - Удалена для упрощения конфигурации

### ✅ Что было исправлено:

1. **Исправлена аннотация rate-limit**
   ```yaml
   # Было:
   traefik.ingress.kubernetes.io/rate-limit: |
     extractorfunc: client.ip
     rateset:
       default:
         period: 10s
         average: 100
         burst: 200
   
   # Стало: Удалено из аннотаций (используется отдельный Middleware ресурс)
   ```

2. **Исправлен indent в Middleware metadata**
   ```yaml
   # Было:
   metadata:
     name: rate-limit
    namespace: demo-app  # ❌ Неправильный indent!
   
   # Стало:
   metadata:
     name: rate-limit
     namespace: demo-app  # ✅ Правильный indent
   ```

## 📊 Файлы обновлены:
- ✅ `backend/k8s/ingress.yaml` - исправлены ошибки YAML

## ✨ Проверка:
```
✅ YAML синтаксис корректен
✅ Найдено 5 документов:
   1. Ingress
   2. Middleware (https-redirectscheme)
   3. Middleware (rate-limit)
   4. ResourceQuota
   5. PodDisruptionBudget
```

## 🚀 Теперь готово для деплоя:
```bash
kubectl apply -f backend/k8s/ingress.yaml
# ✅ Без ошибок!
```

## 📝 Структура ingress.yaml:

### 1. Ingress (главный)
- Хост: `serv.temasuug.ru`
- TLS: `demo-app-tls`
- Роут: `/` → `demo-app:80`

### 2. Middleware (HTTPS redirect)
- Редирект HTTP → HTTPS
- Постоянный редирект (301)

### 3. Middleware (Rate Limiting)
- 100 запросов в среднем
- 200 всплесков
- IP-based rate limiting

### 4. ResourceQuota
- CPU requests: 5
- Memory requests: 5Gi
- CPU limits: 10
- Memory limits: 10Gi
- Max pods: 20

### 5. PodDisruptionBudget
- Минимум доступных pods: 2
- Для graceful shutdown

## ✅ Готово для GitHub push!
