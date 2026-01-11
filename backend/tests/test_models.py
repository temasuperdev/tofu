import pytest
from datetime import datetime
from app.models.user import User
from app.models.note import Note
from app.models.category import Category


def test_user_model(db_session):
    """Test basic user model functionality."""
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password"
    )
    
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.password_hash == "hashed_password"
    assert isinstance(user.created_at, datetime)
    assert user.is_active is True


def test_category_model(db_session, test_user):
    """Test basic category model functionality."""
    category = Category(
        name="Test Category",
        user_id=test_user.id
    )
    
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    
    assert category.name == "Test Category"
    assert category.user_id == test_user.id
    assert category.owner == test_user


def test_note_model(db_session, test_user, test_category):
    """Test basic note model functionality."""
    note = Note(
        title="Test Note",
        content="This is a test note",
        user_id=test_user.id,
        category_id=test_category.id
    )
    
    db_session.add(note)
    db_session.commit()
    db_session.refresh(note)
    
    assert note.title == "Test Note"
    assert note.content == "This is a test note"
    assert note.user_id == test_user.id
    assert note.category_id == test_category.id
    assert note.owner == test_user
    assert note.category_rel == test_category
    assert isinstance(note.created_at, datetime)
    # updated_at может быть None при создании, так как устанавливается только при обновлении
    # assert isinstance(note.updated_at, datetime)


def test_user_relationships(db_session, test_user, test_category, test_note):
    """Test user relationships with categories and notes."""
    assert len(test_user.categories) >= 1
    assert len(test_user.notes) >= 1
    assert test_category in test_user.categories
    assert test_note in test_user.notes


def test_category_notes_relationship(db_session, test_category, test_note):
    """Test category relationship with notes."""
    assert len(test_category.notes) >= 1
    assert test_note in test_category.notes