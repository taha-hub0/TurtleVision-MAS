"""
SeaTurtleID2022 Integration - Quick Start Example
==================================================

Bu dosya, turtle-id-mas sistemine SeaTurtleID2022 matching logic'ini
hızlıca entegre etmek için gerekli adımları gösterir.

Kısa Özet (TL;DR):
- Mock database: 20 kaplumbağa örneği
- Cosine similarity ile %60 benzerlik eşiği
- Otomatik "Kayıtlı Birey" vs "Yeni Birey" sınıflandırması
"""

# ============================================================================
# EXAMPLE 1: Python'da Direkt Kullanım
# ============================================================================

def example_python_direct_usage():
    """
    Python image-analysis-agent içinde direkt TurtleMatcher kullanma
    """
    import numpy as np
    from src.data.seaturtle_mock_db import get_mock_database
    from src.matching.turtle_matcher import TurtleMatcher, MatchResult
    
    # Matcher'ı başlat (%60 eşik, cosine similarity)
    matcher = TurtleMatcher(threshold=0.60, method='cosine')
    
    # Gelen fotoğraftan çıkarılmış biyometrik vektör (128-boyutlu)
    # Gerçekte: CNN model tarafından çıkarılır
    # Demo için: Random vektör
    incoming_vector = np.random.random(128).tolist()
    
    # Eşleştirme yap
    result = matcher.match(incoming_vector)
    
    # Sonuç
    print(f"Sınıflandırma: {result.classification}")
    print(f"Güven: {result.confidence * 100:.1f}%")
    print(f"Sebep: {result.reasoning}")
    
    if result.classification == 'EXISTING_RECORD':
        print(f"✓ Eşleşen kaplumbağa: {result.matched_turtle_id}")
    else:
        print(f"⚠ Yeni birey, veritabanına eklenecek")


# ============================================================================
# EXAMPLE 2: HTTP API Üzerinden (Flask)
# ============================================================================

def example_http_api_usage():
    """
    Backend'i çalıştırırken, HTTP POST request'i gönderme
    """
    import requests
    import numpy as np
    
    # Image Analysis Agent'ın /api/match endpoint'i
    URL = 'http://localhost:5000/api/match'
    
    # Biometric vektör (veya real model'den gelir)
    biometric_vector = np.random.random(128).tolist()
    
    # Request gönder
    response = requests.post(URL, json={
        'biometric_vector': biometric_vector,
        'threshold': 0.60,
        'method': 'cosine',
        'metadata': {
            'location': 'Dalyan Beach',
            'capture_date': '2024-01-15T10:30:00Z',
        }
    })
    
    if response.status_code == 200:
        result = response.json()
        print(f"Sonuç: {result['classification']}")
        print(f"Güven: {result['confidence']*100:.1f}%")
    else:
        print(f"Hata: {response.status_code}")


# ============================================================================
# EXAMPLE 3: Matching Agent ile (Node.js Backend)
# ============================================================================

def example_node_js_matching_agent():
    """
    JavaScript Matching Agent'ın SeaTurtleID entegrasyonu
    
    File: backend/src/agents/matchingAgentWithSeaTurtleID.js
    
    Usage:
        const { runMatchingAgent } = require('./agents/matchingAgentWithSeaTurtleID');
        
        const result = await runMatchingAgent({
            photoId: 'photo_123',
            biometricVector: [0.45, 0.23, ..., 0.78],  // 128 elements
            location: 'Dalyan Beach',
            captureDate: '2024-01-15T10:30:00Z'
        });
        
        if (result.success) {
            console.log(result.data.matchResult.classification);
            // EXISTING_RECORD or NEW_INDIVIDUAL
        }
    """
    pass


# ============================================================================
# EXAMPLE 4: Frontend Integration (React)
# ============================================================================

