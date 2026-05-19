from datetime import date, datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_
from db.models import Task


def get_tasks(db: Session, business_id=None, status=None, due_date=None):
    q = db.query(Task)
    if business_id is not None:
        q = q.filter(Task.business_id == business_id)
    if status:
        q = q.filter(Task.status == status)
    if due_date:
        q = q.filter(Task.due_date == due_date)
    return q.order_by(Task.due_date.asc().nullslast(), Task.created_at.desc()).all()


def get_task(db: Session, task_id: int):
    return db.query(Task).filter(Task.id == task_id).first()


def create_task(db: Session, title: str, business_id=None, description=None,
                due_date=None, due_time=None, priority="normal"):
    task = Task(
        title=title,
        business_id=business_id,
        description=description,
        due_date=due_date,
        due_time=due_time,
        priority=priority,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def update_task(db: Session, task_id: int, **kwargs):
    task = get_task(db, task_id)
    if not task:
        return None
    for key, value in kwargs.items():
        if hasattr(task, key):
            setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return task


def mark_task_done(db: Session, task_id: int):
    return update_task(db, task_id, status="done", done_at=datetime.utcnow())


def delete_task(db: Session, task_id: int):
    task = get_task(db, task_id)
    if task:
        db.delete(task)
        db.commit()
    return task


def get_tasks_due_today(db: Session):
    return db.query(Task).filter(
        and_(Task.due_date == date.today(), Task.status == "pending")
    ).all()


def get_overdue_tasks(db: Session):
    return db.query(Task).filter(
        and_(Task.due_date < date.today(), Task.status == "pending")
    ).all()


def get_tasks_due_week(db: Session):
    from datetime import timedelta
    today = date.today()
    week_end = today + timedelta(days=7)
    return db.query(Task).filter(
        and_(Task.due_date >= today, Task.due_date <= week_end, Task.status == "pending")
    ).all()
