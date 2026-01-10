import pytest
from datetime import datetime
from src.models.note_model import Note, NoteCreate, NoteUpdate


class TestNoteModel:
    """Тесты для модели заметки"""
    
    def test_note_model_defaults(self):
        """Тест значений по умолчанию для модели заметки"""
        note = Note()
        
        # Проверяем значения по умолчанию
        assert note.id is None
        assert note.title == ""
        assert note.content == ""
        assert note.created_at is not None
        assert note.updated_at is not None

    def test_note_create_model(self):
        """Тест модели создания заметки"""
        note_create = NoteCreate(
            title="Заголовок",
            content="Содержимое"
        )
        
        assert note_create.title == "Заголовок"
        assert note_create.content == "Содержимое"

    def test_note_update_model(self):
        """Тест модели обновления заметки"""
        note_update = NoteUpdate(
            title="Обновленный заголовок",
            content="Обновленное содержимое"
        )
        
        assert note_update.title == "Обновленный заголовок"
        assert note_update.content == "Обновленное содержимое"
        
        # Тест с частичным обновлением
        partial_update = NoteUpdate(title="Новый заголовок")
        assert partial_update.title == "Новый заголовок"
        assert partial_update.content is None

    def test_create_note(self):
        """Тест создания заметки"""
        # Создаем объект NoteCreate
        note_create = NoteCreate(
            title="Тестовая заметка",
            content="Содержимое тестовой заметки"
        )
        
        # Создаем заметку
        note = Note(
            id=1,
            title=note_create.title,
            content=note_create.content,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Проверяем, что заметка создана с правильными параметрами
        assert note.title == "Тестовая заметка"
        assert note.content == "Содержимое тестовой заметки"
        assert note.id == 1
        assert note.created_at is not None
        assert note.updated_at is not None