from datetime import date, timedelta
from sqlalchemy.orm import Session
from db.models import AIMessage


def get_recent_messages(db: Session, limit=20):
    return (
        db.query(AIMessage)
        .order_by(AIMessage.created_at.desc())
        .limit(limit)
        .all()[::-1]  # chronological order
    )


def add_message(db: Session, role: str, content: str):
    msg = AIMessage(role=role, content=content)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


def clear_old_messages(db: Session, keep_days=30):
    cutoff = date.today() - timedelta(days=keep_days)
    db.query(AIMessage).filter(AIMessage.session_date < cutoff).delete()
    db.commit()
