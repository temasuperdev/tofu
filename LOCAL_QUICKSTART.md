# ⚡ Локальный Quick Start (за 2 минуты)

## 🚀 Одна команда - и всё работает!

```bash
bash setup-local.sh
```

Это запустит:
1. ✅ Локальный Docker Registry (localhost:5000)
2. ✅ Соберет Docker образ
3. ✅ Загрузит в локальный registry
4. ✅ Развернет в K3s
5. ✅ Выведет инструкции

---

## 📌 После setup-local.sh (в другом терминале):

```bash
# Доступ к приложению
kubectl port-forward svc/demo-app 8080:80 -n demo-app

# Откройте в браузере
open http://localhost:8080
# или
curl http://localhost:8080/api/health | jq .
```

---

## 🛠️ Полезные команды во время разработки

```bash
# Посмотреть логи
kubectl logs -f deployment/demo-app -n demo-app

# Посмотреть статус
kubectl get pods -n demo-app

# Обновить образ (после изменений в коде)
bash build-local.sh
docker push localhost:5000/demo-app:latest
kubectl rollout restart deployment/demo-app -n demo-app

# Локальное тестирование (без K3s)
python src/app.py
pytest tests/ -v

# Или Docker Compose
docker-compose up
```

---

## 🧹 Очистка

```bash
# Удалить всё
bash cleanup-local.sh

# Или отдельно:
bash registry.sh stop         # Остановить registry
kubectl delete namespace demo-app  # Удалить K3s ресурсы
```

---

## 📚 Подробнее

Полный гайд локальной разработки: [LOCAL_SETUP.md](LOCAL_SETUP.md)

---

**Готово! Приложение работает локально! 🎉**
