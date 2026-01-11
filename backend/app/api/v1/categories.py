from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.crud.category import get_categories, get_category, create_category, update_category, delete_category
from app.schemas.category import Category, CategoryCreate, CategoryUpdate
from app.security.auth import get_current_user
from app.models.user import User as UserModel

router = APIRouter(prefix="/categories", tags=["categories"])

@router.get("/", response_model=list[Category])
def read_categories(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    categories = get_categories(db, skip=skip, limit=limit, user_id=current_user.id)
    return categories

@router.get("/{category_id}", response_model=Category)
def read_category(
    category_id: int, 
    db: Session = Depends(get_db), 
    current_user: UserModel = Depends(get_current_user)
):
    category = get_category(db, category_id=category_id)
    if not category or category.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.post("/", response_model=Category, status_code=status.HTTP_201_CREATED)
def create_new_category(
    category: CategoryCreate, 
    db: Session = Depends(get_db), 
    current_user: UserModel = Depends(get_current_user)
):
    return create_category(db=db, category=category, user_id=current_user.id)

@router.put("/{category_id}", response_model=Category)
def update_existing_category(
    category_id: int, 
    category: CategoryUpdate, 
    db: Session = Depends(get_db), 
    current_user: UserModel = Depends(get_current_user)
):
    db_category = get_category(db, category_id=category_id)
    if not db_category or db_category.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Category not found")
    return update_category(db=db, category_id=category_id, category=category)

@router.delete("/{category_id}")
def delete_existing_category(
    category_id: int, 
    db: Session = Depends(get_db), 
    current_user: UserModel = Depends(get_current_user)
):
    db_category = get_category(db, category_id=category_id)
    if not db_category or db_category.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Category not found")
    delete_category(db=db, category_id=category_id)
    return {"message": "Category deleted successfully"}