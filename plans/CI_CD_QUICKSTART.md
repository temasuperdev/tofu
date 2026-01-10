# 🚀 Быстрый старт CI/CD

## 📋 Что нужно сделать?

### Шаг 1: Убедиться что всё коммитить с улучшениями

```bash
cd /root/tofu
git status
```

### Шаг 2: Просмотреть изменения

```bash
git diff .github/workflows/ci-cd.yaml
git diff backend/requirements.txt
```

### Шаг 3: Локально протестировать

```bash
cd backend

# Установить зависимости
pip install -r requirements.txt

# Запустить тесты
pytest tests/ -v

# Проверить код качество
black --check src/
flake8 src/
pylint src/
```

### Шаг 4: Закоммитить и запушить

```bash
git add .github/workflows/ci-cd.yaml
git add backend/requirements.txt
git add backend/tests/conftest.py
git add backend/pytest.ini
git add backend/.flake8
git add backend/.pylintrc
git add backend/pyproject.toml
git add backend/docs/CI_CD_IMPROVEMENTS.md
git commit -m "refactor: improve CI/CD with quality checks, matrix testing, and auto-rollback"
git push origin main
```

## 🎯 Что произойдёт на GitHub?

1. **GitHub Actions запустится автоматически**
   - Перейдите на Actions tab
   - Нажмите на последний workflow run

2. **Workflow выполнит шаги**:
   - ✅ Запустит тесты на Python 3.9, 3.10, 3.11
   - ✅ Проверит код качество (Black, Flake8, Pylint)
   - ✅ Собрет Docker образ
   - ✅ Отправит в GHCR
   - ✅ Отсканирует на уязвимости
   - ✅ Развернёт в K3s
   - ✅ Проверит здоровье приложения
   - ✅ При ошибке - откатит на предыдущую версию

## 📊 Где смотреть результаты?

### GitHub Actions:
```
GitHub → Actions → Последний run
```

### Логи тестов:
```
Jobs → Run Tests → Step output
```

### Логи deployment:
```
Jobs → Deploy to K3s → Step output
```

### Логи pod'ов в K3s:
```bash
kubectl logs -n demo-app -l app=demo-app --tail=100
```

## ✅ Проверочный список

- [ ] Все файлы закоммичены
- [ ] Push выполнен в main
- [ ] GitHub Actions запустился
- [ ] Все тесты проходят
- [ ] Deployment успешен
- [ ] Приложение отвечает на запросы

## 🆘 Если что-то не работает

### Проблема: Тесты падают
```bash
# Локально запустить с verbose
pytest backend/tests/ -vv

# Посмотреть на GitHub Actions логи
# Actions → Job → Run Tests → Output
```

### Проблема: Code quality checks падают
```bash
# Форматировать код
black backend/src/

# Исправить flake8 ошибки
flake8 backend/src/ --show-source

# Проверить pylint
pylint backend/src/ --disable=C0114,C0115,C0116
```

### Проблема: Docker build падает
```bash
# Локально собрать образ
docker build -f backend/docker/Dockerfile -t demo-app:test .

# Запустить контейнер
docker run -p 5000:5000 demo-app:test
```

### Проблема: Deployment падает
```bash
# Посмотреть статус
kubectl get deployment demo-app -n demo-app

# Посмотреть pod'ы
kubectl get pods -n demo-app

# Посмотреть события
kubectl get events -n demo-app --sort-by='.lastTimestamp'

# Посмотреть логи
kubectl logs -n demo-app --all-containers=true --tail=50
```

## 📚 Полная документация

- [CI/CD Guide](CI_CD_GUIDE.md) - подробное описание CI/CD
- [CI/CD Improvements](CI_CD_IMPROVEMENTS.md) - что было улучшено
- [Troubleshooting](TROUBLESHOOTING.md) - решение проблем
