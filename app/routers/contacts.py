# app/routers/contacts.py
from fastapi import APIRouter, Depends, HTTPException, Query, status, Response
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from typing import Optional

from app.core.dependencies import get_db_session
from app.schemas.contacts import ContactCreate, ContactRead, ContactList, ContactStatus
from app.models.contacts import ContactMessage , ContactStatus

router = APIRouter(prefix="/contacts", tags=["contacts"])

@router.post("/create", response_model=ContactRead, status_code=status.HTTP_201_CREATED)
def create_contact(payload: ContactCreate, db: Session = Depends(get_db_session)):
    """
    Create a new contact message.

    - Honors honeypot (`website`): if filled, return 204 No Content (silently drop spam).
    - Validates phone/email via Pydantic.
    """
    # Honeypot: bots often fill "website". If present, ignore the submission.
    if getattr(payload, "website", None) and payload.website.strip():
        # 204 No Content is the clean way to indicate "handled, nothing to return".
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    obj = ContactMessage(
        name=payload.name.strip(),
        email=payload.email,
        phone=payload.phone,
        service=(payload.service.strip() if payload.service else None),
        preferred_time=payload.preferred_time,
        message=(payload.message.strip() if payload.message else None),
        status=ContactStatus.new,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("", response_model=ContactList)
def list_contacts(
    db: Session = Depends(get_db_session),
    q: Optional[str] = Query(None, description="Search in name, email, phone, service"),
    status_filter: Optional[ContactStatus] = Query(None, alias="status"),
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    """
    Get contacts with search + pagination.
    Ordered by newest first.
    """
    stmt = select(ContactMessage)
    if q:
        like = f"%{q.strip()}%"
        stmt = stmt.where(
            (ContactMessage.name.ilike(like)) |
            (ContactMessage.email.ilike(like)) |
            (ContactMessage.phone.ilike(like)) |
            (ContactMessage.service.ilike(like))
        )
    if status_filter:
        stmt = stmt.where(ContactMessage.status == status_filter)

    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    items = db.execute(
        stmt.order_by(ContactMessage.created_at.desc())
            .offset(offset)
            .limit(limit)
    ).scalars().all()

    return {"total": total or 0, "items": items}


@router.get("/{contact_id}", response_model=ContactRead)
def get_contact(contact_id: int, db: Session = Depends(get_db_session)):
    obj = db.get(ContactMessage, contact_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return obj


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact(contact_id: int, db: Session = Depends(get_db_session)):
    obj = db.get(ContactMessage, contact_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    db.delete(obj)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
