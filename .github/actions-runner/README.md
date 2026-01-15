# GitHub Actions Self-Hosted Runner в k3s

## Обзор

Этот документ описывает процесс настройки self-hosted runner для GitHub Actions в локальном k3s кластере. Это позволяет запускать CI/CD процессы внутри вашей собственной инфраструктуры.

## Архитектура

```
[GitHub] → [k3s Cluster] → [Self-Hosted Runner] → [Выполнение задач]
```

## Требования

- Установленный k3s кластер
- Доступ к GitHub API (токен)
- Docker внутри кластера
- Достаточные ресурсы для выполнения задач

## Установка

### 1. Создание токена для GitHub Actions Runner

1. Перейдите в настройки вашего репозитория: `Settings` → `Actions` → `Runners`
2. Нажмите `New self-hosted runner`
3. Скопируйте токен для регистрации

### 2. Настройка секретов в Kubernetes

```bash
kubectl create secret generic github-runner-secrets \
  --from-literal=GITHUB_REPO_URL="https://github.com/your-org/your-repo" \
  --from-literal=GITHUB_RUNNER_TOKEN="your-runner-token" \
  --from-literal=GITHUB_RUNNER_NAME="k3s-runner" \
  --namespace=default
```

### 3. Установка Runner с помощью Helm или манифестов

Используйте предоставленные манифесты для развертывания runner в k3s кластере.

## Преимущества использования k3s для runner

- Более быстрая инициализация по сравнению с cloud экземплярами
- Контроль над вычислительными ресурсами
- Возможность использования внутренней инфраструктуры
- Интеграция с остальными сервисами в кластере
- Упрощение сетевой безопасности и доступа к внутренним ресурсам

## Конфигурация

Runner настроен для автоматического подключения к GitHub и выполнения заданий в соответствии с вашими workflow файлами.