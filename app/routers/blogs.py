import os
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException , status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List

from app.core.dependencies import get_db_session, get_current_user
from app.models.blog import Blog
from app.models.user import User
from app.schemas.blog import BlogCreate, BlogResponse, BlogUpdate
import shutil

router = APIRouter(prefix="/blogs", tags=["blogs"])

### CRUD Operations ###

@router.post("/", response_model=BlogResponse)
def create_blog(
    title: str = Form(...),
    content: str = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db_session),
    current_user = Depends(get_current_user),
):
    try:
        os.makedirs("static/images", exist_ok=True)

        # Save file
        file_location = f"static/images/{image.filename}"
        with open(file_location, "wb") as f:
            shutil.copyfileobj(image.file, f)

        # Build a public URL (see #3 below to mount /static)
        base_url = "http://127.0.0.1:8000"
        image_url = f"{base_url}/{file_location}" 

        # Uniqueness check
        existing_blog = db.query(Blog).filter(Blog.title == title).first()
        if existing_blog:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"A blog with the title '{title}' already exists."
            )

        blog = Blog(title=title, content=content, image=image_url, owner=current_user)
        db.add(blog)
        db.commit()
        db.refresh(blog)
        return blog

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A blog with the title '{title}' already exists."
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating blog: {str(e)}"
        )

# Get all blogs (GET /blogs/)
@router.get("/", response_model=List[BlogResponse])
def get_all_blogs(db: Session = Depends(get_db_session)):
    blogs = db.query(Blog).all()
    blog_list = []
    for blog in blogs:
        author = None
        if hasattr(blog, 'owner') and blog.owner:
            author = blog.owner.username
        else:
            # Fallback: fetch user from User model if relationship not set up
            user = db.query(User).filter(User.id == blog.owner_id).first()
            author = user.username if user else None
        blog_dict = blog.__dict__.copy()
        blog_dict['author'] = author
        blog_list.append(blog_dict)
    return blog_list

# app/routers/blogs.py (or wherever your router is)
@router.get("/blog-id/{blog_id}", response_model=BlogResponse)
def get_blog(
    blog_id: int,
    db: Session = Depends(get_db_session)
):
    blog = db.query(Blog).filter(Blog.id == blog_id).first()
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found")

    author = blog.owner.username if blog.owner else None
    blog_dict = blog.__dict__.copy()
    blog_dict["author"] = author
    return blog_dict


# Update a blog post (PUT /blogs/{blog_id})
@router.put("/update/{blog_id}", response_model=BlogResponse)
def update_blog(
    blog_id: int,
    blog_update: BlogUpdate,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    db_blog = db.query(Blog).filter(Blog.id == blog_id).first()
    if not db_blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found")

    if db_blog.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this blog")

    try:
        if blog_update.title is not None:
            db_blog.title = blog_update.title
        if blog_update.content is not None:
            db_blog.content = blog_update.content

        db.commit()
        db.refresh(db_blog)
        return db_blog
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# Delete a blog post (DELETE /blogs/{blog_id})
@router.delete("/delete/{blog_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_blog(
    blog_id: int,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    db_blog = db.query(Blog).filter(Blog.id == blog_id).first()
    if not db_blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found")

    if db_blog.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this blog")

    try:
        db.delete(db_blog)
        db.commit()
        return {"detail": "Blog deleted successfully"}
    except Exception:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not delete blog")