# Database session handling (e.g., SQLAlchemy)

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Create the database engine
engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})

# Create a configured SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Base class for ORM models
Base = declarative_base()

# Create all tables in the database
def init_db():
    Base.metadata.create_all(bind=engine)