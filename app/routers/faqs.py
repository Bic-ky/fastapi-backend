from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.dependencies import get_db_session, get_current_user
from app.models.faq import FAQ
from app.models.user import User
from app.schemas.faq import FAQCreate, FAQResponse, FAQUpdate

router = APIRouter(prefix="/faqs", tags=["faqs"])

# Get all FAQs
@router.get("/", response_model=List[FAQResponse])
def get_all_faqs(db: Session = Depends(get_db_session)):
    faqs = db.query(FAQ).all()
    return faqs

# Get a specific FAQ by ID
@router.get("/{faq_id}", response_model=FAQResponse)
def get_faq(faq_id: int, db: Session = Depends(get_db_session)):
    faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
    if not faq:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="FAQ not found")
    return faq


# Create a new FAQ
@router.post("/", response_model=FAQResponse, status_code=status.HTTP_201_CREATED)
def create_faq(
    faq: FAQCreate,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    try:
        new_faq = FAQ(question=faq.question, answer=faq.answer)
        db.add(new_faq)
        db.commit()
        db.refresh(new_faq)
        return new_faq
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))



# Update an existing FAQ
@router.put("/{faq_id}", response_model=FAQResponse)
def update_faq(
    faq_id: int,
    faq_update: FAQUpdate,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    db_faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
    if not db_faq:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="FAQ not found")
    
    try:
        if faq_update.question is not None:
            db_faq.question = faq_update.question
        if faq_update.answer is not None:
            db_faq.answer = faq_update.answer
            
        db.commit()
        db.refresh(db_faq)
        return db_faq
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))



# Delete an FAQ
@router.delete("/{faq_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_faq(
    faq_id: int,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    db_faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
    if not db_faq:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="FAQ not found")
    
    try:
        db.delete(db_faq)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not delete FAQ")
    return None # Return None for 204 No Content