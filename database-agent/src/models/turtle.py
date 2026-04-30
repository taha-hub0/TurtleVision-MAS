from datetime import datetime
import json


class TurtleModel:
    """Kaplumbağa Veri Modeli"""

    def __init__(self, id: str, image_base64: str, analysis_result: str,
                 metadata: str = None, species: str = None, location: str = None,
                 registered_at: datetime = None):
        self.id = id
        self.image_base64 = image_base64
        self.analysis_result = analysis_result
        self.metadata = metadata or '{}'
        self.species = species
        self.location = location
        self.registered_at = registered_at or datetime.now()
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def save(self, db) -> bool:
        """Kaplumbağayı veritabanına kaydet"""
        try:
            query = """
            INSERT INTO turtles
            (id, image_base64, analysis_result, metadata, species, location, registered_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """

            params = [
                self.id,
                self.image_base64,
                self.analysis_result,
                self.metadata,
                self.species,
                self.location,
                self.registered_at
            ]

            db.execute(query, params)
            return True

        except Exception as e:
            print(f"Error saving turtle: {e}")
            return False

    def update(self, db) -> bool:
        """Kaplumbağa bilgisini güncelle"""
        try:
            query = """
            UPDATE turtles 
            SET metadata=%s, species=%s, location=%s, updated_at=NOW()
            WHERE id=%s
            """
            
            params = [self.metadata, self.species, self.location, self.id]

            db.execute(query, params)
            return True

        except Exception as e:
            print(f"Error updating turtle: {e}")
            return False

    def to_dict(self) -> dict:
        """Modeli dictionary'e dönüştür"""
        return {
            'id': self.id,
            'species': self.species,
            'location': self.location,
            'registered_at': self.registered_at.isoformat() if isinstance(self.registered_at, datetime) else self.registered_at,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'updated_at': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
            'metadata': json.loads(self.metadata) if isinstance(self.metadata, str) else self.metadata
        }

    @staticmethod
    def get_by_id(db, turtle_id: str):
        """ID ile kaplumbağa getir"""
        try:
            query = "SELECT * FROM turtles WHERE id = %s"
            result = db.execute(query, [turtle_id])

            if result:
                return TurtleModel(
                    id=result['id'],
                    image_base64=result['image_base64'],
                    analysis_result=result['analysis_result'],
                    metadata=result['metadata'],
                    species=result['species'],
                    location=result['location'],
                    registered_at=result['registered_at']
                )
            return None

        except Exception as e:
            print(f"Error fetching turtle: {e}")
            return None

    @staticmethod
    def from_row(row: dict):
        """Veritabanı satırından model oluştur"""
        return TurtleModel(
            id=row.get('id'),
            image_base64=row.get('image_base64', ''),
            analysis_result=row.get('analysis_result', ''),
            metadata=row.get('metadata', '{}'),
            species=row.get('species'),
            location=row.get('location'),
            registered_at=row.get('registered_at')
        )
