# 🚀 Локальная разработка и развертывание (Local Setup)

## Полная локальная конфигурация

Этот гайд показывает как запустить всё локально с собственным Docker Registry и K3s, без зависимостей от GitHub Actions или внешних сервисов.

---

## 📋 Требования

- Docker установлен и запущен
- K3s кластер установлен и работает (можно использовать k3d для локального K3s)
- kubectl установлен и настроен
- bash shell

---

## 🚀 Быстрый старт (одна команда!)

```bash
# Полная настройка: запускает registry, строит образ, развертывает в K3s
bash setup-local.sh
```

Это сделает все автоматически:
1. ✅ Запустит локальный Docker Registry на порту 5000
2. ✅ Соберет Docker образ
3. ✅ Загрузит образ в локальный registry
4. ✅ Развернет в K3s кластер
5. ✅ Выведет инструкции для доступа

---

## 📝 Пошаговая локальная разработка

### Шаг 1: Запустить локальный Docker Registry

```bash
# Запустить registry
bash registry.sh start

# Проверить статус
bash registry.sh status

# Остановить (если нужно)
bash registry.sh stop
```

**Что происходит:**
- Запускает Docker контейнер с registry на `http://localhost:5000`
- Создает volume для хранения образов
- Эти образы хранятся локально на вашей машине

**Проверить доступные образы:**
```bash
curl http://localhost:5000/v2/_catalog | jq .
```

---

### Шаг 2: Собрать Docker образ для локального registry

```bash
# С переменными окружения
REGISTRY_HOST=localhost:5000 \
IMAGE_NAME=demo-app \
IMAGE_TAG=latest \
bash build-local.sh

# Или просто (используются значения по умолчанию)
bash build-local.sh
```

**Результат:**
```
localhost:5000/demo-app:latest  ← готовый образ
```

---

### Шаг 3: Загрузить образ в локальный registry

```bash
# Автоматически во время push
docker push localhost:5000/demo-app:latest

# Проверить
curl http://localhost:5000/v2/_catalog | jq .
```

**Вывод:**
```json
{
  "repositories": [
    "demo-app"
  ]
}
```

---

### Шаг 4: Развернуть в K3s

```bash
# Развернуть с локальным registry
REGISTRY_HOST=localhost:5000 bash deploy-local.sh

# Или просто (используются значения по умолчанию)
bash deploy-local.sh
```

**Что происходит:**
- Подставляет `localhost:5000/demo-app:latest` в K8s манифесты
- Применяет Deployment, Service, Ingress
- Ждет, пока все pods запустятся

---

### Шаг 5: Доступ к приложению

```bash
# В отдельном терминале запустить port-forward
kubectl port-forward svc/demo-app 8080:80 -n demo-app

# В браузере или curl
curl http://localhost:8080
open http://localhost:8080
```

---

## 🛠️ Команды make-local (Альтернатива bash скриптам)

```bash
# Помощь
bash make-local.sh help

# Запустить registry
bash make-local.sh registry-start
bash make-local.sh registry-status
bash make-local.sh registry-stop

# Полная настройка
bash make-local.sh setup

# Построить и развернуть
bash make-local.sh build
bash make-local.sh push
bash make-local.sh deploy

# Развитие
bash make-local.sh port-forward
bash make-local.sh logs
bash make-local.sh test

# Очистка
bash make-local.sh clean       # Удалить K3s
bash make-local.sh clean-all   # Удалить всё
```

---

## 🔄 Типичный workflow локальной разработки

### Вариант 1: Один раз настроить, затем итерировать

```bash
# День 1: Полная настройка
bash setup-local.sh

# Дни 2-N: Работа с кодом
# 1. Измените src/app.py
# 2. Тестируйте локально
python src/app.py
pytest tests/ -v

# 3. Когда готово, обновите в K3s
bash build-local.sh                           # Собрать образ
docker push localhost:5000/demo-app:latest    # Загрузить
kubectl rollout restart deployment/demo-app -n demo-app  # Перезагрузить
kubectl logs -f deployment/demo-app -n demo-app          # Проверить
```

### Вариант 2: Быстрая локальная разработка без K3s

```bash
# Просто запустить приложение локально
python src/app.py

# Тестировать
curl http://localhost:5000/api/health | jq .

# Когда готово - развернуть в K3s
bash setup-local.sh
```

### Вариант 3: Docker Compose для локальной разработки

```bash
# Быстро запустить всё в Docker
docker-compose up

# Тестировать
curl http://localhost:5000/api/health

# Остановить
docker-compose down
```

---

## 📊 Обновление приложения (при изменениях в коде)

### Самый быстрый способ (for development)

```bash
# Способ 1: Пересобрать и развернуть
bash build-local.sh
docker push localhost:5000/demo-app:latest
kubectl rollout restart deployment/demo-app -n demo-app

# Способ 2: С явным tagом версии
bash build-local.sh
docker push localhost:5000/demo-app:v1.1
kubectl set image deployment/demo-app \
  app=localhost:5000/demo-app:v1.1 \
  -n demo-app
```

### Проверить обновление

```bash
# Смотреть логи
kubectl logs -f deployment/demo-app -n demo-app

# Проверить версию
curl http://localhost:8080/api/info | jq .version

# Проверить health
curl http://localhost:8080/api/health
```

