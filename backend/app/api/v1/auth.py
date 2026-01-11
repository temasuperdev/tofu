from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database import get_db
from app.schemas.auth import LoginRequest, RegisterRequest
from app.schemas.user import User
from app.security.auth import authenticate_user, create_access_token, get_current_user
from app.security.password import get_password_hash
from app.crud.user import create_user, get_user_by_username
from app.config import settings

router = APIRouter(tags=["auth"])

@router.post("/login", response_model=dict)
def login(login_request: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, login_request.username, login_request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=User)
def register(register_request: RegisterRequest, db: Session = Depends(get_db)):
    # Проверяем, что пользователь с таким именем или email еще не существует
    existing_user = get_user_by_username(db, register_request.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Хешируем пароль
    hashed_password = get_password_hash(register_request.password)
    
    # Создаем пользователя
    user = create_user(
        db=db,
        username=register_request.username,
        email=register_request.email,
        password=register_request.password
    )
    
    return user