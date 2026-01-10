#!/usr/bin/env python3
"""
Скрипт для локального запуска приложения с SQLite базой данных
"""
import os
import sys
from pathlib import Path

# Добавляем директорию src в путь Python
sys.path.insert(0, str(Path(__file__).parent / "src"))

def main():
    # Устанавливаем переменные окружения для локальной разработки
    os.environ.setdefault('ENVIRONMENT', 'development')
    os.environ.setdefault('DB_TYPE', 'sqlite')
    os.environ.setdefault('DB_NAME', 'notes_db')
    os.environ.setdefault('DATABASE_URL', 'sqlite:///./notes_db.db')
    
    # Импортируем и запускаем приложение
    from src.app import app
    
    print("Запуск приложения с SQLite базой данных...")
    print(f"DATABASE_URL: {os.environ.get('DATABASE_URL')}")
    
    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == "__main__":
    main()