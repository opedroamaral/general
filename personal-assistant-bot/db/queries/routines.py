from datetime import date
from sqlalchemy.orm import Session
from db.models import Routine


def get_routines(db: Session, business_id=None, active=None):
    q = db.query(Routine)
    if business_id is not None:
        q = q.filter(Routine.business_id == business_id)
    if active is not None:
        q = q.filter(Routine.active == active)
    return q.order_by(Routine.title).all()


def get_routine(db: Session, routine_id: int):
    return db.query(Routine).filter(Routine.id == routine_id).first()


def create_routine(db: Session, title: str, frequency: str, business_id=None,
                   weekdays=None, remind_time=None):
    routine = Routine(
        title=title,
        frequency=frequency,
        business_id=business_id,
        weekdays=weekdays,
        remind_time=remind_time,
    )
    db.add(routine)
    db.commit()
    db.refresh(routine)
    return routine


def update_routine(db: Session, routine_id: int, **kwargs):
    routine = get_routine(db, routine_id)
    if not routine:
        return None
    for key, value in kwargs.items():
        if hasattr(routine, key):
            setattr(routine, key, value)
    db.commit()
    db.refresh(routine)
    return routine


def mark_routine_done(db: Session, routine_id: int):
    return update_routine(db, routine_id, last_done=date.today())


def delete_routine(db: Session, routine_id: int):
    routine = get_routine(db, routine_id)
    if routine:
        db.delete(routine)
        db.commit()
    return routine


def get_routines_for_today(db: Session):
    today_weekday = str(date.today().isoweekday())  # 1=Monday
    routines = db.query(Routine).filter(Routine.active == True).all()
    result = []
    for r in routines:
        if r.frequency == "daily":
            result.append(r)
        elif r.frequency == "weekly" and r.weekdays:
            if today_weekday in r.weekdays.split(","):
                result.append(r)
        elif r.frequency == "monthly":
            if date.today().day == 1:
                result.append(r)
    return result
