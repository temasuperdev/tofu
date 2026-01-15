from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import router as api_v1_router
from app.database import Base, init_db_engine
import uvicorn
from app.metrics import MetricsMiddleware
from starlette.responses import Response
from prometheus_client import generate_latest
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Инициализация подключения к БД при запуске приложения
    init_db_engine()
    yield
    # Здесь можно добавить логику завершения работы приложения

app = FastAPI(
    title="Notes API",
    description="API для управления заметками",
    version="1.0.0",
    lifespan=lifespan
)

# Настройка CORS
cors_origins = os.getenv("BACKEND_CORS_ORIGINS", "http://localhost:8080").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in cors_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Добавление middleware для метрик
app.add_middleware(MetricsMiddleware)

# Подключение маршрутов
app.include_router(api_v1_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Notes API"}

@app.get("/health")
def health_check():
    """Проверка здоровья приложения с проверкой подключения к БД"""
    try:
        from app.database import engine
        from sqlalchemy import text
        if engine is None:
            return {"status": "unhealthy", "reason": "database_not_initialized"}, 503
        
        # Проверка подключения к БД
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        return {"status": "healthy"}
    except Exception as e:
        return {"status": "unhealthy", "reason": str(e)}, 503

@app.get("/metrics")
def metrics_endpoint():
    return Response(generate_latest(), media_type="text/plain")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)