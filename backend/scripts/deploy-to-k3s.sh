#!/bin/bash
#
# Скрипт для развертывания приложения в K3s с правильным порядком запуска сервисов

set -e  # Выход при ошибке

NAMESPACE="demo-app"

echo "Создание namespace..."
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

echo "Применение конфигурации PostgreSQL..."
kubectl apply -f k8s/postgres.yaml

echo "Ожидание запуска PostgreSQL..."
kubectl wait --for=condition=ready pod -l app=postgres -n $NAMESPACE --timeout=120s

echo "Проверка состояния PostgreSQL..."
kubectl get pods -n $NAMESPACE | grep postgres

# Ждем дополнительное время для полной инициализации БД
echo "Дополнительная задержка для инициализации PostgreSQL..."
sleep 15

echo "Проверка логов PostgreSQL..."
kubectl logs -l app=postgres -n $NAMESPACE

echo "Применение основного деплоймента..."
kubectl apply -f k8s/deployment.yaml

echo "Ожидание запуска приложения..."
kubectl wait --for=condition=ready pod -l app=demo-app -n $NAMESPACE --timeout=180s

echo "Проверка состояния всех сервисов..."
kubectl get all -n $NAMESPACE

echo "Проверка логов приложения..."
kubectl logs -l app=demo-app -n $NAMESPACE

echo "Развертывание завершено успешно!"