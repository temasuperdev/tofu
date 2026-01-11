#!/bin/bash

echo "Установка зависимостей..."
pip install --upgrade pip
pip install pydantic[email]
pip install -r requirements.txt

echo "Запуск тестов..."
PYTHONPATH=. python -m pytest tests/ -v --cov=app --cov-report=html --cov-report=xml

echo "Тестирование завершено!"