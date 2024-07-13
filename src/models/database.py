import logging

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, declarative_base, Session

from src.core.config import settings

logger = logging.getLogger(__name__)

try:
    engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
except SQLAlchemyError as e:
    logger.error(f"Error connecting to the database: {str(e)}")
    raise


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise
    finally:
        db.close()
