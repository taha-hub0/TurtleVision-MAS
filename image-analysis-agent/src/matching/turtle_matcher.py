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

# Kimlik duzeyinde toplama (multi-shot galeri) icin max/centroid karisim
# agirligi: skor = w * en_iyi_kare + (1 - w) * centroid.
#
# Neden karisim? Iki toplayici farkli sorgularda kazaniyor:
#   - `max`      ayni cekim seansindan gelen, galerideki bir kareyle
#                neredeyse birebir ayni sorguda ustun.
#   - `centroid` gercekten yeni bir gunde cekilmis sorguda ustun; tek bir
#                kotu acili karenin sonucu belirlemesini engeller.
# SeaTurtleID2022 uzerinde olculdu (galeri = birey basina 2 kare, flip-TTA):
#   w=1.0 (saf max)      ayni gun 83.3/88.6, farkli gun 27.0/35.1  (top1/top5)
#   w=0.5 (bu deger)     ayni gun 83.3/88.6, farkli gun 27.9/38.7
#   w=0.0 (saf centroid) ayni gun 80.4/86.8, farkli gun 27.0/38.7
# w=0.5 hicbir sutunda saf max'in altinda kalmiyor; varsayilan bu.
DEFAULT_MAX_WEIGHT = 0.5


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
    # --- kimlik duzeyinde toplama (multi-shot) ---
    # matched_turtle_id geriye donuk uyumluluk icin hala bir KARE kimligi
    # ('T001_1'); asagidakiler eslesmenin ait oldugu BIREYI tarif eder.
    matched_identity: str = None   # or. 't001'
    supporting_frames: int = 0     # o bireyin galerideki kare sayisi
    aggregation: str = 'hybrid'    # kullanilan toplama yontemi


def calculate_cosine_similarity(vector1, vector2) -> float:
    """
    Kosinus benzerligi. Sonuc SimilarityStrategy ile ayni olcekte doner:
    [-1, 1] araligi [0, 1]'e haritalanir.

    NOT: Bu fonksiyonun govdesi eksikti - norm1 hesaplaniyor ama `return`
    yoktu, yani None donuyordu. match_with_top_n() bunu kullandigi icin
    Top-N eslestirme, sonuclari siralarken None karsilastirmasindan
    TypeError ile dusuyordu.
    """
    return SimilarityStrategy.calculate(vector1, vector2, method='cosine')


def calculate_euclidean_distance(vector1, vector2) -> float:
    """Oklid mesafesinden turetilmis benzerlik (1 / (1 + d)).

    src/matching/__init__.py bu adi import etmeye calisiyordu ama fonksiyon
    tanimli degildi; ImportError paketin tamaminin yuklenmesini engelliyordu.
    app.py bu hatayi yakalayip `matcher = None` yaptigi icin SeaTurtleID
    eslestirmesi uretimde sessizce devre disi kaliyordu.
    """
    return SimilarityStrategy.calculate(vector1, vector2, method='euclidean')


class SimilarityStrategy:
    """SOLID - Strategy Pattern: Benzerlik hesaplama algoritmaları."""
    @staticmethod
    def calculate(v1, v2, method='cosine'):
        v1, v2 = np.array(v1, dtype=np.float64), np.array(v2, dtype=np.float64)

        # Farkli boyuttaki vektorler karsilastirilamaz. Bu, model degistiginde
        # (or. egitilmis checkpoint devreye girdiginde) eski kayitlarin
        # yeniden gomulmesi gerektiginin isaretidir; np.dot'un ValueError'i
        # yerine acik bir 0 donuyoruz ki eslestirme cokmesin.
        if v1.shape != v2.shape:
            logger.warning('Gomu boyutu uyusmuyor: %s vs %s - kayitlar yeniden '
                           'gomulmeli (bkz. reid/README.md)', v1.shape, v2.shape)
            return 0.0

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


