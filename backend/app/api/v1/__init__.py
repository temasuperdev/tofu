from fastapi import APIRouter
from app.api.v1 import auth, users, notes, categories

router = APIRouter()

# Подключение маршрутов
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(users.router, prefix="/users", tags=["users"])
router.include_router(notes.router, prefix="/notes", tags=["notes"])
router.include_router(categories.router, prefix="/categories", tags=["categories"])
