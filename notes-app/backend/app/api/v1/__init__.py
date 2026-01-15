from .notes import router as notes_router
from .auth import router as auth_router

__all__ = ["notes_router", "auth_router"]