from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.crud.note import get_notes, get_note, create_note, update_note, delete_note
from app.schemas.note import Note, NoteCreate, NoteUpdate
from app.security.auth import get_current_user
from app.models.user import User as UserModel

router = APIRouter(prefix="/notes", tags=["notes"])

@router.get("/", response_model=list[Note])
def read_notes(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    notes = get_notes(db, skip=skip, limit=limit, user_id=current_user.id)
    return notes

@router.get("/{note_id}", response_model=Note)
def read_note(
    note_id: int, 
    db: Session = Depends(get_db), 
    current_user: UserModel = Depends(get_current_user)
):
    note = get_note(db, note_id=note_id)
    if not note or note.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@router.post("/", response_model=Note, status_code=status.HTTP_201_CREATED)
def create_new_note(
    note: NoteCreate, 
    db: Session = Depends(get_db), 
    current_user: UserModel = Depends(get_current_user)
):
    return create_note(db=db, note=note, user_id=current_user.id)

@router.put("/{note_id}", response_model=Note)
def update_existing_note(
    note_id: int, 
    note: NoteUpdate, 
    db: Session = Depends(get_db), 
    current_user: UserModel = Depends(get_current_user)
):
    db_note = get_note(db, note_id=note_id)
    if not db_note or db_note.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Note not found")
    return update_note(db=db, note_id=note_id, note=note)

@router.delete("/{note_id}")
def delete_existing_note(
    note_id: int, 
    db: Session = Depends(get_db), 
    current_user: UserModel = Depends(get_current_user)
):
    db_note = get_note(db, note_id=note_id)
    if not db_note or db_note.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Note not found")
    delete_note(db=db, note_id=note_id)
    return {"message": "Note deleted successfully"}