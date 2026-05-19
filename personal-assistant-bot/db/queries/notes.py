from sqlalchemy.orm import Session
from db.models import Note


def get_notes(db: Session, business_id=None, limit=10):
    q = db.query(Note)
    if business_id is not None:
        q = q.filter(Note.business_id == business_id)
    return q.order_by(Note.created_at.desc()).limit(limit).all()


def get_note(db: Session, note_id: int):
    return db.query(Note).filter(Note.id == note_id).first()


def create_note(db: Session, content: str, business_id=None, tags=None):
    note = Note(content=content, business_id=business_id, tags=tags or [])
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


def update_note(db: Session, note_id: int, **kwargs):
    note = get_note(db, note_id)
    if not note:
        return None
    for key, value in kwargs.items():
        if hasattr(note, key):
            setattr(note, key, value)
    db.commit()
    db.refresh(note)
    return note


def delete_note(db: Session, note_id: int):
    note = get_note(db, note_id)
    if note:
        db.delete(note)
        db.commit()
    return note
