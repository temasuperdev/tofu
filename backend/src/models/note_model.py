from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base


# SQLAlchemy Base
Base = declarative_base()


@dataclass
class Note:
    id: Optional[int] = None
    title: str = ""
    content: str = ""
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()


@dataclass
class NoteCreate:
    title: str
    content: str


@dataclass
class NoteUpdate:
    title: Optional[str] = None
    content: Optional[str] = None


# SQLAlchemy model
class NoteDB(Base):
    __tablename__ = 'notes'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Функция для преобразования между моделями
def convert_db_note_to_note(db_note) -> Optional[Note]:
    """Преобразование объекта NoteDB в объект Note"""
    if db_note:
        return Note(
            id=db_note.id,
            title=db_note.title,
            content=db_note.content,
            created_at=db_note.created_at,
            updated_at=db_note.updated_at
        )
    return None