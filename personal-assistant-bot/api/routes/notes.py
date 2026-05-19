from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.auth import verify_token
from db.session import get_db
from db.queries import notes as q

router = APIRouter(prefix="/notes", tags=["notes"], dependencies=[Depends(verify_token)])


class NoteCreate(BaseModel):
    content: str
    business_id: Optional[int] = None
    tags: Optional[List[str]] = None


class NoteUpdate(BaseModel):
    content: Optional[str] = None
    business_id: Optional[int] = None
    tags: Optional[List[str]] = None


def serialize(n):
    return {
        "id": n.id,
        "content": n.content,
        "business_id": n.business_id,
        "business_name": n.business.name if n.business else None,
        "business_emoji": n.business.emoji if n.business else None,
        "tags": n.tags or [],
        "created_at": n.created_at.isoformat() if n.created_at else None,
    }


@router.get("/")
def list_notes(business_id: Optional[int] = None, limit: int = 50, db: Session = Depends(get_db)):
    return [serialize(n) for n in q.get_notes(db, business_id=business_id, limit=limit)]


@router.post("/", status_code=201)
def create(body: NoteCreate, db: Session = Depends(get_db)):
    return serialize(q.create_note(db, **body.model_dump()))


@router.put("/{note_id}")
def update(note_id: int, body: NoteUpdate, db: Session = Depends(get_db)):
    note = q.update_note(db, note_id, **{k: v for k, v in body.model_dump().items() if v is not None})
    if not note:
        raise HTTPException(404, "Nota não encontrada")
    return serialize(note)


@router.delete("/{note_id}")
def delete(note_id: int, db: Session = Depends(get_db)):
    q.delete_note(db, note_id)
    return {"ok": True}
