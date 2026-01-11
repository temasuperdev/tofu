import pytest
from datetime import datetime
from pydantic import ValidationError
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.schemas.note import NoteCreate, NoteUpdate, NoteResponse
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse


def test_user_create_schema():
    """Test UserCreate schema validation."""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "securepassword123"
    }
    
    user = UserCreate(**user_data)
    
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.password == "securepassword123"


def test_user_update_schema():
    """Test UserUpdate schema validation."""
    user_data = {
        "username": "updateduser",
        "email": "updated@example.com"
    }
    
    user = UserUpdate(**user_data)
    
    assert user.username == "updateduser"
    assert user.email == "updated@example.com"


def test_user_response_schema():
    """Test UserResponse schema serialization."""
    from datetime import datetime
    user_response = UserResponse.model_validate({
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "is_active": True
    })
    
    assert user_response.id == 1
    assert user_response.username == "testuser"
    assert user_response.email == "test@example.com"
    assert isinstance(user_response.created_at, datetime)


def test_category_create_schema():
    """Test CategoryCreate schema validation."""
    category_data = {
        "name": "Test Category"
    }
    
    category = CategoryCreate(**category_data)
    
    assert category.name == "Test Category"


def test_category_update_schema():
    """Test CategoryUpdate schema validation."""
    category_data = {
        "name": "Updated Category"
    }
    
    category = CategoryUpdate(**category_data)
    
    assert category.name == "Updated Category"


def test_category_response_schema():
    """Test CategoryResponse schema serialization."""
    from datetime import datetime
    category_response = CategoryResponse.model_validate({
        "id": 1,
        "name": "Test Category",
        "description": "Test Description",
        "user_id": 1,
        "created_at": datetime.now()
    })
    
    assert category_response.id == 1
    assert category_response.name == "Test Category"
    assert category_response.user_id == 1


def test_note_create_schema():
    """Test NoteCreate schema validation."""
    note_data = {
        "title": "Test Note",
        "content": "This is a test note content"
    }
    
    note = NoteCreate(**note_data)
    
    assert note.title == "Test Note"
    assert note.content == "This is a test note content"


def test_note_update_schema():
    """Test NoteUpdate schema validation."""
    note_data = {
        "title": "Updated Note",
        "content": "Updated content"
    }
    
    note = NoteUpdate(**note_data)
    
    assert note.title == "Updated Note"
    assert note.content == "Updated content"


def test_note_response_schema():
    """Test NoteResponse schema serialization."""
    from datetime import datetime
    note_response = NoteResponse.model_validate({
        "id": 1,
        "title": "Test Note",
        "content": "This is a test note",
        "user_id": 1,
        "is_public": False,
        "category": "Test Category",
        "tags": ["test", "note"],
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    })
    
    assert note_response.id == 1
    assert note_response.title == "Test Note"
    assert note_response.content == "This is a test note"
    assert note_response.user_id == 1
    assert note_response.category == "Test Category"
    assert isinstance(note_response.created_at, datetime)
    assert isinstance(note_response.updated_at, datetime)


def test_user_create_invalid_email():
    """Test UserCreate schema with invalid email."""
    user_data = {
        "username": "testuser",
        "email": "invalid-email",
        "password": "securepassword123"
    }
    
    with pytest.raises(ValidationError):
        UserCreate(**user_data)


def test_user_create_short_password():
    """Test UserCreate schema with short password."""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "short"
    }
    
    with pytest.raises(ValidationError):
        UserCreate(**user_data)


def test_note_create_empty_title():
    """Test NoteCreate schema with empty title."""
    note_data = {
        "title": "",
        "content": "This is a test note content"
    }
    
    with pytest.raises(ValueError):
        NoteCreate(**note_data)