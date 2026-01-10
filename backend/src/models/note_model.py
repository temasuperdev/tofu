from dataclasses import dataclass
from datetime import datetime
from typing import Optional


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