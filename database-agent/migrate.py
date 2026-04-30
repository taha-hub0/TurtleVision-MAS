from src.database import Database
import logging

logger = logging.getLogger(__name__)


def migrate():
    """Veritabanı migration'larını çalıştır"""
    try:
        db = Database()
        db.connect()
        
        logger.info("Running database migrations...")
        
        # Create tables
        db.create_tables()
        
        logger.info("Migrations completed successfully")
        db.disconnect()
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise


if __name__ == '__main__':
    migrate()
