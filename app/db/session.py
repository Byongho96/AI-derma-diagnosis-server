from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# DB connection pool
engine = create_engine(settings.DATABASE_URL)

# Create a new session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()