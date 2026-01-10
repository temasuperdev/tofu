from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Message:
    id: Optional[int] = None
    content: str = ""
    created_at: datetime = None
    pod_name: str = ""

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()