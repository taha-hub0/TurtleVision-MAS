import mysql.connector
from mysql.connector import Error
import logging
from config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME, DB_POOL_SIZE

logger = logging.getLogger(__name__)


class Database:
    """MySQL Veritabanı Bağlantısı Yöneticisi"""

    def __init__(self):
        self.connection = None
        self.cursor = None

    def connect(self):
        """Veritabanına bağlan"""
        try:
            self.connection = mysql.connector.connect(
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME,
                autocommit=True
            )
            
            if self.connection.is_connected():
                logger.info(f"Connected to MySQL database: {DB_NAME}")
                self.cursor = self.connection.cursor(dictionary=True)
            else:
                raise Error("Failed to connect to MySQL")
                
        except Error as e:
            logger.error(f"Error while connecting to MySQL: {e}")
            raise

    def disconnect(self):
        """Veritabanı bağlantısını kapat"""
        if self.connection and self.connection.is_connected():
            if self.cursor:
                self.cursor.close()
            self.connection.close()
            logger.info("MySQL connection closed")

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

        except Error as e:
            logger.error(f"Error executing query: {e}")
            raise

    def create_tables(self):
        """Veritabanı tablolarını oluştur"""
        try:
            # Turtles table
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS turtles (
                id VARCHAR(36) PRIMARY KEY,
                image_base64 LONGTEXT NOT NULL,
                analysis_result JSON,
                metadata JSON,
                species VARCHAR(100),
                location VARCHAR(200),
                registered_at DATETIME,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_species (species),
                INDEX idx_location (location),
                FULLTEXT INDEX ft_metadata (metadata)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)

            # Turtle sightings table
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS sightings (
                id VARCHAR(36) PRIMARY KEY,
                turtle_id VARCHAR(36) NOT NULL,
                location VARCHAR(200),
                date_sighted DATETIME,
                observer_name VARCHAR(100),
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (turtle_id) REFERENCES turtles(id),
                INDEX idx_turtle_id (turtle_id),
                INDEX idx_date (date_sighted)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)

            # Turtle features table (for similarity search)
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS turtle_features (
                id VARCHAR(36) PRIMARY KEY,
                turtle_id VARCHAR(36) NOT NULL,
                feature_vector LONGBLOB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (turtle_id) REFERENCES turtles(id),
                INDEX idx_turtle_id (turtle_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)

            self.connection.commit()
            logger.info("Database tables created successfully")

        except Error as e:
            logger.error(f"Error creating tables: {e}")
            raise

    def close(self):
        """Bağlantıyı kapat"""
        self.disconnect()
