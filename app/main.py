from fastapi import FastAPI
from app.core.config import get_settings
from app.models.base import Base, engine

# Import all your models to ensure they are registered with the Base
from app.models import user, blog, faq
from app.routers import faqs, users , blogs

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
)

# This creates all the tables in the database based on the models defined
Base.metadata.create_all(bind=engine)

app.include_router(users.router)
app.include_router(blogs.router)
app.include_router(faqs.router) 