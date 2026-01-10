#!/usr/bin/env python3
"""
Тест для проверки присвоения следующего по порядку ID новым заметкам
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from src.services.note_service import NoteService
from src.models.note_model import NoteCreate
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.note_model import Base, NoteDB

def test_note_id_assignment():
    # Создаем временную базу данных для теста
    engine = create_engine('sqlite:///:memory:', echo=True)
    Base.metadata.create_all(bind=engine)
    
    # Создаем сессию
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Создаем сервис с временной базой данных
    service = NoteService(database_url='sqlite:///:memory:')
    
    # Убедимся, что у нас нет никаких заметок
    with SessionLocal() as session:
        existing_notes = session.query(NoteDB).all()
        print(f"Начальное количество заметок: {len(existing_notes)}")
    
    # Создаем несколько заметок и проверим, что им присваиваются последовательные ID
    note1 = service.create_note(NoteCreate(title="Заметка 1", content="Содержимое заметки 1"))
    print(f"Создана заметка с ID: {note1.id}")
    assert note1.id == 1, f"Ожидался ID 1, получен {note1.id}"
    
    note2 = service.create_note(NoteCreate(title="Заметка 2", content="Содержимое заметки 2"))
    print(f"Создана заметка с ID: {note2.id}")
    assert note2.id == 2, f"Ожидался ID 2, получен {note2.id}"
    
    note3 = service.create_note(NoteCreate(title="Заметка 3", content="Содержимое заметки 3"))
    print(f"Создана заметка с ID: {note3.id}")
    assert note3.id == 3, f"Ожидался ID 3, получен {note3.id}"
    
    # Проверим, что теперь у нас 3 заметки с правильными ID
    all_notes = service.get_all_notes()
    print(f"Общее количество заметок: {len(all_notes)}")
    
    expected_ids = [1, 2, 3]
    actual_ids = [note.id for note in all_notes]
    assert actual_ids == expected_ids, f"Ожидались ID {expected_ids}, получены {actual_ids}"
    
    print("Тест пройден успешно! Новые заметки получают следующие по порядку ID.")

if __name__ == "__main__":
    test_note_id_assignment()