from functools import wraps
from flask import jsonify
import logging
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from marshmallow import ValidationError


def handle_exceptions(logger=None):
    """
    Декоратор для обработки общих исключений в контроллерах
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except OperationalError as e:
                if logger:
                    logger.error(f"Operational database error in {func.__name__}: {str(e)}")
                return jsonify({'error': 'Database operational error'}), 500
            except SQLAlchemyError as e:
                if logger:
                    logger.error(f"Database error in {func.__name__}: {str(e)}")
                return jsonify({'error': 'Database error'}), 500
            except ValueError as e:
                if logger:
                    logger.error(f"Value error in {func.__name__}: {str(e)}")
                return jsonify({'error': 'Invalid value provided'}), 400
            except Exception as e:
                if logger:
                    logger.error(f"Unexpected error in {func.__name__}: {str(e)}")
                return jsonify({'error': 'Internal server error'}), 500
        return wrapper
    return decorator


def handle_validation_errors(logger=None):
    """
    Декоратор для обработки ошибок валидации
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ValidationError as e:
                if logger:
                    logger.error(f"Validation error in {func.__name__}: {str(e)}")
                return jsonify({'error': 'Validation error', 'details': e.messages}), 400
            except Exception as e:
                # Если это другая ошибка, передаем её дальше
                if isinstance(e, (OperationalError, SQLAlchemyError, ValueError)):
                    # Используем общий обработчик
                    raise e
                else:
                    if logger:
                        logger.error(f"Unexpected error in {func.__name__}: {str(e)}")
                    return jsonify({'error': 'Internal server error'}), 500
        return wrapper
    return decorator