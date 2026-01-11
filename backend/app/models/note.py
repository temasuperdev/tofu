from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Note(Base):
    __tablename__ = "notes"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)  # Добавляем внешний ключ на категории
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_public = Column(Boolean, default=False)
    category_name = Column(String(50))  # Поле для имени категории, если не используем связь
    tags = Column(String)  # Временно используем строку для совместимости с SQLite
    
    # Связи
    owner = relationship("User", back_populates="notes")
    category_rel = relationship("Category", back_populates="notes")
    shares = relationship("NoteShare", back_populates="note")