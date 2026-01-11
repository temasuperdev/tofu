from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime

class NoteBase(BaseModel):
    title: str
    content: Optional[str] = None
    is_public: bool = False
    category: Optional[str] = None
    tags: Optional[List[str]] = []

    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        if not v or v.strip() == "":
            raise ValueError('Title cannot be empty')
        return v.strip()

class NoteCreate(NoteBase):
    pass

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    is_public: Optional[bool] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None

class NoteResponse(NoteBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Для обратной совместимости
Note = NoteResponse