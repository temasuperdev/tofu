from flask import request, jsonify
from marshmallow import ValidationError
from datetime import datetime
import logging
import time
from sqlalchemy.exc import OperationalError
from ..services.note_service import NoteService
from ..models.note_model import NoteCreate, NoteUpdate, convert_db_note_to_note
from ..utils.logging_config import configure_logging
from ..utils.error_handlers import handle_exceptions
from ..config import get_config


# Настройка структурированного логирования
logger = configure_logging()

# Получение конфигурации
config = get_config()

# Сервис для работы с заметками (инициализируется при первом использовании)
_note_service_instance = None


def get_note_service():
    global _note_service_instance
    if _note_service_instance is None:
        # Повторная попытка инициализации сервиса при проблемах с подключением
        max_retries = 5
        retry_count = 0
        while retry_count < max_retries:
            try:
                _note_service_instance = NoteService()
                break
            except OperationalError as e:
                retry_count += 1
                if retry_count >= max_retries:
                    logger.error(f"Не удалось инициализировать сервис заметок после {max_retries} попыток: {str(e)}")
                    raise
                else:
                    logger.warning(f"Попытка {retry_count} инициализации сервиса не удалась: {str(e)}. Повтор через 3 секунды...")
                    time.sleep(3)
    return _note_service_instance


@handle_exceptions(logger=logger)
def create_note_controller():
    """Контроллер для создания заметки"""
    # Проверяем, является ли запрос JSON
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400

    # Получаем JSON-данные из запроса
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # Проверяем наличие обязательных полей
    if 'title' not in data or 'content' not in data:
        return jsonify({'error': 'Title and content are required'}), 400

    # Убедимся, что в данных нет ID, который может привести к путанице
    if 'id' in data:
        logger.warning(f"ID field provided in POST request, ignoring it. Creating new note.")
    
    # Создаем объект NoteCreate
    note_create = NoteCreate(
        title=data['title'],
        content=data['content']
    )

    # Создаем заметку через сервис
    note = get_note_service().create_note(note_create)

    # Логируем создание заметки
    logger.info(f"Note created successfully with ID: {note.id}")

    return jsonify({
        'id': note.id,
        'title': note.title,
        'content': note.content,
        'created_at': note.created_at.isoformat(),
        'updated_at': note.updated_at.isoformat()
    }), 201


@handle_exceptions(logger=logger)
def get_note_controller(note_id):
    """Контроллер для получения заметки по ID"""
    note = get_note_service().get_note(note_id)
    
    if not note:
        return jsonify({'error': 'Note not found'}), 404

    return jsonify({
        'id': note.id,
        'title': note.title,
        'content': note.content,
        'created_at': note.created_at.isoformat(),
        'updated_at': note.updated_at.isoformat()
    }), 200


@handle_exceptions(logger=logger)
def get_all_notes_controller():
    """Контроллер для получения всех заметок"""
    # Получаем параметры пагинации из запроса
    skip = int(request.args.get('skip', 0))
    limit = int(request.args.get('limit', 100))

    # Ограничиваем максимальное значение limit
    if limit > 1000:
        limit = 1000

    notes = get_note_service().get_all_notes(skip=skip, limit=limit)

    return jsonify({
        'notes': [
            {
                'id': note.id,
                'title': note.title,
                'content': note.content,
                'created_at': note.created_at.isoformat(),
                'updated_at': note.updated_at.isoformat()
            }
            for note in notes
        ],
        'total': get_note_service().get_all_notes_count(),  # Обновленный метод для получения общего количества заметок
        'skip': skip,
        'limit': limit
    }), 200


@handle_exceptions(logger=logger)
def update_note_controller(note_id):
    """Контроллер для обновления заметки"""
    # Проверяем, является ли запрос JSON
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400

    # Получаем JSON-данные из запроса
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # Создаем объект NoteUpdate
    note_update = NoteUpdate(
        title=data.get('title'),
        content=data.get('content')
    )

    # Обновляем заметку через сервис
    note = get_note_service().update_note(note_id, note_update)
    
    if not note:
        return jsonify({'error': 'Note not found'}), 404

    # Логируем обновление заметки
    logger.info(f"Note updated successfully with ID: {note.id}")

    return jsonify({
        'id': note.id,
        'title': note.title,
        'content': note.content,
        'created_at': note.created_at.isoformat(),
        'updated_at': note.updated_at.isoformat()
    }), 200


@handle_exceptions(logger=logger)
def delete_note_controller(note_id):
    """Контроллер для удаления заметки"""
    # Удаляем заметку через сервис
    deleted = get_note_service().delete_note(note_id)
    
    if not deleted:
        return jsonify({'error': 'Note not found'}), 404

    # Логируем удаление заметки
    logger.info(f"Note deleted successfully with ID: {note_id}")

    return jsonify({'message': 'Note deleted successfully'}), 200


@handle_exceptions(logger=logger)
def search_notes_controller():
    """Контроллер для поиска заметок"""
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': 'Query parameter "q" is required'}), 400

    # Получаем параметры пагинации из запроса
    skip = int(request.args.get('skip', 0))
    limit = int(request.args.get('limit', 100))

    # Ограничиваем максимальное значение limit
    if limit > 1000:
        limit = 1000

    notes = get_note_service().search_notes(query=query, skip=skip, limit=limit)

    return jsonify({
        'notes': [
            {
                'id': note.id,
                'title': note.title,
                'content': note.content,
                'created_at': note.created_at.isoformat(),
                'updated_at': note.updated_at.isoformat()
            }
            for note in notes
        ],
        'total': len(notes),
        'skip': skip,
        'limit': limit,
        'query': query
    }), 200