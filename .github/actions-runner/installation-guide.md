# Установка GitHub Actions Self-Hosted Runner в k3s

## Обзор

В этом руководстве описывается процесс установки и настройки self-hosted runner для GitHub Actions в локальном k3s кластере.

## Требования

- Установленный k3s кластер (версия 1.20 или выше рекомендуется)
- Доступ к командной строке с установленным `kubectl`
- Доступ к GitHub с правами настройки Actions runners
- Docker установлен в системе (для Docker-in-Docker функциональности)

## Шаги установки

### Шаг 1: Подготовка GitHub токена

1. Перейдите в настройки вашего репозитория: `Settings` → `Actions` → `Runners`
2. Нажмите `New self-hosted runner`
3. Скопируйте токен для регистрации
4. Запишите URL вашего репозитория (например, `https://github.com/your-org/your-repo`)

### Шаг 2: Создание секретов в Kubernetes

Создайте секреты, необходимые для подключения runner к GitHub:

```bash
kubectl create secret generic github-runner-secrets \
  --from-literal=GITHUB_REPO_URL="https://github.com/your-org/your-repo" \
  --from-literal=GITHUB_RUNNER_TOKEN="your-runner-token" \
  --from-literal=GITHUB_RUNNER_NAME="k3s-runner" \
  --namespace=default
```

### Шаг 3: Выбор подходящего варианта развертывания

В зависимости от ваших требований выберите один из двух вариантов:

#### Вариант A: Базовый runner (для простых задач)

Используйте этот вариант, если вам не нужны контейнеры внутри runner.

Примените манифест:

```bash
kubectl apply -f github-actions-runner.yaml
```

#### Вариант B: Runner с Docker-in-Docker (для задач с контейнеризацией)

Используйте этот вариант, если в ваших workflow используются Docker контейнеры.

Примените манифест:

```bash
kubectl apply -f github-actions-runner-dind.yaml
```

### Шаг 4: Проверка состояния

Проверьте, что pod запущен успешно:

```bash
kubectl get pods -l app=github-actions-runner
```

Или для Docker-in-Docker версии:

```bash
kubectl get pods -l app=github-actions-runner-dind
```

Проверьте логи:

```bash
kubectl logs -l app=github-actions-runner -f
```

### Шаг 5: Проверка регистрации в GitHub

1. Перейдите в настройки Actions runners: `Settings` → `Actions` → `Runners`
2. Убедитесь, что ваш runner появился в списке и имеет статус `Online`

## Настройка workflow для использования self-hosted runner

В своих workflow файлах укажите runner типа `self-hosted`:

```yaml
name: CI Pipeline

on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: self-hosted  # или конкретное имя runner
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Build application
      run: |
        echo "Running on self-hosted runner in k3s cluster"
```

## Мониторинг и обслуживание

### Проверка состояния runner

```bash
kubectl get pods -n default
kubectl describe pod <pod-name>
kubectl logs <pod-name>
```

### Обновление runner

1. Удалите старый deployment:

```bash
kubectl delete deployment github-actions-runner
```

2. Обновите образ в манифесте (если необходимо)
3. Примените новый манифест:

```bash
kubectl apply -f github-actions-runner.yaml
```

### Перезапуск runner

```bash
kubectl delete pod -l app=github-actions-runner
```

Kubernetes автоматически пересоздаст pod.

## Устранение неполадок

### Проблема: Runner не регистрируется в GitHub

1. Проверьте корректность токена:

```bash
kubectl get secret github-runner-secrets -o yaml
```

2. Проверьте логи pod:

```bash
kubectl logs <pod-name>
```

3. Убедитесь, что URL репозитория указан правильно

### Проблема: Ошибки с Docker (в случае использования dind)

1. Проверьте, что privileged режим включен в container specification
2. Убедитесь, что у k3s есть доступ к внешним ресурсам для скачивания образов

### Проблема: Недостаточно ресурсов

Отредактируйте манифест, увеличив значения в разделах `resources.requests` и `resources.limits`.

## Безопасность

- Регулярно обновляйте токены runner
- Используйте network policies для ограничения доступа к runner
- Ограничьте привилегии service accounts
- Периодически проверяйте логи на предмет подозрительной активности

## Удаление runner

Для удаления runner выполните:

```bash
kubectl delete deployment github-actions-runner
kubectl delete secret github-runner-secrets
```

## Заключение

Теперь у вас есть полнофункциональный GitHub Actions runner, работающий в вашем локальном k3s кластере. Он может выполнять все те же задачи, что и hosted runner, но с дополнительными преимуществами локальной инфраструктуры.