def kimlik_anahtari(kayit: Dict[str, Any]) -> str:
    """Bir galeri kaydinin ait oldugu bireyi bul.

    build_gallery.py her kayda `identity` alanini yaziyor (or. 't001').
    Daha eski galerilerde bu alan yok; o durumda turtle_id'nin sonundaki
    kare numarasi atilir: 'T001_0' ve 'T001_1' -> 't001'.
    """
    ident = kayit.get('identity')
    if ident:
        return str(ident).strip().lower()
    tid = str(kayit.get('turtle_id', '') or '')
    kok, _, ek = tid.rpartition('_')
    return (kok if kok and ek.isdigit() else tid).lower()


class KimlikIndeksi:
    """Galeriyi birey basina tek bir [k, D] matriste toplar.

    Iki isi birden cozer:

    1. A2 (multi-shot): eslestirme artik tekil kareler arasinda degil
       bireyler arasinda yapilir. Bir bireyin birden fazla karesi varsa
       skoru bu karelerden toplanir; top-N listesi de ayni bireyin
       tekrarlanan kareleriyle dolmak yerine ayri bireyler dondurur.
    2. Hiz: onceki kod her sorguda 875 kaydin her birini ayri ayri
       np.array'e ceviriyordu. Matris bir kez kurulur, sorgu tek bir
       matris carpimina duser.
    """

    def __init__(self, kayitlar: List[Dict[str, Any]]):
        gruplar: Dict[str, List[Dict[str, Any]]] = {}
        boyut_sayaci: Dict[int, int] = {}
        for kayit in kayitlar:
            vec = kayit.get('biometric_vector')
            if not vec:
                continue
            boyut_sayaci[len(vec)] = boyut_sayaci.get(len(vec), 0) + 1
            gruplar.setdefault(kimlik_anahtari(kayit), []).append(kayit)

        # Galeri tek bir modelden uretilmis olmali. Karisik boyut, kismen
        # yeniden gomulmus bir galeri demektir; cogunluk disindakileri
        # sessizce dahil etmek yerine ayikla ve say.
        self.dim = max(boyut_sayaci, key=boyut_sayaci.get) if boyut_sayaci else 0
        self.atlanan = sum(n for d, n in boyut_sayaci.items() if d != self.dim)
        if self.atlanan:
            logger.warning(
                'Galeride karisik gomu boyutu var: %s. %d kayit (beklenen '
                'boyut %d disinda) eslestirmeye alinmadi - galeriyi tek bir '
                'modelle yeniden gomun (reid/build_gallery.py).',
                dict(boyut_sayaci), self.atlanan, self.dim)

        self.identities: List[str] = []
        self.matrisler: List[np.ndarray] = []
        self.kayitlar: List[List[Dict[str, Any]]] = []
        for kimlik in sorted(gruplar):
            uygun = [k for k in gruplar[kimlik]
                     if len(k['biometric_vector']) == self.dim]
            if not uygun:
                continue
            self.identities.append(kimlik)
            self.matrisler.append(np.asarray(
                [k['biometric_vector'] for k in uygun], dtype=np.float64))
            self.kayitlar.append(uygun)

        self.kayit_sayisi = sum(len(k) for k in self.kayitlar)

    def __len__(self):
        return len(self.identities)


