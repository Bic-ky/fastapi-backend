from fastapi import FastAPI
from app.core.config import get_settings
from app.models.base import Base, engine
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.routers import dashboard, faqs, users , blogs , contacts

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# This creates all the tables in the database based on the models defined
Base.metadata.create_all(bind=engine)

app.include_router(users.router)
app.include_router(blogs.router)
app.include_router(faqs.router)
app.include_router(contacts.router)
app.include_router(dashboard.router) 
app.mount("/static", StaticFiles(directory="static"), name="static")
