from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.user import User
from app.schemas.user import UserCreate

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, username: str, email: str, password: str):
    from app.security.password import get_password_hash
    # Усекаем пароль до 72 символов, чтобы избежать ошибки bcrypt
    if len(password) > 72:
        password = password[:72]
    password_hash = get_password_hash(password)
    db_user = User(username=username, email=email, password_hash=password_hash)
    db.add(db_user)
    try:
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        # Проверяем, какой именно уникальный ключ был нарушен
        existing_user_by_username = get_user_by_username(db, username)
        if existing_user_by_username:
            raise ValueError("Username already registered")
        
        existing_user_by_email = get_user_by_email(db, email)
        if existing_user_by_email:
            raise ValueError("Email already registered")
        
        # Если другая ошибка целостности, повторно выбрасываем
        raise

def update_user(db: Session, user_id: int, **kwargs):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        for key, value in kwargs.items():
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user