import pytest
from datetime import datetime
from src.models.note_model import Note, NoteCreate, NoteUpdate, convert_db_note_to_note
from src.services.note_service import NoteService
from src.models.note_model import NoteDB
from unittest.mock import patch


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

    def test_convert_db_note_to_note_function(self):
        """Тест функции преобразования между моделями"""
        # Создаем объект NoteDB
        db_note = NoteDB(
            id=1,
            title="Тестовая заметка",
            content="Тестовое содержимое",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Преобразуем в Note
        note = convert_db_note_to_note(db_note)
        
        # Проверяем, что преобразование выполнено корректно
        assert note.id == 1
        assert note.title == "Тестовая заметка"
        assert note.content == "Тестовое содержимое"
        assert note.created_at is not None
        assert note.updated_at is not None

    def test_convert_db_note_to_note_with_none(self):
        """Тест функции преобразования с None"""
        # Преобразуем None
        note = convert_db_note_to_note(None)
        
        # Проверяем, что возвращается None
        assert note is None

    def test_note_model_post_init(self):
        """Тест метода __post_init__ модели Note"""
        note = Note()
        # Проверяем, что даты инициализируются
        assert note.created_at is not None
        assert note.updated_at is not None
        
        # Создаем с конкретными датами
        custom_date = datetime(2023, 1, 1)
        note_with_dates = Note(created_at=custom_date, updated_at=custom_date)
        assert note_with_dates.created_at == custom_date
        assert note_with_dates.updated_at == custom_date

class TestNoteService:
    """Тесты для сервиса заметок"""
    
    def test_note_service_methods_exist(self):
        """Тест наличия методов в сервисе заметок"""
        # Проверяем, что у сервиса есть все необходимые методы
        # Создаем объект без вызова __init__ чтобы избежать подключения к БД
        service = NoteService.__new__(NoteService)
        
        # Проверяем наличие методов
        assert hasattr(service, 'create_note')
        assert hasattr(service, 'get_note')
        assert hasattr(service, 'get_all_notes')
        assert hasattr(service, 'update_note')
        assert hasattr(service, 'delete_note')
        assert hasattr(service, 'search_notes')
        assert hasattr(service, '_commit_or_rollback')
        assert hasattr(service, '_convert_db_note_to_note')