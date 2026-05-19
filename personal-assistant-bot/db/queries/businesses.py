from sqlalchemy.orm import Session
from db.models import Business


def get_businesses(db: Session, active=None):
    q = db.query(Business)
    if active is not None:
        q = q.filter(Business.active == active)
    return q.order_by(Business.name).all()


def get_business(db: Session, business_id: int):
    return db.query(Business).filter(Business.id == business_id).first()


def get_business_by_name(db: Session, name: str):
    return db.query(Business).filter(
        Business.name.ilike(f"%{name}%")
    ).first()


def create_business(db: Session, name: str, emoji=None, description=None):
    biz = Business(name=name, emoji=emoji, description=description)
    db.add(biz)
    db.commit()
    db.refresh(biz)
    return biz


def update_business(db: Session, business_id: int, **kwargs):
    biz = get_business(db, business_id)
    if not biz:
        return None
    for key, value in kwargs.items():
        if hasattr(biz, key):
            setattr(biz, key, value)
    db.commit()
    db.refresh(biz)
    return biz


def delete_business(db: Session, business_id: int):
    biz = get_business(db, business_id)
    if biz:
        db.delete(biz)
        db.commit()
    return biz
