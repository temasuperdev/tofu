import pytest
from sqlalchemy.exc import IntegrityError
from app.crud.user import create_user, get_user_by_username, get_user_by_email, update_user, delete_user
from app.crud.category import create_category, get_categories, get_category, update_category, delete_category
from app.crud.note import create_note, get_notes, get_note, update_note, delete_note
from app.models.user import User
from app.models.category import Category
from app.models.note import Note


def test_create_and_get_user(db_session):
    """Test creating and retrieving a user."""
    user = create_user(db_session, username="testuser2", email="test2@example.com", password="pass123")
    
    assert user.username == "testuser2"
    assert user.email == "test2@example.com"
    
    retrieved_user = get_user_by_username(db_session, "testuser2")
    assert retrieved_user is not None
    assert retrieved_user.username == "testuser2"
    
    retrieved_user_by_email = get_user_by_email(db_session, "test2@example.com")
    assert retrieved_user_by_email is not None
    assert retrieved_user_by_email.email == "test2@example.com"


def test_duplicate_username_fails(db_session, test_user):
    """Test that creating a user with duplicate username fails."""
    with pytest.raises(IntegrityError):
        create_user(db_session, username=test_user.username, email="different@example.com", password="pass123")


def test_duplicate_email_fails(db_session, test_user):
    """Test that creating a user with duplicate email fails."""
    with pytest.raises(IntegrityError):
        create_user(db_session, username="different_username", email=test_user.email, password="pass123")


def test_update_user(db_session, test_user):
    """Test updating a user."""
    updated_user = update_user(db_session, test_user.id, username="updated_testuser", email="updated@example.com")
    
    assert updated_user.username == "updated_testuser"
    assert updated_user.email == "updated@example.com"


def test_delete_user(db_session):
    """Test deleting a user."""
    user = create_user(db_session, username="todelete", email="todelete@example.com", password="pass123")
    user_id = user.id
    
    deleted_user = delete_user(db_session, user_id)
    
    assert deleted_user.id == user_id
    assert get_user_by_username(db_session, "todelete") is None


def test_create_and_get_category(db_session, test_user):
    """Test creating and retrieving a category."""
    from app.schemas.category import CategoryCreate
    
    category_data = CategoryCreate(name="Test Category 2")
    category = create_category(db_session, category=category_data, user_id=test_user.id)
    
    assert category.name == "Test Category 2"
    assert category.user_id == test_user.id
    
    retrieved_category = get_category(db_session, category.id)
    assert retrieved_category is not None
    assert retrieved_category.name == "Test Category 2"


def test_get_categories(db_session, test_user):
    """Test retrieving all categories for a user."""
    from app.schemas.category import CategoryCreate
    
    # Create multiple categories
    category1_data = CategoryCreate(name="Category 1")
    category2_data = CategoryCreate(name="Category 2")
    
    create_category(db_session, category=category1_data, user_id=test_user.id)
    create_category(db_session, category=category2_data, user_id=test_user.id)
    
    categories = get_categories(db_session, user_id=test_user.id)
    
    assert len(categories) >= 2
    category_names = [cat.name for cat in categories]
    assert "Category 1" in category_names
    assert "Category 2" in category_names


def test_update_category(db_session, test_category):
    """Test updating a category."""
    from app.schemas.category import CategoryUpdate
    
    updated_data = CategoryUpdate(name="Updated Category Name")
    updated_category = update_category(db_session, test_category.id, updated_data)
    
    assert updated_category.name == "Updated Category Name"


def test_delete_category(db_session, test_user):
    """Test deleting a category."""
    from app.schemas.category import CategoryCreate
    
    category_data = CategoryCreate(name="To Delete Category")
    category = create_category(db_session, category=category_data, user_id=test_user.id)
    category_id = category.id
    
    deleted_category = delete_category(db_session, category_id)
    
    assert deleted_category.id == category_id
    assert get_category(db_session, category_id) is None


def test_create_and_get_note(db_session, test_user, test_category):
    """Test creating and retrieving a note."""
    from app.schemas.note import NoteCreate
    
    note_data = NoteCreate(title="Test Note 2", content="This is another test note")
    note = create_note(db_session, note=note_data, user_id=test_user.id)
    
    assert note.title == "Test Note 2"
    assert note.content == "This is another test note"
    assert note.user_id == test_user.id
    
    retrieved_note = get_note(db_session, note.id)
    assert retrieved_note is not None
    assert retrieved_note.title == "Test Note 2"


def test_get_notes(db_session, test_user, test_category):
    """Test retrieving all notes for a user."""
    from app.schemas.note import NoteCreate
    
    # Create multiple notes
    note1_data = NoteCreate(title="Note 1", content="Content 1")
    note2_data = NoteCreate(title="Note 2", content="Content 2")
    
    create_note(db_session, note=note1_data, user_id=test_user.id)
    create_note(db_session, note=note2_data, user_id=test_user.id)
    
    notes = get_notes(db_session, user_id=test_user.id)
    
    assert len(notes) >= 2
    note_titles = [note.title for note in notes]
    assert "Note 1" in note_titles
    assert "Note 2" in note_titles


def test_update_note(db_session, test_note):
    """Test updating a note."""
    from app.schemas.note import NoteUpdate
    
    updated_data = NoteUpdate(title="Updated Note Title", content="Updated note content")
    updated_note = update_note(db_session, test_note.id, updated_data)
    
    assert updated_note.title == "Updated Note Title"
    assert updated_note.content == "Updated note content"


def test_delete_note(db_session, test_user, test_category):
    """Test deleting a note."""
    from app.schemas.note import NoteCreate
    
    note_data = NoteCreate(title="To Delete Note", content="This note will be deleted")
    note = create_note(db_session, note=note_data, user_id=test_user.id)
    note_id = note.id
    
    deleted_note = delete_note(db_session, note_id)
    
    assert deleted_note.id == note_id
    assert get_note(db_session, note_id) is None