#!/bin/bash

echo "Установка зависимостей..."
pip install -r requirements.txt

echo "Запуск тестов..."
PYTHONPATH=. python -m pytest tests/ -v --cov=app --cov-report=html --cov-report=xml

echo "Тестирование завершено!"