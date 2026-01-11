from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Глобальные переменные для движка и сессии
engine = None
SessionLocal = None

def init_db_engine(database_url=None):
    global engine, SessionLocal
    if database_url is None:
        database_url = settings.DATABASE_URL
    
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine

# Базовый класс для моделей
Base = declarative_base()

# Зависимость для получения сессии базы данных
def get_db():
    if SessionLocal is None:
        init_db_engine()
        
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()