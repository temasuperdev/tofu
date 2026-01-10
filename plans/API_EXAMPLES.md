# Примеры использования API

В этом документе приведены примеры использования API приложения.

## Содержание
- [Получение информации о приложении](#получение-информации-о-приложении)
- [Проверка состояния приложения](#проверка-состояния-приложения)
- [Отправка сообщения](#отправка-сообщения)
- [Получение метрик](#получение-метрик)
- [Проверка связи](#проверка-связи)

## Получение информации о приложении

### Запрос
```
GET /api/info
```

### Пример с cURL
```bash
curl -X GET http://localhost:5000/api/info
```

### Пример с Python (requests)
```python
import requests

response = requests.get("http://localhost:5000/api/info")
print(response.json())
```

### Ответ
```json
{
  "name": "K3s CI/CD Demo",
  "version": "1.0.0",
  "environment": "development",
  "pod_name": "unknown",
  "timestamp": "2023-10-01T12:34:56.789123"
}
```

## Проверка состояния приложения

### Запрос
```
GET /api/health
```

### Пример с cURL
```bash
curl -X GET http://localhost:5000/api/health
```

### Пример с Python (requests)
```python
import requests

response = requests.get("http://localhost:5000/api/health")
print(response.json())
```

### Ответ
```json
{
  "status": "healthy",
  "timestamp": "2023-10-01T12:34:56.789123",
  "version": "1.0.0"
}
```

## Отправка сообщения

### Запрос
```
POST /api/message
Content-Type: application/json

{
  "message": "Текст сообщения (до 100 символов)"
}
```

### Пример с cURL
```bash
curl -X POST http://localhost:5000/api/message \
  -H "Content-Type: application/json" \
  -d '{"message": "Привет, это тестовое сообщение!"}'
```

### Пример с Python (requests)
```python
import requests

data = {"message": "Привет, это тестовое сообщение!"}
response = requests.post("http://localhost:5000/api/message", json=data)
print(response.json())
```

### Успешный ответ
```
Status: 201 Created
```

```json
{
  "success": true,
  "message": "Сообщение получено: Привет, это тестовое сообщение!",
  "processed_at": "2023-10-01T12:34:56.789123",
  "pod": "unknown"
}
```

### Ответ с ошибкой (отсутствует поле message)
```
Status: 400 Bad Request
```

```json
{
  "error": "message field is required"
}
```

### Ответ с ошибкой (слишком длинное сообщение)
```
Status: 400 Bad Request
```

```json
{
  "error": "message exceeds maximum length of 1000"
}
```

## Получение метрик

### Запрос
```
GET /metrics
```

### Пример с cURL
```bash
curl -X GET http://localhost:5000/metrics
```

### Пример с Python (requests)
```python
import requests

response = requests.get("http://localhost:5000/metrics")
print(response.text)
```

### Ответ
```
Content-Type: text/plain; charset=utf-8
```

```
# HELP app_info Application information
# TYPE app_info gauge
app_info{version="1.0.0",environment="development",pod="unknown"} 1

# HELP app_requests_total Total requests processed
# TYPE app_requests_total counter
app_requests_total 10

# HELP app_uptime_seconds Application uptime in seconds
# TYPE app_uptime_seconds gauge
app_uptime_seconds 1234.567

# HELP app_current_datetime Current datetime
# TYPE app_current_datetime gauge
app_current_datetime{timestamp="2023-10-01T12:34:56.789123"} 1
```

## Проверка связи

### Запрос
```
GET /api/ping
```

### Пример с cURL
```bash
curl -X GET http://localhost:5000/api/ping
```

### Пример с Python (requests)
```python
import requests

response = requests.get("http://localhost:5000/api/ping")
print(response.json())
```

### Ответ
```json
{
  "pong": true,
  "timestamp": "2023-10-01T12:34:56.789123"
}
```

## Обработка ошибок

При возникновении ошибок API возвращает JSON-объект с описанием ошибки:

```json
{
  "error": "Описание ошибки"
}
```

Статусы ошибок:
- `400 Bad Request`: Некорректный запрос или неверные параметры
- `404 Not Found`: Запрашиваемый ресурс не найден
- `500 Internal Server Error`: Внутренняя ошибка сервера

## Переменные окружения

Приложение может быть настроено с помощью следующих переменных окружения:

- `APP_VERSION` - версия приложения (по умолчанию: "1.0.0")
- `ENVIRONMENT` - окружение (по умолчанию: "development")
- `HOSTNAME` - имя хоста (по умолчанию: "unknown")
- `MAX_MESSAGE_LENGTH` - максимальная длина сообщения (по умолчанию: 1000)
- `PORT` - порт для прослушивания (по умолчанию: 5000)
- `LOG_LEVEL` - уровень логирования (по умолчанию: "INFO")