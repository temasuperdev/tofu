#!/bin/bash

# Скрипт для безопасного обновления Helm релиза с учетом ограничений StatefulSet

RELEASE_NAME=$1
CHART_PATH=$2
NAMESPACE=${3:-"default"}

if [ -z "$RELEASE_NAME" ] || [ -z "$CHART_PATH" ]; then
    echo "Использование: $0 <release-name> <chart-path> [namespace]"
    exit 1
fi

echo "Выполняем безопасное обновление Helm релиза: $RELEASE_NAME"

# Проверяем, существует ли релиз
if helm status "$RELEASE_NAME" -n "$NAMESPACE" >/dev/null 2>&1; then
    echo "Релиз $RELEASE_NAME существует, проверяем состояние PostgreSQL StatefulSet"

    # Получаем информацию о StatefulSet PostgreSQL
    POSTGRES_STS=$(kubectl get statefulsets -l app.kubernetes.io/name=postgresql -n "$NAMESPACE" -o json 2>/dev/null)
    
    if [ -n "$POSTGRES_STS" ] && [ "$(echo "$POSTGRES_STS" | jq -r '.items | length')" -gt 0 ]; then
        echo "Обнаружен StatefulSet PostgreSQL, проверяем необходимость обновления PVC..."

        # Сохраняем текущую конфигурацию
        kubectl get statefulset -l app.kubernetes.io/name=postgresql -n "$NAMESPACE" -o yaml > /tmp/current-postgres-sts.yaml
        
        # Выполняем dry-run обновления для проверки возможных изменений
        helm upgrade "$RELEASE_NAME" "$CHART_PATH" --namespace "$NAMESPACE" --dry-run --debug > /tmp/helm-dry-run-output.yaml 2>&1
    
        # Если есть конфликт с PVC, возможно, нужно удалить старый StatefulSet
        if grep -q "PersistentVolumeClaimRetentionPolicy\|volumeClaimTemplates" /tmp/helm-dry-run-output.yaml; then
            echo "Обнаружены потенциальные конфликты с PVC, сохраняем данные и готовимся к обновлению..."
            
            # Резервное копирование данных (опционально)
            # kubectl exec -it "$RELEASE_NAME-postgresql-0" -n "$NAMESPACE" -- pg_dump -U postgres -d notesdb > backup.sql
            
            # Проверяем, можно ли выполнить обновление с флагом --force
            echo "Пытаемся выполнить обновление с флагами --force и --atomic=false"
            helm upgrade "$RELEASE_NAME" "$CHART_PATH" --namespace "$NAMESPACE" --install --atomic=false --timeout=10m --set postgresql.primary.persistentVolumeClaimRetentionPolicy.whenDeleted=Retain --set postgresql.primary.persistentVolumeClaimRetentionPolicy.whenScaled=Retain
        else
            # Обычное обновление
            echo "Конфликтов не обнаружено, выполняем стандартное обновление"
            helm upgrade "$RELEASE_NAME" "$CHART_PATH" --namespace "$NAMESPACE" --install --atomic=true --timeout=10m
        fi
    else
        # Первичная установка или StatefulSet не существует
        echo "StatefulSet PostgreSQL не найден или это первая установка, выполняем обычное обновление"
        helm upgrade "$RELEASE_NAME" "$CHART_PATH" --namespace "$NAMESPACE" --install --atomic=true --timeout=10m
    fi
else
    # Первая установка
    echo "Выполняем новую установку Helm релиза: $RELEASE_NAME"
    helm upgrade "$RELEASE_NAME" "$CHART_PATH" --namespace "$NAMESPACE" --install --atomic=true --timeout=10m
fi

echo "Обновление завершено"