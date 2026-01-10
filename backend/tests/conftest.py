import pytest
from src.app import app
from src.services.note_service import NoteService
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.note_model import Base


@pytest.fixture(scope='session')
def test_app():
    """Фикстура для тестового приложения"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        yield app


@pytest.fixture(scope='session')
def test_database():
    """Фикстура для тестовой базы данных"""
    # Создаем временную SQLite базу для тестов
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    
    yield Session()
    
    # Закрываем соединение
    engine.dispose()


@pytest.fixture
def note_service(test_database):
    """Фикстура для сервиса заметок с тестовой базой данных"""
    # Создаем сервис с временной базой данных
    service = NoteService.__new__(NoteService)  # Создаем экземпляр без вызова __init__
    service.database_url = 'sqlite:///:memory:'  # Используем in-memory SQLite
    service.engine = create_engine(service.database_url)
    Base.metadata.create_all(bind=service.engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=service.engine)
    service.db = SessionLocal()
    
    yield service
    
    # Закрываем сессию
    service.db.close()