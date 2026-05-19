from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.auth import verify_token
from db.session import get_db
from db.queries import routines as q

router = APIRouter(prefix="/routines", tags=["routines"], dependencies=[Depends(verify_token)])


class RoutineCreate(BaseModel):
    title: str
    frequency: str
    business_id: Optional[int] = None
    weekdays: Optional[str] = None
    remind_time: Optional[str] = None


class RoutineUpdate(BaseModel):
    title: Optional[str] = None
    frequency: Optional[str] = None
    business_id: Optional[int] = None
    weekdays: Optional[str] = None
    remind_time: Optional[str] = None
    active: Optional[bool] = None


def serialize(r):
    return {
        "id": r.id,
        "title": r.title,
        "business_id": r.business_id,
        "business_name": r.business.name if r.business else None,
        "business_emoji": r.business.emoji if r.business else None,
        "frequency": r.frequency,
        "weekdays": r.weekdays,
        "remind_time": str(r.remind_time) if r.remind_time else None,
        "active": r.active,
        "last_done": r.last_done.isoformat() if r.last_done else None,
        "created_at": r.created_at.isoformat() if r.created_at else None,
    }


@router.get("/")
def list_routines(business_id: Optional[int] = None, active: Optional[bool] = None, db: Session = Depends(get_db)):
    return [serialize(r) for r in q.get_routines(db, business_id=business_id, active=active)]


@router.post("/", status_code=201)
def create(body: RoutineCreate, db: Session = Depends(get_db)):
    return serialize(q.create_routine(db, **body.model_dump()))


@router.put("/{routine_id}")
def update(routine_id: int, body: RoutineUpdate, db: Session = Depends(get_db)):
    routine = q.update_routine(db, routine_id, **{k: v for k, v in body.model_dump().items() if v is not None})
    if not routine:
        raise HTTPException(404, "Rotina não encontrada")
    return serialize(routine)


@router.patch("/{routine_id}/done")
def mark_done(routine_id: int, db: Session = Depends(get_db)):
    routine = q.mark_routine_done(db, routine_id)
    if not routine:
        raise HTTPException(404, "Rotina não encontrada")
    return serialize(routine)


@router.delete("/{routine_id}")
def delete(routine_id: int, db: Session = Depends(get_db)):
    q.delete_routine(db, routine_id)
    return {"ok": True}
