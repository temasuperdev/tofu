# Быстрый старт за 5 минут

## 1️⃣ Локальный запуск

```bash
# Установите зависимости
pip install -r requirements.txt

# Запустите приложение
python src/app.py

# Откройте в браузере
open http://localhost:5000
```

## 2️⃣ Docker локально

```bash
# Постройте образ
docker build -f docker/Dockerfile -t demo-app:latest .

# Запустите контейнер
docker run -p 5000:5000 demo-app:latest

# Проверьте здоровье
curl http://localhost:5000/api/health
```

## 3️⃣ Docker Compose

```bash
# Запустите весь стек
docker-compose up -d

# Логи
docker-compose logs -f app

# Остановка
docker-compose down
```

## 4️⃣ K3s развертывание (вручную)

```bash
# Убедитесь, что подключены к K3s
kubectl cluster-info

# Примените манифесты
sed -e "s|IMAGE_REGISTRY|ghcr.io|g" \
    -e "s|IMAGE_NAME|yourname/tofu|g" \
    -e "s|IMAGE_TAG|latest|g" \
    k8s/deployment.yaml | kubectl apply -f -

kubectl apply -f k8s/ingress.yaml

# Проверьте статус
kubectl get pods -n demo-app
kubectl logs -f deployment/demo-app -n demo-app

# Доступ
kubectl port-forward svc/demo-app 8080:80 -n demo-app
open http://localhost:8080
```

## 5️⃣ GitHub Actions CI/CD

1. **Push в GitHub**:
   ```bash
   git push origin main
   ```

2. **Установите KUBECONFIG secret**:
   ```bash
   # Settings → Secrets and variables → Actions
   # Добавьте KUBECONFIG (base64 закодированный содержимое ~/.kube/config)
   ```

3. **Pipeline автоматически запустится**:
   - ✅ Тесты
   - ✅ Build Docker образа
   - ✅ Security сканирование
   - ✅ Deploy в K3s

## 📚 Полезные команды

```bash
# Тесты
pytest tests/ -v

# Логи приложения в K3s
kubectl logs -f deployment/demo-app -n demo-app

# Port forward
kubectl port-forward svc/demo-app 8080:80 -n demo-app

# Описание пода
kubectl describe pod <pod-name> -n demo-app

# Удаление приложения
kubectl delete namespace demo-app

# Скрипт развертывания
bash deploy.sh

# Makefile
make help
make test
make deploy
make logs
```

## 🔗 Endpoints

| URL | Метод | Описание |
|-----|-------|---------|
| `/` | GET | Главная страница |
| `/api/health` | GET | Health check |
| `/api/info` | GET | Информация |
| `/api/ping` | GET | Ping |
| `/api/message` | POST | Отправить сообщение |
| `/metrics` | GET | Метрики |

## 🆘 Troubleshooting

```bash
# Проверьте pod
kubectl describe pod <pod-name> -n demo-app

# Смотрите логи
kubectl logs <pod-name> -n demo-app

# Проверьте ресурсы
kubectl top pods -n demo-app

# Проверьте события
kubectl get events -n demo-app
```

---

**Готово! Приложение развернуто и готово к использованию!** 🚀
