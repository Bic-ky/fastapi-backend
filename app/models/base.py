from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
from app.core.config import get_settings

settings = get_settings()
Base = declarative_base()
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
