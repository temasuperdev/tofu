import os
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from ..models.note_model import Note, NoteCreate, NoteUpdate
from ..utils.logging_config import configure_logging
from ..config import get_config


# Настройка структурированного логирования
logger = configure_logging()

# Получение конфигурации
config = get_config()

# SQLAlchemy setup
Base = declarative_base()


class NoteDB(Base):
    __tablename__ = 'notes'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class NoteService:
    def __init__(self, database_url=None):
        # Получаем URL базы данных из конфигурации или параметра
        if database_url:
            self.database_url = database_url
        else:
            # Получаем URL базы данных из конфигурации
            self.database_url = config.SQLALCHEMY_DATABASE_URI
            if not self.database_url:
                # По умолчанию используем PostgreSQL
                db_user = os.getenv('DB_USER', 'postgres')
                db_password = os.getenv('DB_PASSWORD', 'postgres')
                db_host = os.getenv('DB_HOST', 'localhost')
                db_port = os.getenv('DB_PORT', '5432')
                db_name = os.getenv('DB_NAME', 'notes_db')
                self.database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

        self.engine = create_engine(self.database_url)
        Base.metadata.create_all(bind=self.engine)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.db = SessionLocal()

    def create_note(self, note_create: NoteCreate) -> Note:
        """
        Создание новой заметки
        """
        try:
            db_note = NoteDB(
                title=note_create.title,
                content=note_create.content,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            self.db.add(db_note)
            self.db.commit()
            self.db.refresh(db_note)
            
            # Возвращаем объект Note вместо NoteDB
            return Note(
                id=db_note.id,
                title=db_note.title,
                content=db_note.content,
                created_at=db_note.created_at,
                updated_at=db_note.updated_at
            )
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error while creating note: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error creating note: {str(e)}")
            raise

    def get_note(self, note_id: int) -> Optional[Note]:
        """
        Получение заметки по ID
        """
        try:
            db_note = self.db.query(NoteDB).filter(NoteDB.id == note_id).first()
            if db_note:
                return Note(
                    id=db_note.id,
                    title=db_note.title,
                    content=db_note.content,
                    created_at=db_note.created_at,
                    updated_at=db_note.updated_at
                )
            return None
        except SQLAlchemyError as e:
            logger.error(f"Database error while getting note: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error getting note: {str(e)}")
            raise

    def get_all_notes(self, skip: int = 0, limit: int = 100) -> List[Note]:
        """
        Получение всех заметок с пагинацией
        """
        try:
            db_notes = self.db.query(NoteDB).offset(skip).limit(limit).all()
            return [
                Note(
                    id=db_note.id,
                    title=db_note.title,
                    content=db_note.content,
                    created_at=db_note.created_at,
                    updated_at=db_note.updated_at
                )
                for db_note in db_notes
            ]
        except SQLAlchemyError as e:
            logger.error(f"Database error while getting notes: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error getting notes: {str(e)}")
            raise

    def update_note(self, note_id: int, note_update: NoteUpdate) -> Optional[Note]:
        """
        Обновление заметки
        """
        try:
            db_note = self.db.query(NoteDB).filter(NoteDB.id == note_id).first()
            if not db_note:
                return None
            
            # Обновляем поля, если они предоставлены
            if note_update.title is not None:
                db_note.title = note_update.title
            if note_update.content is not None:
                db_note.content = note_update.content
            
            db_note.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(db_note)
            
            return Note(
                id=db_note.id,
                title=db_note.title,
                content=db_note.content,
                created_at=db_note.created_at,
                updated_at=db_note.updated_at
            )
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error while updating note: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error updating note: {str(e)}")
            raise

    def delete_note(self, note_id: int) -> bool:
        """
        Удаление заметки
        """
        try:
            db_note = self.db.query(NoteDB).filter(NoteDB.id == note_id).first()
            if not db_note:
                return False
            
            self.db.delete(db_note)
            self.db.commit()
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error while deleting note: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error deleting note: {str(e)}")
            raise

    def search_notes(self, query: str, skip: int = 0, limit: int = 100) -> List[Note]:
        """
        Поиск заметок по заголовку или содержимому
        """
        try:
            db_notes = self.db.query(NoteDB).filter(
                (NoteDB.title.contains(query)) | (NoteDB.content.contains(query))
            ).offset(skip).limit(limit).all()
            return [
                Note(
                    id=db_note.id,
                    title=db_note.title,
                    content=db_note.content,
                    created_at=db_note.created_at,
                    updated_at=db_note.updated_at
                )
                for db_note in db_notes
            ]
        except SQLAlchemyError as e:
            logger.error(f"Database error while searching notes: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error searching notes: {str(e)}")
            raise