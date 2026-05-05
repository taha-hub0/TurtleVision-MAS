"""
Kaplumbağa Eşleştirme Mantığı (Turtle Matching Logic)
=====================================================

Biyometrik benzerlik hesaplama ve %60 eşik değeri ile
"Kayıtlı Birey" vs "Yeni Birey" sınıflandırması.

Yöntemler:
1. Cosine Similarity: Vektörler arasındaki açısal benzerlik
2. Euclidean Distance: 128-boyutlu uzayda doğrudan mesafe

Non-Invasive Metodoloji:
------------------------
Bu fotoğrafik biyometrik yaklaşım:
✓ Kaplumbağaya fiziksel hasar vermiyor (metal plaka vs)
✓ Tekrar yakalamaya gerek kalmıyor
✓ Uzun vadeli izleme mümkün (plakanın düşme riski yok)
✓ Etik ve yasal açıdan daha uygun
✓ Daha düşük maliyetli

Eşik Değeri (%60):
------------------
Proje yönetmeliğine göre belirlenen hassasiyet seviyesi:
- %60+ → Aynı birey (Existing Individual)
- %60- → Yeni birey (New Individual)
"""

import numpy as np
from typing import Dict, Tuple, List, Any
from dataclasses import dataclass
import sys
import os
import json
import logging
from pathlib import Path

# Parent dizinden data modülünü import etme (src/)
sys.path.insert(0, str(Path(__file__).parent.parent))
from data.seaturtle_mock_db import get_mock_database

logger = logging.getLogger(__name__)

# Eşik değer (%)
SIMILARITY_THRESHOLD = 0.60  # %60 - proje kriteri


@dataclass
class MatchResult:
    """Eşleştirme sonucu."""
    matched: bool  # Eşleşme bulundu mu?
    classification: str  # 'EXISTING_RECORD' veya 'NEW_INDIVIDUAL'
    confidence: float  # 0-1 arasında güven skoru
    matched_turtle_id: str = None  # Eşleşen kaplumbağa ID'si (varsa)
    similarity_score: float = 0.0
    matching_method: str = 'cosine'  # Kullanılan yöntem
    reasoning: str = ''  # İnsan tarafından okunabilir açıklama


def calculate_cosine_similarity(vector1: np.ndarray, vector2: np.ndarray) -> float:
    """
    Cosine Similarity Hesapla.
    """
    norm1 = np.linalg.norm(vector1)
class SimilarityStrategy:
    """SOLID - Strategy Pattern: Benzerlik hesaplama algoritmaları."""
    @staticmethod
    def calculate(v1, v2, method='cosine'):
        v1, v2 = np.array(v1), np.array(v2)
        if method == 'cosine':
            dot_product = np.dot(v1, v2)
            norm_a = np.linalg.norm(v1)
            norm_b = np.linalg.norm(v2)
            if norm_a == 0 or norm_b == 0: return 0.0
            
            # -1 ile 1 arası sonucu 0 ile 1 arasına (%0 - %100) çekiyoruz
            cosine_sim = dot_product / (norm_a * norm_b)
            mapped_sim = (cosine_sim + 1.0) / 2.0
            return float(np.clip(mapped_sim, 0.0, 1.0))
        else: # Euclidean
            dist = np.linalg.norm(v1 - v2)
            return float(1 / (1 + dist))


class KaggleDBWrapper:
    """JSON tabanlı gerçek Kaggle veritabanını mock_db ile aynı arayüzde sarmalar."""
    def __init__(self, json_data: dict):
        self.database = json_data
        
    def get_all_turtles(self) -> List[Dict[str, Any]]:
        return list(self.database.values())
        
    def get_turtle_by_id(self, turtle_id: str) -> Dict[str, Any]:
        return self.database.get(turtle_id)

    def add_turtle(self, turtle_id: str, data: dict):
        self.database[turtle_id] = data
        # JSON'a da kaydet
        kaggle_db_path = os.path.join(Path(__file__).parent.parent.parent, "data", "kaggle_seaturtle", "kaggle_db.json")
        try:
            with open(kaggle_db_path, "w", encoding="utf-8") as f:
                json.dump(self.database, f, indent=4)
        except Exception as e:
            logger.error(f"Error saving to db: {e}")

    def delete_turtle(self, turtle_id: str):
        if turtle_id in self.database:
            del self.database[turtle_id]
            # JSON'a da kaydet
            kaggle_db_path = os.path.join(Path(__file__).parent.parent.parent, "data", "kaggle_seaturtle", "kaggle_db.json")
            try:
                with open(kaggle_db_path, "w", encoding="utf-8") as f:
                    json.dump(self.database, f, indent=4)
            except Exception as e:
                logger.error(f"Error saving to db: {e}")


