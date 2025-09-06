import logging

from sqlalchemy.orm import Session

from app.core.rid import generate_rid
from app.db.session import Base, engine
from app.models.user import User
from app.services.auth_service import get_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db() -> None:
    """
    Initialize the database by creating all tables.
    """
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        raise


def create_first_superuser(db: Session) -> None:
    """
    Create the first superuser if no users exist.
    """
    try:
        # Check if any user exists
        user = db.query(User).first()
        if not user:
            # Create superuser with RID
            user_id = generate_rid("user")
            superuser = User(
                id=user_id,
                email="admin@example.com",
                hashed_password=get_password_hash("admin"),
                full_name="Admin User",
                is_superuser=True,
                is_active=True,
            )
            db.add(superuser)
            db.commit()
            logger.info("First superuser created successfully")
    except Exception as e:
        logger.error(f"Error creating first superuser: {str(e)}")
        raise


if __name__ == "__main__":
    logger.info("Creating initial data")
    init_db()
    # Note: create_first_superuser requires a database session
    # It should be called from your application startup code
