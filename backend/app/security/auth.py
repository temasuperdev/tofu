from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.config import settings
from app.models.user import User
from app.database import get_db
from app.crud.user import get_user_by_username
import bcrypt

# Настройка OAuth2 схемы
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def verify_password(plain_password, hashed_password):
    # Ограничиваем длину пароля до 72 символов, как того требует bcrypt
    if len(plain_password) > 72:
        plain_password = plain_password[:72]
    # Конвертируем строки в байты, если необходимо
    if isinstance(plain_password, str):
        plain_password = plain_password.encode('utf-8')
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')
    
    try:
        return bcrypt.checkpw(plain_password, hashed_password)
    except ValueError:
        return False

def get_password_hash(password):
    # Ограничиваем длину пароля до 72 символов, как того требует bcrypt
    if len(password) > 72:
        password = password[:72]
    # Конвертируем строку в байты
    password_bytes = password.encode('utf-8')
    # Хешируем пароль
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    # Возвращаем строку
    return hashed.decode('utf-8')

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user or not verify_password(password, user.password_hash):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return user