class TurtleMatcher:
    """
    Ana Eşleştirme Ajanı (Matching Agent).
    SOLID - Single Responsibility: Sadece biyometrik karşılaştırma ve karar verme süreçlerini yönetir.
    """
    
    def __init__(self, threshold: float = SIMILARITY_THRESHOLD, strategy: str = 'cosine'):
        self.threshold = threshold
        self.strategy = strategy
        self.engine = SimilarityStrategy()
        
        # Eğer Kaggle veritabanı (json) mevcutsa onu kullan, yoksa mock_db'ye düş
        kaggle_db_path = os.path.join(Path(__file__).parent.parent.parent, "data", "kaggle_seaturtle", "kaggle_db.json")
        try:
            if os.path.exists(kaggle_db_path):
                with open(kaggle_db_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.db = KaggleDBWrapper(data)
                # 2. YEREL MOD (Sadece İçe Aktarılan Verilerle Çalışır)
                logger.info(f"Offline Mode: Loaded {len(data)} records from local database.")
            else:
                self.db = get_mock_database()
                logger.info("Kaggle database not found. Falling back to MOCK database.")
        except Exception as e:
            logger.error(f"Error initializing Matcher: {e}")
            self.db = get_mock_database()

    
    def match(self, incoming_biometric_vector: List[float]) -> MatchResult:
        """
        Gelen biyometrik vektörü veritabanında ara.
        
        İş akışı:
        1. Gelen vektörü tüm kayıtlarla karşılaştır
        2. En yüksek benzerliği bul
        3. Eşik değerle karşılaştır
        4. Sınıflandır ve sonuç döndür
        
        Args:
            incoming_biometric_vector: Yeni fotoğraftan çıkarılan 128-boyutlu vektör
        
        Returns:
            MatchResult: Eşleştirme sonucu
        """
        incoming_vector = np.array(incoming_biometric_vector)
        all_turtles = self.db.get_all_turtles()
        
        if not all_turtles:
            # Veritabanı boşsa yeni birey
            return MatchResult(
                matched=False,
                classification='NEW_INDIVIDUAL',
                confidence=0.0,
                reasoning='Veritabanı boş, bu bir yeni birey.'
            )
        
        # Tüm kayıtlarla benzerlik hesapla
        similarities = []
        for turtle in all_turtles:
            db_vector = np.array(turtle['biometric_vector'])
            
            # Benzerlik hesapla (Strategy Pattern)
            sim = self.engine.calculate(incoming_vector, db_vector, self.strategy)
            
            similarities.append({
                'turtle_id': turtle['turtle_id'],
                'species': turtle['species'],
                'similarity': sim,
                'first_recorded': turtle['first_recorded'],
            })
        
        # En yüksek benzerliği bul
        best_match = max(similarities, key=lambda x: x['similarity'])
        
        # Eşik kontrolü
        if best_match['similarity'] >= self.threshold:
            # %60+ → Kayıtlı birey
            result = MatchResult(
                matched=True,
                classification='EXISTING_RECORD',
                confidence=best_match['similarity'],
                matched_turtle_id=best_match['turtle_id'],
                similarity_score=best_match['similarity'],
                matching_method=self.strategy,
                reasoning=(
                    f"Benzerlik {best_match['similarity']*100:.1f}% (eşik: %{self.threshold*100}). "
                    f"{best_match['turtle_id']} ({best_match['species']}) ile eşleşti. "
                    f"İlk kayıt: {best_match['first_recorded']}"
                )
            )
        else:
            # %60- → Yeni birey
            result = MatchResult(
                matched=False,
                classification='NEW_INDIVIDUAL',
                confidence=best_match['similarity'],
                matched_turtle_id=None,
                similarity_score=best_match['similarity'],
                matching_method=self.strategy,
                reasoning=(
                    f"Benzerlik {best_match['similarity']*100:.1f}% (eşik: %{self.threshold*100} altında). "
                    f"En yakın kayıt: {best_match['turtle_id']} ({best_match['similarity']*100:.1f}%). "
                    f"Bu yeni bir birey olarak kaydedilecek."
                )
            )
        
        return result
    
    def match_with_top_n(self, incoming_biometric_vector: List[float], top_n: int = 5) -> Dict[str, Any]:
        """
        En benzer N kayıtla birlikte eşleştirme sonucu döndür.
        
        İnsan müdahalesi gereken durumlar için bu faydalıdır.
        
        Args:
            incoming_biometric_vector: Gelen vektör
            top_n: Döndürülecek en benzer kayıt sayısı
        
        Returns:
            Ana sonuç + top N alternatif
        """
        main_result = self.match(incoming_biometric_vector)
        
        incoming_vector = np.array(incoming_biometric_vector)
        all_turtles = self.db.get_all_turtles()
        
        similarities = []
        for turtle in all_turtles:
            db_vector = np.array(turtle['biometric_vector'])
            if self.method == 'cosine':
                sim = calculate_cosine_similarity(incoming_vector, db_vector)
            else:
                sim = calculate_euclidean_distance(incoming_vector, db_vector)
            
            similarities.append({
                'turtle_id': turtle['turtle_id'],
                'species': turtle['species'],
                'similarity': sim,
            })
        
        # En benzer top_n'i al
        top_matches = sorted(similarities, key=lambda x: x['similarity'], reverse=True)[:top_n]
        
        return {
            'main_result': main_result,
            'top_alternatives': top_matches,
        }


# Demo: Kullanım örneği
if __name__ == '__main__':
    print("=" * 70)
    print("TURTLE MATCHER - Demo")
    print("=" * 70)
    
    matcher = TurtleMatcher(threshold=0.60, method='cosine')
    
    # Mock vektör 1: Veritabanındaki turtle_001'e benzer
    db = get_mock_database()
    test_turtle = db.get_turtle_by_id('turtle_001')
    if test_turtle:
        # Hafif gürültü ekle
        incoming_vector = (np.array(test_turtle['biometric_vector']) + 
                          np.random.normal(0, 0.05, 128)).tolist()
        
        result = matcher.match(incoming_vector)
        print(f"\nTest 1: turtle_001'e benzer vektör")
        print(f"  Sınıflandırma: {result.classification}")
        print(f"  Güven: {result.confidence*100:.1f}%")
        print(f"  Sebep: {result.reasoning}")
        
        # Tam farklı vektör
        random_vector = np.random.random(128).tolist()
        result2 = matcher.match(random_vector)
        print(f"\nTest 2: Tamamen rastgele vektör")
        print(f"  Sınıflandırma: {result2.classification}")
        print(f"  Güven: {result2.confidence*100:.1f}%")
        print(f"  Sebep: {result2.reasoning}")
