import mysql.connector
from mysql.connector import Error

def setup_database():
    """Veritabanı ve tabloları oluştur"""

    # İlk olarak veritabanı olmadan bağlan
    try:
        connection = mysql.connector.connect(
            host='localhost',
            port=3306,
            user='root',
            password='1234'
        )
        cursor = connection.cursor()

        print("✓ MySQL'e bağlandı")

        # Veritabanı oluştur
        cursor.execute("CREATE DATABASE IF NOT EXISTS turtle_id_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print("✓ Veritabanı oluşturuldu")

        # Veritabanını seç
        cursor.execute("USE turtle_id_db")

        # Turtles tablosu
        cursor.execute("""
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
            INDEX idx_location (location)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        print("✓ turtles tablosu oluşturuldu")

        # Sightings tablosu
        cursor.execute("""
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
        print("✓ sightings tablosu oluşturuldu")

        # Turtle features tablosu
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS turtle_features (
            id VARCHAR(36) PRIMARY KEY,
            turtle_id VARCHAR(36) NOT NULL,
            feature_vector LONGBLOB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (turtle_id) REFERENCES turtles(id),
            INDEX idx_turtle_id (turtle_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        print("✓ turtle_features tablosu oluşturuldu")

        connection.commit()
        print("\n✅ Veritabanı başarıyla kuruldu!")
        print("📊 Tablolar: turtles, sightings, turtle_features")

        cursor.close()
        connection.close()

    except Error as e:
        print(f"❌ Hata: {e}")
        return False

    return True

if __name__ == '__main__':
    setup_database()
