"""
SeaTurtleID2022 Mock Veritabanı
================================

Bu modül, Kaggle'daki SeaTurtleID2022 veri setini simüle eder.
Gerçek veri seti yerine, kaplumbağaların benzersiz yüz pulu (facial scutes) 
dizilimlerini biyometrik imza (feature vector) olarak temsil eden yapay veriler içerir.

Akademik Amaç (Non-Invasive Methodology):
-------------------------------------------
Metal plaka takma (invazif) yerine fotoğrafik biyometri kullanarak:
- Hayvanın fiziksel bütünlüğünü koruyoruz
- Plaka kayması/kaybı riskini ortadan kaldırıyoruz
- Uzun vadeli popülasyon izlemesi sağlıyoruz
- Etik hassasiyetleri karşılıyoruz

Veri Yapısı:
- turtle_id: Benzersiz kimlik
- species: Tür (Green, Loggerhead, Leatherback, Hawksbill)
- biometric_vector: Post-ocular scutes'den çıkarılan 128-boyutlu öznitelik vektörü
- location: İlk kayıt konumu
- first_recorded: İlk kaydedilme tarihi
- sightings: Avistama sayısı
"""

import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Seed for reproducibility
np.random.seed(42)


class SeaTurtleMockDB:
    """
    SeaTurtleID2022 veri setinin mock temsili.
    
    Her kaplumbağa için:
    - Benzersiz biyometrik vektör (post-ocular scutes pattern)
    - Tür ve konum bilgisi
    - Avistama geçmişi
    """
    
    SPECIES = ['GREEN_TURTLE', 'LOGGERHEAD', 'LEATHERBACK', 'HAWKSBILL']
    LOCATIONS = [
        'Dalyan Beach', 'Iztuzu Beach', 'Patara Beach', 
        'Ekincik Lagoon', 'Oludeniz', 'Mediterranean Coast'
    ]
    
    def __init__(self):
        """Mock veritabanını başlat ve sahte kaplumbağa kayıtları oluştur."""
        self.database = self._initialize_mock_database()
    
    def _initialize_mock_database(self) -> Dict[str, Dict[str, Any]]:
        """
        SeaTurtleID2022 veri setinden ilham alarak 20 sahte kaplumbağa kaydı oluştur.
        
        Gerçek veri setinde ~5000 fotoğraf ve ~1600 kaplumbağa olmasına rağmen,
        demo için 20 kayıt kullanıyoruz.
        """
        db = {}
        base_date = datetime.now() - timedelta(days=365)
        
        for i in range(1, 21):
            turtle_id = f'turtle_{i:03d}'
            species = self.SPECIES[i % len(self.SPECIES)]
            location = self.LOCATIONS[i % len(self.LOCATIONS)]
            
            # Post-ocular scutes pattern'den çıkarılan 128-boyutlu biyometrik vektör
            # Gerçekte, OpenCV/TensorFlow'dan çıkarılan CNN features'dır
            biometric_vector = self._generate_realistic_biometric_vector(species)
            
            db[turtle_id] = {
                'turtle_id': turtle_id,
                'species': species,
                'biometric_vector': biometric_vector,
                'location': location,
                'first_recorded': (base_date + timedelta(days=i*10)).isoformat(),
                'sightings': np.random.randint(1, 8),
                'quality_score': np.random.uniform(0.75, 0.98),
            }
        
        return db
    
    def _generate_realistic_biometric_vector(self, species: str) -> List[float]:
        """
        Tür-spesifik biyometrik vektör oluştur.
        
        Gerçekte: OpenCV SIFT/ORB + CNN features
        Mock'ta: Türe göre temel desen + rastgele varyasyon
        
        Args:
            species: Kaplumbağa türü
        
        Returns:
            128-boyutlu biyometrik öznitelik vektörü
        """
        base_pattern = {
            'GREEN_TURTLE': np.array([0.45, 0.23, 0.89, 0.12, 0.56, 0.78] + [0.5] * 122),
            'LOGGERHEAD': np.array([0.52, 0.31, 0.72, 0.18, 0.64, 0.85] + [0.5] * 122),
            'LEATHERBACK': np.array([0.61, 0.28, 0.79, 0.22, 0.71, 0.92] + [0.5] * 122),
            'HAWKSBILL': np.array([0.48, 0.35, 0.82, 0.15, 0.59, 0.80] + [0.5] * 122),
        }
        
        pattern = base_pattern.get(species, base_pattern['GREEN_TURTLE'])
        # Yaklaşık ±0.1 varyasyon ekle (biyolojik ve fotoğrafik varyasyon)
        noise = np.random.normal(0, 0.08, 128)
        vector = np.clip(pattern + noise, 0, 1)
        
        return vector.tolist()
    
    def get_all_turtles(self) -> List[Dict[str, Any]]:
        """Tüm kaplumbağa kayıtlarını döndür."""
        return list(self.database.values())
    
    def get_turtle_by_id(self, turtle_id: str) -> Dict[str, Any]:
        """ID'ye göre kaplumbağa kaydını döndür."""
        return self.database.get(turtle_id)
    
    def get_turtles_by_species(self, species: str) -> List[Dict[str, Any]]:
        """Türe göre kaplumbağaları filtrele."""
        return [t for t in self.database.values() if t['species'] == species]
    
    def add_sighting(self, turtle_id: str):
        """Bir kaplumbağanın avistama sayısını artır."""
        if turtle_id in self.database:
            self.database[turtle_id]['sightings'] += 1
    
    def __len__(self) -> int:
        """Veritabanındaki kaplumbağa sayısı."""
        return len(self.database)


# Global mock veritabanı (Django ORM benzeri singleton pattern)
_mock_db_instance = None

def get_mock_database() -> SeaTurtleMockDB:
    """Global mock veritabanı instance'ını al (singleton)."""
    global _mock_db_instance
    if _mock_db_instance is None:
        _mock_db_instance = SeaTurtleMockDB()
    return _mock_db_instance
