import sqlite3
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class Database:
    """SQLite Veritabanı Bağlantısı Yöneticisi"""

    def __init__(self, db_path='./turtle_id.db'):
        self.db_path = db_path
        self.connection = None
        self.cursor = None
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    def connect(self):
        """Veritabanına bağlan"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            self.cursor = self.connection.cursor()
            logger.info(f"Connected to SQLite database: {self.db_path}")
        except Exception as e:
            logger.error(f"Error while connecting to SQLite: {e}")
            raise

    def disconnect(self):
        """Veritabanı bağlantısını kapat"""
        if self.connection:
            self.connection.close()
            logger.info("SQLite connection closed")

    def execute(self, query: str, params: list = None, fetch_all: bool = False):
        """
        SQL sorgusu çalıştır

        Args:
            query: SQL query
            params: Query parameters
            fetch_all: Tüm sonuçları getir

        Returns:
            Query results or None
        """
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)

            if fetch_all:
                return self.cursor.fetchall()
            else:
                return self.cursor.fetchone()

        except Exception as e:
            logger.error(f"Error executing query: {e}")
            raise

    def create_tables(self):
        """Veritabanı tablolarını oluştur"""
        try:
            # Turtles table
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS turtles (
                id TEXT PRIMARY KEY,
                image_base64 TEXT NOT NULL,
                analysis_result TEXT,
                metadata TEXT,
                species TEXT,
                location TEXT,
                registered_at DATETIME,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            # Turtle sightings table
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS sightings (
                id TEXT PRIMARY KEY,
                turtle_id TEXT NOT NULL,
                location TEXT,
                date_sighted DATETIME,
                observer_name TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (turtle_id) REFERENCES turtles(id)
            );
            """)

            # Turtle features table (for similarity search)
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS turtle_features (
                id TEXT PRIMARY KEY,
                turtle_id TEXT NOT NULL,
                feature_vector BLOB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (turtle_id) REFERENCES turtles(id)
            );
            """)

            # İndeks oluştur
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_species ON turtles(species);")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_location ON turtles(location);")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_turtle_id ON sightings(turtle_id);")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_date ON sightings(date_sighted);")

            self.connection.commit()
            logger.info("Database tables created successfully")

        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            raise

    def close(self):
        """Bağlantıyı kapat"""
        self.disconnect()
