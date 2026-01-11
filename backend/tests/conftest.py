import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
import uuid

from app.database import Base, get_db
from app.main import app
from app.models.user import User
from app.models.note import Note
from app.models.category import Category


@pytest.fixture(scope="session")
def engine():
    return create_engine("sqlite:///./test.db")


@pytest.fixture(scope="session")
def tables(engine):
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session")
def db_session(engine, tables):
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    # Генерируем уникальные значения для каждого теста
    unique_id = str(uuid.uuid4())
    # Создаем пользователя без хэширования пароля, чтобы избежать проблем с bcrypt
    user_data = {
        "username": f"testuser_{unique_id[:8]}",
        "email": f"test_{unique_id[:8]}@example.com",
        "password_hash": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"  # Хардкод хэша для 'password'
    }
    user = User(**user_data)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_category(db_session, test_user):
    category_data = {
        "name": "Test Category Main",
        "user_id": test_user.id  # Обновлено поле на user_id, а не owner_id
    }
    category = Category(**category_data)
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category


@pytest.fixture
def test_note(db_session, test_user, test_category):
    note_data = {
        "title": "Test Note Main",
        "content": "This is a test note",
        "user_id": test_user.id,  # Обновлено поле на user_id, а не owner_id
        "category_id": test_category.id,  # Обновлено поле для связи с категорией
        "tags": "test,note"  # Обновлено поле тегов для совместимости с SQLite
    }
    note = Note(**note_data)
    db_session.add(note)
    db_session.commit()
    db_session.refresh(note)
    return note