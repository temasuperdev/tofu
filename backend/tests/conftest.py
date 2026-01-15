import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
import uuid
from contextlib import contextmanager

from app.database import Base, get_db, init_db_engine
from app.main import app
from app.models.user import User
from app.models.note import Note
from app.models.category import Category
from app.security.password import get_password_hash


@pytest.fixture(scope="session", autouse=True)
def engine():
    """Инициализируем тестовую БД и переопределяем глобальный engine"""
    test_db_url = "sqlite:///./test.db"
    test_engine = create_engine(test_db_url)
    
    # Переопределяем глобальный engine для health check и других компонентов
    import app.database
    app.database.engine = test_engine
    app.database.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    
    # Также переопределяем init_db_engine, чтобы она использовала тестовую БД
    original_init_db_engine = app.database.init_db_engine
    def mock_init_db_engine(database_url=None):
        app.database.engine = test_engine
        app.database.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
        return test_engine
    
    app.database.init_db_engine = mock_init_db_engine
    
    yield test_engine
    
    # Восстанавливаем оригинальную функцию после тестов
    app.database.init_db_engine = original_init_db_engine


@pytest.fixture(scope="session")
def tables(engine):
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(engine, tables):
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def client(db_session, engine):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass  # Не закрываем сессию здесь, так как она управляется фикстурой
    
    # Устанавливаем переменную окружения для определения тестового режима ДО создания клиента
    import os
    os.environ["TESTING"] = "true"
    
    # Переопределяем init_db_engine ПЕРЕД созданием клиента, чтобы lifespan использовал тестовую БД
    import app.database
    original_init_db_engine = app.database.init_db_engine
    def mock_init_db_engine(database_url=None):
        # Всегда возвращаем тестовый engine
        app.database.engine = engine
        app.database.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        return engine
    app.database.init_db_engine = mock_init_db_engine
    
    # Устанавливаем engine перед созданием клиента
    app.database.engine = engine
    app.database.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    app.dependency_overrides[get_db] = override_get_db
    
    # Создаем клиент - lifespan вызовет init_db_engine, но мы его переопределили
    with TestClient(app) as test_client:
        # Убеждаемся, что engine все еще тестовый после создания клиента и lifespan
        app.database.engine = engine
        app.database.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        yield test_client
    
    # Восстанавливаем
    app.database.init_db_engine = original_init_db_engine
    app.dependency_overrides.clear()
    if "TESTING" in os.environ:
        del os.environ["TESTING"]


@pytest.fixture
def test_user(db_session):
    # Генерируем уникальные значения для каждого теста
    unique_id = str(uuid.uuid4())
    # Создаем пользователя с правильным хешированием пароля
    user_data = {
        "username": f"testuser_{unique_id[:8]}",
        "email": f"test_{unique_id[:8]}@example.com",
        "password_hash": get_password_hash("password")
    }
    user = User(**user_data)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_category(db_session, test_user):
    unique_id = str(uuid.uuid4())[:8]
    category_data = {
        "name": f"Test Category {unique_id}",
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