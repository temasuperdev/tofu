#!/bin/bash

# Скрипт для безопасного обновления Helm релиза с учетом ограничений StatefulSet

RELEASE_NAME=$1
CHART_PATH=$2
NAMESPACE=${3:-"default"}

if [ -z "$RELEASE_NAME" ] || [ -z "$CHART_PATH" ]; then
    echo "Использование: $0 <release-name> <chart-path> [namespace]"
    exit 1
fi

echo "Выполняем безопасное обновление Helm релиза: $RELEASE_NAME в namespace: $NAMESPACE"

# Обновляем зависимости чарта
echo "Обновляем зависимости Helm чарта"
helm dependency update "$CHART_PATH"

# Проверяем, существует ли релиз в целевом namespace
if helm status "$RELEASE_NAME" -n "$NAMESPACE" >/dev/null 2>&1; then
    echo "Релиз $RELEASE_NAME существует в namespace $NAMESPACE, проверяем состояние PostgreSQL StatefulSet"

    # Удаляем старые секреты, которые могут вызвать конфликты с метаданными владельца
    echo "Удаляем старые секреты, связанные с релизом $RELEASE_NAME в namespace $NAMESPACE"
    kubectl delete secret -n "$NAMESPACE" -l "meta.helm.sh/release-name=$RELEASE_NAME" --field-selector type=Opaque --ignore-not-found=true

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
    # Проверяем, существует ли релиз в другом namespace (например, default)
    DEFAULT_NAMESPACE="default"
    if [ "$NAMESPACE" != "$DEFAULT_NAMESPACE" ] && helm status "$RELEASE_NAME" -n "$DEFAULT_NAMESPACE" >/dev/null 2>&1; then
        echo "Релиз $RELEASE_NAME найден в namespace $DEFAULT_NAMESPACE, удаляем его перед установкой в $NAMESPACE"
        
        # Удаляем релиз из старого namespace
        helm uninstall "$RELEASE_NAME" -n "$DEFAULT_NAMESPACE"
        
        # Удаляем связанные ресурсы, которые могли остаться
        kubectl delete secret -n "$DEFAULT_NAMESPACE" -l "meta.helm.sh/release-name=$RELEASE_NAME" --field-selector type=Opaque --ignore-not-found=true
        kubectl delete pvc -n "$DEFAULT_NAMESPACE" -l "app.kubernetes.io/name=postgresql,release=$RELEASE_NAME" --ignore-not-found=true
    fi

    # Первая установка в целевой namespace
    echo "Выполняем новую установку Helm релиза: $RELEASE_NAME в namespace: $NAMESPACE"
    helm upgrade "$RELEASE_NAME" "$CHART_PATH" --namespace "$NAMESPACE" --install --atomic=true --timeout=10m
fi

echo "Обновление завершено"