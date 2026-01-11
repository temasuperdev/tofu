from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class CategoryBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: Optional[str] = None
    description: Optional[str] = None

class CategoryResponse(CategoryBase):
    id: int
    user_id: int
    created_at: datetime

# Для обратной совместимости
Category = CategoryResponse