REACT_EXAMPLE = """
// frontend/src/api/services/identificationService.ts

export async function identifyTurtle(imageFile: File, location: string) {
    // 1. Görüntüyü Image Analysis Agent'a gönder
    const formData = new FormData();
    formData.append('file', imageFile);
    
    const imageResponse = await fetch('/api/analyze', {
        method: 'POST',
        body: formData,
    });
    
    const imageData = await imageResponse.json();
    const biometricVector = imageData.features;  // 128-boyutlu
    
    // 2. Biometric vektörü Matching Agent'a gönder
    const matchResponse = await fetch('/api/identify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            photoId: `photo_${Date.now()}`,
            biometricVector: biometricVector,
            location: location,
            captureDate: new Date().toISOString(),
        }),
    });
    
    const matchData = await matchResponse.json();
    
    // 3. Sonuca göre UI'ı güncelle
    if (matchData.identification.matchResult.classification === 'EXISTING_RECORD') {
        // Mevcut kaplumbağa profilini göster
        navigate(`/turtle/${matchData.turtleId}`);
    } else {
        // Yeni birey formu göster
        showNewIndividualForm();
    }
    
    return matchData;
}
"""


# ============================================================================
# EXAMPLE 5: Top-N Matching (İnsan Müdahalesi Gereken Durumlar)
# ============================================================================

def example_top_n_matching():
    """
    Benzerlik eşiğin yakınında ise (58-62%), insanın karar vermesi için
    en benzer 5 kayıt göster
    """
    import requests
    import numpy as np
    
    URL = 'http://localhost:5000/api/match-top-n'
    
    biometric_vector = np.random.random(128).tolist()
    
    response = requests.post(URL, json={
        'biometric_vector': biometric_vector,
        'top_n': 5,
        'threshold': 0.60,
        'method': 'cosine'
    })
    
    if response.status_code == 200:
        result = response.json()
        
        print("Ana Sonuç:")
        print(f"  Sınıflandırma: {result['main_result']['classification']}")
        print(f"  Güven: {result['main_result']['confidence']*100:.1f}%")
        
        print("\nEn Benzer Alternatifler (Manuel Doğrulama İçin):")
        for i, alt in enumerate(result['top_alternatives'], 1):
            print(f"  {i}. {alt['turtle_id']} ({alt['species']}) - "
                  f"{alt['similarity']*100:.1f}%")


# ============================================================================
# EXAMPLE 6: Detaylı Sınıflandırma Mantığı
# ============================================================================

"""
Eşik Kontrol Akışı:
====================

similarity_score = cosine_similarity(incoming_vector, db_vector)

if similarity_score >= 0.60:  # %60 ve üzeri
    classification = "EXISTING_RECORD"
    action = "Show turtle profile"
    confidence = similarity_score
    
else:  # %60 altında
    classification = "NEW_INDIVIDUAL"
    action = "Show new individual form"
    confidence = similarity_score


Örnek Sonuçlar:
===============

1. similarity_score = 0.847
   → EXISTING_RECORD (güven: %84.7)
   → turtle_015 profili göster
   → Avistama sayısını artır

2. similarity_score = 0.423
   → NEW_INDIVIDUAL (güven: %42.3)
   → Yeni birey formu göster
   → Veritabanına ekle

3. similarity_score = 0.589
   → NEW_INDIVIDUAL (eşik altında)
   → Ama top-5'te öneriler göster
   → İnsan karar versin
"""


# ============================================================================
# EXAMPLE 7: Veritabanı Sorguları
# ============================================================================

def example_database_queries():
    """
    Mock veritabanında kayıt sorgulama
    """
    from src.data.seaturtle_mock_db import get_mock_database
    
    db = get_mock_database()
    
    # Tüm kaplumbağaları al
    all_turtles = db.get_all_turtles()
    print(f"Toplam kayıt: {len(all_turtles)}")
    
    # Belirli bir kaplumbağayı al
    turtle = db.get_turtle_by_id('turtle_001')
    if turtle:
        print(f"Tür: {turtle['species']}")
        print(f"Konum: {turtle['location']}")
        print(f"Avistama sayısı: {turtle['sightings']}")
    
    # Türe göre filtrele
    green_turtles = db.get_turtles_by_species('GREEN_TURTLE')
    print(f"Yeşil kaplumbağa: {len(green_turtles)}")
    
    # Avistama sayısını artır
    db.add_sighting('turtle_001')
    updated = db.get_turtle_by_id('turtle_001')
    print(f"Güncellenmiş avistama: {updated['sightings']}")


