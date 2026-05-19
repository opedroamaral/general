from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.auth import verify_token
from db.session import get_db
from db.queries import tasks as q

router = APIRouter(prefix="/tasks", tags=["tasks"], dependencies=[Depends(verify_token)])


class TaskCreate(BaseModel):
    title: str
    business_id: Optional[int] = None
    description: Optional[str] = None
    due_date: Optional[date] = None
    due_time: Optional[str] = None
    priority: str = "normal"


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    business_id: Optional[int] = None
    description: Optional[str] = None
    due_date: Optional[date] = None
    due_time: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None


def serialize(t):
    return {
        "id": t.id,
        "title": t.title,
        "business_id": t.business_id,
        "business_name": t.business.name if t.business else None,
        "business_emoji": t.business.emoji if t.business else None,
        "description": t.description,
        "due_date": t.due_date.isoformat() if t.due_date else None,
        "due_time": str(t.due_time) if t.due_time else None,
        "priority": t.priority,
        "status": t.status,
        "created_at": t.created_at.isoformat() if t.created_at else None,
        "done_at": t.done_at.isoformat() if t.done_at else None,
    }


@router.get("/")
def list_tasks(business_id: Optional[int] = None, status: Optional[str] = None, db: Session = Depends(get_db)):
    return [serialize(t) for t in q.get_tasks(db, business_id=business_id, status=status)]


@router.post("/", status_code=201)
def create(body: TaskCreate, db: Session = Depends(get_db)):
    task = q.create_task(db, **body.model_dump())
    return serialize(task)


@router.put("/{task_id}")
def update(task_id: int, body: TaskUpdate, db: Session = Depends(get_db)):
    task = q.update_task(db, task_id, **{k: v for k, v in body.model_dump().items() if v is not None})
    if not task:
        from fastapi import HTTPException
        raise HTTPException(404, "Tarefa não encontrada")
    return serialize(task)


@router.patch("/{task_id}/done")
def mark_done(task_id: int, db: Session = Depends(get_db)):
    task = q.mark_task_done(db, task_id)
    if not task:
        from fastapi import HTTPException
        raise HTTPException(404, "Tarefa não encontrada")
    return serialize(task)


@router.delete("/{task_id}")
def delete(task_id: int, db: Session = Depends(get_db)):
    q.delete_task(db, task_id)
    return {"ok": True}
