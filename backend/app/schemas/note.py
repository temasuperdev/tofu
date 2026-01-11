from pydantic import BaseModel, field_validator, ConfigDict
from typing import Optional, List
from datetime import datetime

class NoteBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    title: str
    content: Optional[str] = None
    is_public: bool = False
    category: Optional[str] = None
    category_id: Optional[int] = None
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
    model_config = ConfigDict(from_attributes=True)
    title: Optional[str] = None
    content: Optional[str] = None
    is_public: Optional[bool] = None
    category: Optional[str] = None
    category_id: Optional[int] = None
    tags: Optional[List[str]] = None

class NoteResponse(NoteBase):
    id: int
    user_id: int
    category_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    @field_validator('tags', mode='before')
    @classmethod
    def validate_tags(cls, v):
        if isinstance(v, str):
            if v == '':
                return []
            return v.split(',')
        return v

# Для обратной совместимости
Note = NoteResponse