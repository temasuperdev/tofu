from flask import request, jsonify
from marshmallow import ValidationError
from datetime import datetime
import logging
from ..services.note_service import NoteService
from ..models.note_model import NoteCreate, NoteUpdate
from ..utils.logging_config import configure_logging
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
        _note_service_instance = NoteService()
    return _note_service_instance


def create_note_controller():
    """Контроллер для создания заметки"""
    try:
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

    except ValidationError as e:
        logger.error(f"Validation error creating note: {str(e)}")
        return jsonify({'error': 'Validation error', 'details': e.messages}), 400
    except Exception as e:
        logger.error(f"Error creating note: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


def get_note_controller(note_id):
    """Контроллер для получения заметки по ID"""
    try:
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

    except Exception as e:
        logger.error(f"Error getting note: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


def get_all_notes_controller():
    """Контроллер для получения всех заметок"""
    try:
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
            'total': len(notes),
            'skip': skip,
            'limit': limit
        }), 200

    except ValueError:
        return jsonify({'error': 'Invalid skip or limit parameter'}), 400
    except Exception as e:
        logger.error(f"Error getting all notes: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


def update_note_controller(note_id):
    """Контроллер для обновления заметки"""
    try:
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

    except ValidationError as e:
        logger.error(f"Validation error updating note: {str(e)}")
        return jsonify({'error': 'Validation error', 'details': e.messages}), 400
    except Exception as e:
        logger.error(f"Error updating note: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


def delete_note_controller(note_id):
    """Контроллер для удаления заметки"""
    try:
        # Удаляем заметку через сервис
        deleted = get_note_service().delete_note(note_id)
        
        if not deleted:
            return jsonify({'error': 'Note not found'}), 404

        # Логируем удаление заметки
        logger.info(f"Note deleted successfully with ID: {note_id}")

        return jsonify({'message': 'Note deleted successfully'}), 200

    except Exception as e:
        logger.error(f"Error deleting note: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


def search_notes_controller():
    """Контроллер для поиска заметок"""
    try:
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

    except ValueError:
        return jsonify({'error': 'Invalid skip or limit parameter'}), 400
    except Exception as e:
        logger.error(f"Error searching notes: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500