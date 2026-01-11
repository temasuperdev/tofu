import bcrypt
from typing import Union


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Конвертируем строки в байты, если необходимо
    if isinstance(plain_password, str):
        plain_password = plain_password.encode('utf-8')
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')
    
    try:
        return bcrypt.checkpw(plain_password, hashed_password)
    except ValueError:
        return False


def get_password_hash(password: str) -> str:
    # Усекаем пароль до 72 байт вручную, чтобы избежать ошибки bcrypt
    if len(password) > 72:
        password = password[:72]
    # Конвертируем строку в байты
    password_bytes = password.encode('utf-8')
    # Хешируем пароль
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    # Возвращаем строку
    return hashed.decode('utf-8')


def hash_password(password: str) -> str:
    return get_password_hash(password)