import os
from typing import List, Optional
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from ..models.note_model import Note, NoteCreate, NoteUpdate, Base, NoteDB, convert_db_note_to_note
from ..utils.logging_config import configure_logging
from ..config import get_config


# Настройка структурированного логирования
logger = configure_logging()

# Получение конфигурации
config = get_config()


class NoteService:
    def __init__(self, database_url=None):
        # Получаем URL базы данных из конфигурации или параметра
        if database_url:
            self.database_url = database_url
        else:
            # Получаем URL базы данных из конфигурации
            self.database_url = config.SQLALCHEMY_DATABASE_URI
            if not self.database_url:
                # По умолчанию используем SQLite для локальной разработки
                db_type = os.getenv('DB_TYPE', 'sqlite')
                if db_type == 'sqlite':
                    db_name = os.getenv('DB_NAME', 'notes_db')
                    self.database_url = f"sqlite:///./{db_name}.db"
                else:
                    # Для PostgreSQL
                    db_user = os.getenv('DB_USER', 'postgres')
                    db_password = os.getenv('DB_PASSWORD', 'postgres')
                    db_host = os.getenv('DB_HOST', 'localhost')
                    db_port = os.getenv('DB_PORT', '5432')
                    db_name = os.getenv('DB_NAME', 'notes_db')
                    self.database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

        # Для SQLite используем правильные параметры подключения
        if self.database_url.startswith('sqlite'):
            self.engine = create_engine(self.database_url, connect_args={"check_same_thread": False})
        else:
            # Для PostgreSQL используем параметры подключения с повторными попытками
            from sqlalchemy.pool import QueuePool
            self.engine = create_engine(
                self.database_url,
                poolclass=QueuePool,
                pool_size=20,  # Увеличенный размер пула для многоподового окружения
                pool_recycle=3600,  # Повторное использование соединений
                pool_pre_ping=True,  # Проверяет соединения перед использованием
                pool_timeout=20,
                max_overflow=30,
                echo=False  # Установите в True для отладки
            )
        
        # Повторные попытки создания таблиц на случай, если БД еще не готова
        max_retries = 10
        retry_count = 0
        while retry_count < max_retries:
            try:
                Base.metadata.create_all(bind=self.engine)
                break
            except Exception as e:
                retry_count += 1
                if retry_count >= max_retries:
                    logger.error(f"Не удалось создать таблицы после {max_retries} попыток: {str(e)}")
                    raise
                else:
                    logger.warning(f"Попытка {retry_count} создания таблиц не удалась: {str(e)}. Повтор через 5 секунд...")
                    import time
                    time.sleep(5)
        
        # Создаем фабрику сессий как атрибут класса, чтобы использовать её при каждом вызове
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def get_db_session(self):
        """
        Создание новой сессии базы данных для каждой операции
        Это обеспечивает согласованность данных между подами
        """
        return self.SessionLocal()

    def _commit_or_rollback(self, db_session):
        """Общая логика фиксации транзакции или отката"""
        try:
            db_session.commit()
        except SQLAlchemyError:
            db_session.rollback()
            raise

    def _convert_db_note_to_note(self, db_note) -> Optional[Note]:
        """Преобразование объекта NoteDB в объект Note"""
        return convert_db_note_to_note(db_note)

    def create_note(self, note_create: NoteCreate) -> Note:
        """
        Создание новой заметки
        """
        db_session = self.get_db_session()
        try:
            db_note = NoteDB(
                title=note_create.title,
                content=note_create.content,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db_session.add(db_note)
            self._commit_or_rollback(db_session)
            db_session.refresh(db_note)
            
            # Проверяем, что ID был корректно назначен
            if db_note.id is None:
                logger.error("Note ID is None after creation and refresh - this indicates a database issue")
                raise Exception("Failed to assign ID to new note")
            
            # Возвращаем объект Note вместо NoteDB
            result = self._convert_db_note_to_note(db_note)
            logger.debug(f"Created note with ID: {db_note.id}")
            return result
        except SQLAlchemyError as e:
            logger.error(f"Database error while creating note: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error creating note: {str(e)}")
            raise
        finally:
            db_session.close()

    def get_note(self, note_id: int) -> Optional[Note]:
        """
        Получение заметки по ID
        """
        db_session = self.get_db_session()
        try:
            db_note = db_session.query(NoteDB).filter(NoteDB.id == note_id).first()
            return self._convert_db_note_to_note(db_note)
        except SQLAlchemyError as e:
            logger.error(f"Database error while getting note: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error getting note: {str(e)}")
            raise
        finally:
            db_session.close()

    def get_all_notes(self, skip: int = 0, limit: int = 100) -> List[Note]:
        """
        Получение всех заметок с пагинацией
        """
        db_session = self.get_db_session()
        try:
            db_notes = db_session.query(NoteDB).order_by(NoteDB.id).offset(skip).limit(limit).all()
            return [
                self._convert_db_note_to_note(db_note)
                for db_note in db_notes
            ]
        except SQLAlchemyError as e:
            logger.error(f"Database error while getting notes: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error getting notes: {str(e)}")
            raise
        finally:
            db_session.close()

    def update_note(self, note_id: int, note_update: NoteUpdate) -> Optional[Note]:
        """
        Обновление заметки
        """
        db_session = self.get_db_session()
        try:
            db_note = db_session.query(NoteDB).filter(NoteDB.id == note_id).first()
            if not db_note:
                return None
            
            # Обновляем поля, если они предоставлены
            if note_update.title is not None:
                db_note.title = note_update.title
            if note_update.content is not None:
                db_note.content = note_update.content
            
            db_note.updated_at = datetime.utcnow()
            self._commit_or_rollback(db_session)
            db_session.refresh(db_note)
            
            result = self._convert_db_note_to_note(db_note)
            return result
        except SQLAlchemyError as e:
            logger.error(f"Database error while updating note: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error updating note: {str(e)}")
            raise
        finally:
            db_session.close()

    def delete_note(self, note_id: int) -> bool:
        """
        Удаление заметки
        """
        db_session = self.get_db_session()
        try:
            db_note = db_session.query(NoteDB).filter(NoteDB.id == note_id).first()
            if not db_note:
                return False
            
            db_session.delete(db_note)
            self._commit_or_rollback(db_session)
            return True
        except SQLAlchemyError as e:
            logger.error(f"Database error while deleting note: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error deleting note: {str(e)}")
            raise
        finally:
            db_session.close()

    def get_all_notes_count(self) -> int:
        """
        Получение общего количества заметок
        """
        db_session = self.get_db_session()
        try:
            count = db_session.query(NoteDB).count()
            return count
        except SQLAlchemyError as e:
            logger.error(f"Database error while counting notes: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error counting notes: {str(e)}")
            raise
        finally:
            db_session.close()

    def search_notes(self, query: str, skip: int = 0, limit: int = 100) -> List[Note]:
        """
        Поиск заметок по заголовку или содержимому
        """
        db_session = self.get_db_session()
        try:
            db_notes = db_session.query(NoteDB).filter(
                (NoteDB.title.contains(query)) | (NoteDB.content.contains(query))
            ).order_by(NoteDB.id).offset(skip).limit(limit).all()
            return [
                self._convert_db_note_to_note(db_note)
                for db_note in db_notes
            ]
        except SQLAlchemyError as e:
            logger.error(f"Database error while searching notes: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error searching notes: {str(e)}")
            raise
        finally:
            db_session.close()