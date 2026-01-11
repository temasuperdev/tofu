from pydantic import BaseModel, field_validator, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    username: str
    email: EmailStr

    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters long')
        if len(v) > 50:
            raise ValueError('Username must be at most 50 characters long')
        return v

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        # Валидация email уже встроена в EmailStr
        return v

class UserCreate(UserBase):
    password: str

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class UserUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    username: Optional[str] = None
    email: Optional[str] = None

class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool

# Для обратной совместимости
User = UserResponse