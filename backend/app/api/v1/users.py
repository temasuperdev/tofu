from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User as UserModel
from app.schemas.user import User
from app.security.auth import get_current_user

router = APIRouter(tags=["users"])

@router.get("/me", response_model=User)
def read_current_user(current_user: UserModel = Depends(get_current_user)):
    return current_user