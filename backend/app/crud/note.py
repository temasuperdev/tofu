from sqlalchemy.orm import Session
from app.models.note import Note
from app.schemas.note import NoteCreate, NoteUpdate

def get_note(db: Session, note_id: int):
    return db.query(Note).filter(Note.id == note_id).first()

def get_notes(db: Session, skip: int = 0, limit: int = 100, user_id: int = None):
    query = db.query(Note)
    if user_id:
        query = query.filter(Note.user_id == user_id)
    return query.offset(skip).limit(limit).all()

def create_note(db: Session, note: NoteCreate, user_id: int):
    # Преобразуем теги в строку для совместимости с SQLite
    tags_str = ','.join(note.tags) if note.tags else ''
    db_note = Note(
        title=note.title,
        content=note.content,
        user_id=user_id,
        category_id=getattr(note, 'category_id', None),  # Используем category_id, если доступен
        is_public=note.is_public,
        category_name=note.category,  # Сохраняем как строку
        tags=tags_str
    )
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

def update_note(db: Session, note_id: int, note: NoteUpdate):
    db_note = db.query(Note).filter(Note.id == note_id).first()
    if not db_note:
        return None
        
    # Обновляем поля, исключая те, которые не должны быть обновлены
    for field, value in note.dict(exclude_unset=True).items():
        if hasattr(db_note, field):
            setattr(db_note, field, value)
    
    db.commit()
    db.refresh(db_note)
    return db_note

def delete_note(db: Session, note_id: int):
    db_note = db.query(Note).filter(Note.id == note_id).first()
    db.delete(db_note)
    db.commit()
    return db_note