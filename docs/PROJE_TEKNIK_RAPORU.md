# 🐢 TurtleVision: Deniz Kaplumbağası Biyometrik Tanımlama Sistemi
## Teknik Proje Raporu

**Proje Başlığı:** Çok Etmenli Sistem (MAS) Tabanlı Non-Invasive Deniz Kaplumbağası Tanımlama ve İzleme Platformu

---

### 1. Giriş ve Problem Tanımı
Deniz kaplumbağalarının popülasyon takibi, deniz biyolojisi ve koruma çalışmaları için hayati önem taşır. Geleneksel yöntemler olan plastik veya metal markalama (tagging), hayvanlara fiziksel müdahale gerektirir (invasive), enfeksiyon riski taşır ve markaların zamanla düşmesi nedeniyle uzun vadeli veri kaybına yol açar.

**TurtleVision**, bu problemi ortadan kaldırmak için kaplumbağaların yüzlerindeki pul desenlerinin (scutes) birer "biyometrik parmak izi" olduğu gerçeğinden yola çıkarak, tamamen fotoğraf tabanlı ve otonom bir tanımlama sistemi sunar.

### 2. Sistem Mimarisi ve Çok Etmenli Yapı (MAS)
Sistem, birbirleriyle asenkron olarak haberleşen üç temel otonom etmenden oluşmaktadır:

*   **Görüntü Analiz Etmeni (Analysis Agent):** PyTorch ve ResNet50 derin öğrenme modellerini kullanarak görüntüyü 128 boyutlu bir biyometrik vektöre (Embedding) dönüştürür.
*   **Biyometrik Eşleştirme Etmeni (Matching Agent):** **SOLID Strategy Pattern** kullanılarak geliştirilmiştir. Cosine Similarity ve Euclidean Distance gibi algoritmaları çalışma anında (runtime) değiştirebilme esnekliğine sahiptir.
*   **Veri Yönetim Etmeni (Persistence Agent):** Kaggle SeaTurtleID2022 veri seti tabanlı yerel biyometrik veritabanını yönetir ve offline-first (internet bağımsız) çalışma mimarisini destekler.

### 3. Teknik Yenilikler ve Yazılım Prensipleri
Proje, akademik seviyede bir yazılım mühendisliği disipliniyle geliştirilmiştir:
*   **SOLID Uyumluluğu:** Benzerlik hesaplama motoru, genişletilmeye açık ancak değişime kapalı (Open/Closed) bir yapıda kurgulanmıştır.
*   **Yüksek Performans:** 1500+ kayıt arasında biyometrik arama, milisaniyeler düzeyinde optimize edilmiştir.
*   **Kullanıcı Deneyimi:** Akademik sunum için optimize edilmiş, temiz ve sade kullanıcı arayüzü ile biyolojik verilerin görselleştirilmesi sağlanmıştır.

### 4. Sonuç
TurtleVision, Yapay Zeka ve Çok Etmenli Sistemlerin çevre koruma alanında nasıl uygulanabileceğini gösteren, ölçeklenebilir, non-invasive ve sağlam bir çözüm sunmaktadır.