---

## 🔍 Полезные команды для локальной разработки

```bash
# === Registry ===
bash registry.sh status                    # Статус registry
curl http://localhost:5000/v2/_catalog    # Список образов
bash registry.sh clean                     # Удалить registry

# === Docker ===
docker images | grep localhost             # Локальные образы
docker ps | grep demo-app                  # Запущенные контейнеры
docker logs <container-id>                 # Логи контейнера

# === Kubernetes ===
kubectl get all -n demo-app                # Все ресурсы
kubectl describe pod <pod-name> -n demo-app
kubectl exec -it <pod-name> -n demo-app -- /bin/bash  # Зайти в pod
kubectl logs <pod-name> -n demo-app
kubectl port-forward pod/<pod-name> 8080:5000 -n demo-app

# === Тестирование ===
pytest tests/ -v                           # Запустить тесты
curl http://localhost:5000/api/health      # Health check
curl -X POST http://localhost:5000/api/message \
  -H "Content-Type: application/json" \
  -d '{"message": "test"}'                 # Отправить сообщение
```

---

## 🆘 Troubleshooting

### Registry не запускается

```bash
# Проверить Docker
docker ps

# Проверить логи registry
bash registry.sh logs

# Может быть занят порт 5000
lsof -i :5000      # Найти процесс на порту
kill -9 <PID>      # Убить процесс если нужно
```

### K3s не находится

```bash
# Проверить K3s работает
k3s -v
kubectl cluster-info

# Если K3s не установлен, использовать k3d (Docker-based K3s)
k3d cluster create my-cluster
k3d cluster start my-cluster
```

### Pod не запускается

```bash
# Описание пода
kubectl describe pod <pod-name> -n demo-app

# Логи ошибок
kubectl logs <pod-name> -n demo-app

# Проверить image pull - локальный ли используется?
kubectl get pod <pod-name> -n demo-app -o yaml | grep image
```

### Image pull error (localhost:5000 не найден)

```bash
# Убедитесь что registry запущен
bash registry.sh status

# Проверьте в K8s манифесте что правильный image
grep "image:" k8s/deployment.yaml

# Image должен быть: localhost:5000/demo-app:latest
```

### Port forward не работает

```bash
# Может быть занят порт 8080
lsof -i :8080

# Использовать другой порт
kubectl port-forward svc/demo-app 9090:80 -n demo-app
curl http://localhost:9090
```

---

## 📁 Файлы для локальной разработки

| Файл | Назначение |
|------|-----------|
| `setup-local.sh` | Полная локальная настройка (одна команда!) |
| `registry.sh` | Управление локальным Docker Registry |
| `build-local.sh` | Сборка образа для локального registry |
| `deploy-local.sh` | Развертывание в K3s с локальным registry |
| `cleanup-local.sh` | Удаление всех локальных ресурсов |
| `make-local.sh` | Альтернатива bash командам (make-like) |

---

## 🎯 Рекомендуемый локальный workflow

### Для начинающих

```bash
# День 1: Запустить локально без Docker
python src/app.py
curl http://localhost:5000/api/health
# Изучить код, API

# День 2: Docker
docker-compose up
# Понять как контейнеризируется приложение

# День 3: K3s
bash setup-local.sh
kubectl port-forward svc/demo-app 8080:80 -n demo-app
# Увидеть как работает K3s
```

### Для разработчиков

```bash
# Разработка локально
python src/app.py  # или docker-compose up

# Когда готово - тестировать в K3s
bash setup-local.sh
# Проверить в реальной среде

# Итерировать
# 1. Изменить код
# 2. Тестировать локально
# 3. Пересобрать образ
# 4. Обновить в K3s
bash build-local.sh && \
  docker push localhost:5000/demo-app:latest && \
  kubectl rollout restart deployment/demo-app -n demo-app
```

---

## 🚀 Варианты локального K3s (если его нет)

### Использовать k3d (Docker-based K3s) 

```bash
# Установить k3d
curl -s https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | bash

# Создать кластер с registry
k3d cluster create my-cluster \
  --registry-create \
  --port "8080:80@loadbalancer"

# Использовать
export KUBECONFIG=$(k3d kubeconfig write my-cluster)
kubectl cluster-info

# Теперь использовать k3d-registry.local-registry:5000 в образах
REGISTRY_HOST=k3d-registry.local-registry:5000 bash build-local.sh
```

### Использовать Minikube

```bash
# Запустить minikube
minikube start --driver=docker

# Включить registry addon
minikube addons enable registry

# Использовать localhost:5000
REGISTRY_HOST=localhost:5000 bash build-local.sh
```

---

## 📚 Полезные ссылки

- [K3s documentation](https://docs.k3s.io/)
- [k3d - local K3s in Docker](https://k3d.io/)
- [Minikube - local Kubernetes](https://minikube.sigs.k8s.io/)
- [Docker Registry](https://docs.docker.com/registry/)

---

## ✨ Готово!

Теперь вы можете полностью разрабатывать и тестировать приложение локально без интернета!

**Начните с:**
```bash
bash setup-local.sh
```

---

**Happy local development! 🎉**
