#!/bin/bash
#
# Скрипт для проверки состояния базы данных в K3s

NAMESPACE="demo-app"

echo "Проверка состояния PostgreSQL в K3s..."

# Проверяем статус пода PostgreSQL
echo "Статус пода PostgreSQL:"
kubectl get pods -n $NAMESPACE -l app=postgres

# Проверяем логи PostgreSQL
echo "Логи PostgreSQL:"
kubectl logs -l app=postgres -n $NAMESPACE

# Проверяем статус сервиса PostgreSQL
echo "Статус сервиса PostgreSQL:"
kubectl get svc -n $NAMESPACE -l app=postgres

# Проверяем, может ли приложение подключиться к БД
echo "Проверка подключения приложения к БД..."
kubectl logs -l app=demo-app -n $NAMESPACE | tail -20

# Проверяем, есть ли ошибки подключения
echo "Поиск ошибок подключения к БД..."
kubectl logs -l app=demo-app -n $NAMESPACE | grep -i "error\|failed\|connection refused\|psycopg2\|OperationalError" || echo "Ошибки подключения не найдены"

echo "Проверка завершена."