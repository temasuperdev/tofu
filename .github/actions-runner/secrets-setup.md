# Настройка секретов для GitHub Actions Runner в k3s

## Обзор

Для безопасного подключения runner к GitHub, необходимо настроить секреты в Kubernetes. В этом документе описан процесс настройки секретов.

## Необходимые данные

Для настройки runner потребуются следующие данные:

1. **GITHUB_REPO_URL**: URL репозитория (например, `https://github.com/your-org/your-repo`)
2. **GITHUB_RUNNER_TOKEN**: Токен для регистрации runner (генерируется GitHub)
3. **GITHUB_RUNNER_NAME**: Имя, которое будет отображаться в GitHub (опционально)

## Получение токена

1. Перейдите в настройки репозитория: `Settings` → `Actions` → `Runners`
2. Нажмите `New self-hosted runner`
3. Скопируйте токен для регистрации

## Создание секрета в Kubernetes

### Вариант 1: Создание через командную строку

```bash
kubectl create secret generic github-runner-secrets \
  --from-literal=GITHUB_REPO_URL="https://github.com/your-org/your-repo" \
  --from-literal=GITHUB_RUNNER_TOKEN="your-runner-token" \
  --from-literal=GITHUB_RUNNER_NAME="k3s-runner" \
  --namespace=default
```

### Вариант 2: Создание через YAML-манифест

Создайте файл `github-runner-secrets.yaml`:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: github-runner-secrets
  namespace: default
type: Opaque
data:
  GITHUB_REPO_URL: <base64-encoded-url>
  GITHUB_RUNNER_TOKEN: <base64-encoded-token>
  GITHUB_RUNNER_NAME: <base64-encoded-name>
```

Чтобы получить base64-значения:

```bash
echo -n 'https://github.com/your-org/your-repo' | base64
echo -n 'your-runner-token' | base64
echo -n 'k3s-runner' | base64
```

Затем примените манифест:

```bash
kubectl apply -f github-runner-secrets.yaml
```

## Проверка создания секрета

Проверьте, что секрет был создан правильно:

```bash
kubectl describe secret github-runner-secrets
```

## Безопасность

- Не храните токены в открытом виде в репозитории
- Используйте Kubernetes Secrets для хранения чувствительных данных
- Регулярно обновляйте токены
- Ограничьте права доступа к секретам только необходимым pods

## Удаление старых токенов

Если runner больше не нужен, удалите его из GitHub и очистите соответствующий секрет в Kubernetes:

```bash
kubectl delete secret github-runner-secrets
```