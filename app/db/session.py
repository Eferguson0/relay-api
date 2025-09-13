import logging

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # Create database engine
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,  # Enable connection health checks
        pool_size=20,  # Increased pool size for better concurrency
        max_overflow=30,  # Increased max overflow
        pool_timeout=30,  # Add timeout setting
        pool_recycle=1800,  # Recycle connections every 30 minutes
    )

    # Create session factory
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create base class for models
    Base = declarative_base()

    # Test database connection - only when explicitly called
    def test_connection():
        try:
            with engine.connect():
                logger.info("Successfully connected to the database")
                return True
        except Exception as e:
            logger.error(f"Failed to connect to the database: {str(e)}")
            return False

except Exception as e:
    logger.error(f"Failed to create database engine: {str(e)}")
    raise


def get_db():
    """
    Database session dependency.
    Yields a database session and ensures it's closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
