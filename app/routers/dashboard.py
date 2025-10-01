# app/routers/dashboard.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.dependencies import get_db_session
from app.core.dependencies import get_current_user
from app.models.contacts import ContactMessage
from app.models.user import User
from app.models.blog import Blog

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/stats")
def get_stats(
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    total_users = db.query(User).count()
    total_blogs = db.query(Blog).count()
    total_messages = db.query(ContactMessage).count()
    new_messages = db.query(ContactMessage).filter(ContactMessage.status == "new").count()

    return {
        "stats": [
            {"title": "New Messages", "value": str(new_messages)},
            {"title": "Total Patients", "value": str(total_users)},
            {"title": "Blog Posts", "value": str(total_blogs)},
            {"title": "All Messages", "value": str(total_messages)},
        ]
    }

@router.get("/recent-messages")
def recent_messages(
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    q = db.query(ContactMessage).order_by(ContactMessage.created_at.desc()).limit(5).all()
    return {"messages": q}

@router.get("/recent-blogs")
def recent_blogs(
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    q = db.query(Blog).order_by(Blog.id.desc()).limit(5).all()
    return {"blogs": q}