class TurtleMatcher:
    """
    Ana Eşleştirme Ajanı (Matching Agent).
    SOLID - Single Responsibility: Sadece biyometrik karşılaştırma ve karar verme süreçlerini yönetir.

    Eslestirme KARE duzeyinde degil KIMLIK duzeyindedir: bir bireyin
    galerideki tum kareleri tek bir skora toplanir (bkz. DEFAULT_MAX_WEIGHT).
    """

    def __init__(self, threshold: float = SIMILARITY_THRESHOLD,
                 strategy: str = 'cosine', aggregation: str = 'hybrid',
                 max_weight: float = DEFAULT_MAX_WEIGHT, db=None):
        self.threshold = threshold
        self.strategy = strategy
        self.aggregation = aggregation
        self.max_weight = float(np.clip(max_weight, 0.0, 1.0))
        self.engine = SimilarityStrategy()
        self._index = None
        self._index_kayit_sayisi = None

        # Disaridan galeri verilebilir (testler ve alternatif depolar icin);
        # verilmezse asagidaki varsayilan yukleme sirasi isler.
        if db is not None:
            self.db = db
            return

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

    # ------------------------------------------------------------------
    # Kimlik indeksi
    # ------------------------------------------------------------------
    def invalidate_index(self):
        """Galeri disaridan degistiyse indeksi tazele."""
        self._index = None
        self._index_kayit_sayisi = None

    def _indeks(self) -> KimlikIndeksi:
        """Kimlik indeksini dondur; galeri buyuyup kuculduyse yeniden kur.

        Kayit sayisi degismeden icerik degisirse (ayni turtle_id uzerine
        yazmak gibi) bu kontrol yakalamaz; o yolu kullananlar
        invalidate_index() cagirmali - add_turtle/delete_turtle zaten kayit
        sayisini degistirdigi icin kendiliginden tazelenir.
        """
        kayitlar = self.db.get_all_turtles()
        if self._index is None or self._index_kayit_sayisi != len(kayitlar):
            self._index = KimlikIndeksi(kayitlar)
            self._index_kayit_sayisi = len(kayitlar)
            logger.info('Kimlik indeksi kuruldu: %d birey / %d kare (boyut %d)',
                        len(self._index), self._index.kayit_sayisi,
                        self._index.dim)
        return self._index

    def _toplanmis_skorlar(self, incoming_vector: np.ndarray):
        """Her birey icin (skor, en_iyi_kayit) listesi. Skor [0, 1] olceginde.

        Skor = w * (en iyi karenin benzerligi) + (1 - w) * (centroid benzerligi).
        Donen kayit, o bireyin sorguya en cok benzeyen karesidir; kullaniciya
        hangi fotografla eslestigini gostermek icin gerekli.
        """
        idx = self._indeks()
        if not len(idx):
            return []

        q = np.asarray(incoming_vector, dtype=np.float64).ravel()
        if q.size != idx.dim:
            logger.warning('Gomu boyutu uyusmuyor: sorgu %d, galeri %d - '
                           'kayitlar yeniden gomulmeli (bkz. reid/README.md)',
                           q.size, idx.dim)
            return []

        w = self.max_weight
        kosinus = (self.strategy == 'cosine')
        qn = q / max(float(np.linalg.norm(q)), 1e-12) if kosinus else q

        sonuclar = []
        for kimlik, M, kayitlar in zip(idx.identities, idx.matrisler, idx.kayitlar):
            if kosinus:
                Mn = M / np.linalg.norm(M, axis=1, keepdims=True).clip(1e-12)
                kare_skor = Mn @ qn                      # [-1, 1]
                merkez = Mn.mean(axis=0)
                merkez /= max(float(np.linalg.norm(merkez)), 1e-12)
                ham = w * float(kare_skor.max()) + (1.0 - w) * float(qn @ merkez)
                # SimilarityStrategy ile ayni olcek: [-1, 1] -> [0, 1]
                skor = float(np.clip((ham + 1.0) / 2.0, 0.0, 1.0))
            else:
                # Oklid: benzerlik zaten (0, 1] araliginda
                kare_skor = 1.0 / (1.0 + np.linalg.norm(M - q, axis=1))
                merkez_skor = 1.0 / (1.0 + float(np.linalg.norm(q - M.mean(axis=0))))
                skor = w * float(kare_skor.max()) + (1.0 - w) * merkez_skor

            en_iyi = kayitlar[int(np.argmax(kare_skor))]
            sonuclar.append({
                'identity': kimlik,
                'turtle_id': en_iyi.get('turtle_id'),
                'species': en_iyi.get('species'),
                'first_recorded': en_iyi.get('first_recorded'),
                'similarity': skor,
                'frames': len(kayitlar),
            })
        return sonuclar

    def match(self, incoming_biometric_vector: List[float]) -> MatchResult:
        """
        Gelen biyometrik vektörü veritabanında ara.

        İş akışı:
        1. Gelen vektörü her BIREYIN galerisiyle karşılaştır
        2. Kare skorlarını tek bir kimlik skoruna topla
        3. En yüksek skoru eşik değerle karşılaştır
        4. Sınıflandır ve sonuç döndür

        Args:
            incoming_biometric_vector: Yeni fotoğraftan çıkarılan gömü

        Returns:
            MatchResult: Eşleştirme sonucu
        """
        similarities = self._toplanmis_skorlar(np.array(incoming_biometric_vector))

        if not similarities:
            # Galeri bos ya da gomu boyutu uyusmuyor
            return MatchResult(
                matched=False,
                classification='NEW_INDIVIDUAL',
                confidence=0.0,
                matching_method=self.strategy,
                aggregation=self.aggregation,
                reasoning='Karşılaştırılabilir kayıt yok, bu bir yeni birey.'
            )

        best_match = max(similarities, key=lambda x: x['similarity'])
        ortak = dict(
            confidence=best_match['similarity'],
            similarity_score=best_match['similarity'],
            matching_method=self.strategy,
            matched_identity=best_match['identity'],
            supporting_frames=best_match['frames'],
            aggregation=self.aggregation,
        )

        if best_match['similarity'] >= self.threshold:
            # %60+ → Kayıtlı birey
            return MatchResult(
                matched=True,
                classification='EXISTING_RECORD',
                matched_turtle_id=best_match['turtle_id'],
                reasoning=(
                    f"Benzerlik {best_match['similarity']*100:.1f}% (eşik: %{self.threshold*100}). "
                    f"{best_match['identity']} bireyi ({best_match['species']}) ile eşleşti; "
                    f"galeride {best_match['frames']} karesi var, en yakını "
                    f"{best_match['turtle_id']}. İlk kayıt: {best_match['first_recorded']}"
                ),
                **ortak
            )

        # %60- → Yeni birey
        return MatchResult(
            matched=False,
            classification='NEW_INDIVIDUAL',
            matched_turtle_id=None,
            reasoning=(
                f"Benzerlik {best_match['similarity']*100:.1f}% (eşik: %{self.threshold*100} altında). "
                f"En yakın birey: {best_match['identity']} ({best_match['similarity']*100:.1f}%). "
                f"Bu yeni bir birey olarak kaydedilecek."
            ),
            **ortak
        )

    def match_with_top_n(self, incoming_biometric_vector: List[float], top_n: int = 5) -> Dict[str, Any]:
        """
        En benzer N BIREYLE birlikte eşleştirme sonucu döndür.

        İnsan müdahalesi gereken durumlar için bu faydalıdır: liste artık
        aynı bireyin tekrarlanan kareleriyle dolmaz, N ayrı aday gösterir.

        Args:
            incoming_biometric_vector: Gelen vektör
            top_n: Döndürülecek en benzer birey sayısı

        Returns:
            Ana sonuç + top N alternatif
        """
        similarities = self._toplanmis_skorlar(np.array(incoming_biometric_vector))
        top_matches = sorted(similarities, key=lambda x: x['similarity'],
                             reverse=True)[:top_n]

        return {
            'main_result': self.match(incoming_biometric_vector),
            'top_alternatives': top_matches,
        }


# Demo: Kullanım örneği
if __name__ == '__main__':
    print("=" * 70)
    print("TURTLE MATCHER - Demo")
    print("=" * 70)
    
    matcher = TurtleMatcher(threshold=0.60, strategy='cosine')
    
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
