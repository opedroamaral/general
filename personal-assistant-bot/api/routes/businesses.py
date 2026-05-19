from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.auth import verify_token
from db.session import get_db
from db.queries import businesses as q

router = APIRouter(prefix="/businesses", tags=["businesses"], dependencies=[Depends(verify_token)])


class BusinessCreate(BaseModel):
    name: str
    emoji: Optional[str] = None
    description: Optional[str] = None


class BusinessUpdate(BaseModel):
    name: Optional[str] = None
    emoji: Optional[str] = None
    description: Optional[str] = None
    active: Optional[bool] = None


def serialize(b):
    return {
        "id": b.id,
        "name": b.name,
        "emoji": b.emoji,
        "description": b.description,
        "active": b.active,
        "created_at": b.created_at.isoformat() if b.created_at else None,
    }


@router.get("/")
def list_businesses(active: Optional[bool] = None, db: Session = Depends(get_db)):
    return [serialize(b) for b in q.get_businesses(db, active=active)]


@router.post("/", status_code=201)
def create(body: BusinessCreate, db: Session = Depends(get_db)):
    return serialize(q.create_business(db, **body.model_dump()))


@router.put("/{business_id}")
def update(business_id: int, body: BusinessUpdate, db: Session = Depends(get_db)):
    biz = q.update_business(db, business_id, **{k: v for k, v in body.model_dump().items() if v is not None})
    if not biz:
        raise HTTPException(404, "Negócio não encontrado")
    return serialize(biz)


@router.delete("/{business_id}")
def delete(business_id: int, db: Session = Depends(get_db)):
    q.delete_business(db, business_id)
    return {"ok": True}
