from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# from sqlalchemy.ext.declarative import declarative_base # No longer needed here

# Import Base from our models package
from .models import Base # Assuming database.py is in the 'app' directory alongside 'models'

SQLALCHEMY_DATABASE_URL = "sqlite:///../life_system_backend.db" # Path relative to app directory
# For local development with SQLite, connect_args is needed for FastAPI
# For other databases like PostgreSQL, you wouldn't need connect_args
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is now imported from .models

# Dependency to get a DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 