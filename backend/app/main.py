from fastapi import FastAPI
from app.api.v1 import router as api_v1_router
from app.database import engine, Base
import uvicorn
from app.metrics import MetricsMiddleware
from starlette.responses import Response
from prometheus_client import generate_latest

# Создание таблиц в БД
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Notes API",
    description="API для управления заметками",
    version="1.0.0"
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
    return {"status": "healthy"}

@app.get("/metrics")
def metrics_endpoint():
    return Response(generate_latest(), media_type="text/plain")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)