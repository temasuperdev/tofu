from sqlalchemy import Column, Integer, ForeignKey, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class NoteShare(Base):
    __tablename__ = "note_shares"
    
    id = Column(Integer, primary_key=True, index=True)
    note_id = Column(Integer, ForeignKey("notes.id"), nullable=False)
    shared_with_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    permission_level = Column(String(20), nullable=False)  # read, write, admin
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связи
    note = relationship("Note", back_populates="shares")
    shared_with_user = relationship("User")