# ============================================================================
# EXAMPLE 8: Test Senaryoları
# ============================================================================

"""
Test Senaryoları
================

Senaryo 1: Kesin Eşleşme
─────────────────────────
INPUT: turtle_001'in biyometrik vektörüne çok benzer
OUTPUT: EXISTING_RECORD (similarity ≈ 0.95)
EXPECTED: turtle_001 profili gösterilmeli


Senaryo 2: Kesin Yeni Birey
──────────────────────────
INPUT: Hiçbir kayıtla benzer olmayan rastgele vektör
OUTPUT: NEW_INDIVIDUAL (similarity ≈ 0.35)
EXPECTED: Yeni birey formu gösterilmeli


Senaryo 3: Sınır Durumu
─────────────────────
INPUT: similarity = 0.58 (eşik altında ama yakın)
OUTPUT: NEW_INDIVIDUAL ama top-5 alternatif gösterilmeli
EXPECTED: İnsan karar verebilmeli


Senaryo 4: Hata Yönetimi
────────────────────────
INPUT: Boş/geçersiz biometric_vector
OUTPUT: 400 Bad Request
EXPECTED: Uygun hata mesajı döndürülmeli
"""


# ============================================================================
# EXAMPLE 9: Performance Tuning
# ============================================================================

"""
Performans Optimizasyonu
==========================

Mevcut Performans:
- Tek eşleştirme: ~0.4ms (20 kaplumbağa)
- Top-5 bulma: ~1-2ms
- Flask endpoint latency: ~10-50ms (ağ + JSON parsing)

Ölçeklendirme (1000+ kaplumbağa için):
1. Faiss (Meta) kullan: O(log N) similarity search
2. Caching: Benzer vektörleri ön-hesapla
3. GPU acceleration: CUDA ile batch processing
4. Approximate nearest neighbors: LSH (Locality Sensitive Hashing)

For now: Mock database (20 specimen) yeterli, üretim hazırlıkları yapılabilir.
"""


# ============================================================================
# CHECKLIST: Entegrasyon Tamamlama
# ============================================================================

INTEGRATION_CHECKLIST = """
✓ Tamamlandı:
─────────────
[✓] seaturtle_mock_db.py - Mock database (20 specimen)
[✓] turtle_matcher.py - Cosine similarity + %60 threshold
[✓] matchingAgentWithSeaTurtleID.js - Node.js entegrasyonu
[✓] app.py /api/match endpoints - Flask endpoints
[✓] SEATURTLE_ID2022_INTEGRATION.md - Akademik dokumentasyon

⏳ Yapılacak:
────────────
[ ] Real CNN model integration (şu an placeholder)
[ ] Frontend /api/identify endpoint entegrasyonu
[ ] Full SeaTurtleID2022 database (1600+ bireyler)
[ ] Similarity threshold tuning (A/B test gerekli)
[ ] UI için Top-N matching arayüzü
[ ] Automated test suite

Test Etme:
──────────
1. Python:
   $ python src/matching/turtle_matcher.py

2. Flask:
   $ python app.py
   $ curl -X POST http://localhost:5000/api/match \\
       -H "Content-Type: application/json" \\
       -d '{"biometric_vector": [...]}'

3. Full Stack:
   $ npm start (frontend)
   $ python app.py (image-analysis-agent)
   $ node backend/index.js (coordinator)
   $ Upload test photo ve verify classification
"""

if __name__ == '__main__':
    print("🐢 SeaTurtleID2022 Integration Examples")
    print("=" * 50)
    print("\nMevcut örnekler:")
    print("1. example_python_direct_usage() - Python direkt")
    print("2. example_http_api_usage() - HTTP API")
    print("3. example_top_n_matching() - Top-5 matching")
    print("4. example_database_queries() - Veritabanı sorguları")
    print("\nDocumentation: docs/SEATURTLE_ID2022_INTEGRATION.md")
