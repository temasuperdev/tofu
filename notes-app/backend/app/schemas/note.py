from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid


class NoteBase(BaseModel):
    title: str
    content: str
    is_public: bool = False


class NoteCreate(NoteBase):
    pass


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    is_public: Optional[bool] = None


class NoteInDB(NoteBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NotePublic(BaseModel):
    id: uuid.UUID
    title: str
    content: str
    user_id: uuid.UUID
    is_public: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True