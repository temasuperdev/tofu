#!/bin/bash

# Скрипт для исправления проблемы с NetworkPolicy и аннотациями владельца Helm

RELEASE_NAME=$1
NAMESPACE=${2:-"note"}

if [ -z "$RELEASE_NAME" ]; then
    echo "Использование: $0 <release-name> [namespace]"
    exit 1
fi

echo "Исправляем проблему с NetworkPolicy для релиза: $RELEASE_NAME в namespace: $NAMESPACE"

# Сохраняем конфигурацию NetworkPolicy
echo "Сохраняем конфигурацию NetworkPolicy..."
kubectl get networkpolicy frontend-netpol -n "$NAMESPACE" -o yaml > /tmp/frontend-netpol-backup.yaml 2>/dev/null
kubectl get networkpolicy backend-netpol -n "$NAMESPACE" -o yaml > /tmp/backend-netpol-backup.yaml 2>/dev/null
kubectl get networkpolicy postgresql-netpol -n "$NAMESPACE" -o yaml > /tmp/postgresql-netpol-backup.yaml 2>/dev/null

# Удаляем проблемные NetworkPolicy
echo "Удаляем существующие NetworkPolicy..."
kubectl delete networkpolicy frontend-netpol -n "$NAMESPACE" --ignore-not-found=true
kubectl delete networkpolicy backend-netpol -n "$NAMESPACE" --ignore-not-found=true
kubectl delete networkpolicy postgresql-netpol -n "$NAMESPACE" --ignore-not-found=true

# Проверяем, есть ли другие ресурсы с аналогичной проблемой
echo "Проверяем наличие других ресурсов с проблемой владения..."
kubectl get secrets -n "$NAMESPACE" -l "meta.helm.sh/release-name=$RELEASE_NAME" --no-headers=true | grep -v "ownerReferences" | cut -f1 -d' ' | while read secret_name; do
    kubectl patch secret "$secret_name" -n "$NAMESPACE" --patch '{"metadata":{"annotations":{"meta.helm.sh/release-namespace":"'"$NAMESPACE"'"}}}' 2>/dev/null || echo "Не удалось исправить Secret: $secret_name"
done

echo "Подготовка завершена. Теперь можно выполнить обновление Helm релиза:"
echo "helm upgrade $RELEASE_NAME charts/notes-app --namespace $NAMESPACE --install"