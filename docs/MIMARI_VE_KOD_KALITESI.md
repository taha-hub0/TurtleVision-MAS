# Mimari ve Kod Kalitesi

Bu belge `SOLID_VE_CLEAN_CODE_RAPORU.md` ve `CLEAN_CODE_SOLID_REPORT.md`
dosyalarının birleştirilmiş halidir; ikisi de aynı zemini farklı sözcüklerle
anlatıyordu.

---

## 1. SOLID prensipleri

### S — Tek Sorumluluk (Single Responsibility)

Her ajan tek bir işten sorumlu:

| Bileşen | Sorumluluk |
|---|---|
| Arayüz ajanı (React) | Kullanıcı etkileşimi ve görselleştirme |
| Analiz ajanı (Flask) | Görüntüden biyometrik gömü çıkarımı |
| Eşleştirme motoru | Gömüler arası benzerlik ve karar |
| Veri ajanı | Kayıtların saklanması |

Sınıf düzeyinde de aynı ayrım geçerli: `SimilarityStrategy` yalnızca iki
vektör arasındaki benzerliği hesaplar, `KimlikIndeksi` galeriyi birey başına
matrislere böler, `TurtleMatcher` bu ikisini kullanarak karar verir.

### O — Açık/Kapalı (Open/Closed)

Yeni bir benzerlik ölçütü (ör. Manhattan) eklemek için `TurtleMatcher`'a
dokunmak gerekmez; `SimilarityStrategy` içine yeni bir dal yeterlidir.

Aynı şey toplama yöntemi için de geçerli: kare skorlarının birey skoruna
nasıl indirgeneceği `max_weight` parametresiyle dışarıdan verilir.

### L — Liskov Yerine Geçme

`KaggleDBWrapper` ile mock veritabanı aynı arayüzü (`get_all_turtles`,
`get_turtle_by_id`) uygular ve kodda hiçbir değişiklik yapılmadan birbirinin
yerine geçer. Testler bunu kullanıyor: `TurtleMatcher(db=...)` ile sentetik
bir galeri enjekte edilebiliyor, böylece testler gerçek veri setine ya da
model checkpoint'ine bağımlı değil.

### I — Arayüz Ayrımı

API uç noktaları bağımsız: yalnızca analiz yapmak isteyen bir istemci
(`/api/analyze`) kayıt akışının yapılarına maruz kalmaz.

### D — Bağımlılıkların Tersine Çevrilmesi

`TurtleMatcher` somut bir depolama sınıfına değil, yukarıdaki iki metotluk
arayüze bağımlıdır. Veri JSON'dan da gelse, ileride bir vektör indeksinden de
gelse eşleştirme motoru değişmez.

---

## 2. Temiz kod

**İsimlendirme.** `biometric_vector`, `similarity_score`, `top_alternatives`,
`extract_features` gibi adlar amacı yorum gerektirmeden anlatır.

**Modüler yapı.** Kod `models`, `processing`, `matching`, `data` klasörlerine
ayrılmıştır.

**Hata yönetimi.** Kritik işlemler (model yükleme, dosya okuma, API çağrıları)
`try/except` ve `logging` ile korunur; hata durumunda istemciye anlamlı bir
JSON döner.

**DRY.** Benzerlik hesabı ve görüntü ön işleme merkezi fonksiyonlarda toplanır.
Eğitim hattı ile çıkarım servisi ağ mimarisini **aynı** yerden kurar
(`_build_embedding_net`), böylece ikisi ayrışamaz.

---

## 3. Bu projede asıl öğrenilen: sessiz başarısızlık

Yukarıdaki başlıklar standart. Bu kod tabanında gerçekten pahalıya mal olan
şey ise başka bir kategoriydi: **hata fırlatmayan hatalar.**

Üç örnek, üçü de ölçülerek bulundu:

1. **Eğitilmemiş rastgele katman.** Model, ResNet50'nin son katmanını
   rastgele ilklenen bir `Linear(2048, 128)` ile değiştiriyor ama bu katmanı
   diske kaydetmiyordu. Her yeniden başlatmada gömüler değişiyordu — ölçülen
   süreçler arası kosinüs **−0,1377** (olması gereken 1,0). Hiçbir istisna
   fırlamıyordu.

2. **Çift ön işleme.** `/api/analyze` görüntüyü bir kez `preprocess()` ile,
   bir kez de `extract_features` içinde BGR→RGB çeviriyordu. Aynı fotoğrafın
   galeri ve sorgu gömüsü arasındaki kosinüs **0,248**'e düşmüştü. Sistem
   çalışıyor görünüyordu.

3. **Ayar uyuşmazlığı.** Flip-TTA gömüyü değiştirir ama **boyutunu**
   değiştirmez; boyut kontrolü bunu yakalayamaz. Ölçüm: TTA'lı ve TTA'sız
   gömü arası kosinüs **0,965**.

Alınan ders, kodun biçimiyle değil doğrulanabilirliğiyle ilgili:

- **Süreçler arası regresyon testi.** `check_deterministic.py` aynı süreç
  içinde iki çağrıyı karşılaştırdığı için 1. maddeyi hiç yakalayamazdı; o test
  her zaman geçer. `tests/test_determinism.py` modeli ayrı bir süreçte kurar.
- **Değişmezi test et, uygulamayı değil.** Flip-TTA'nın testi "iki geçiş
  yapılıyor mu" değil, `f(x) == f(ayna x)` eşitliğidir.
- **Sessiz bozukluğu gürültülü hale getir.** Galeri ile model uyuşmazsa
  `/health` artık `degraded` + HTTP 503 döner ve nedenini yazar. Yanlış cevap
  fark edilir; sessiz yanlış cevap edilmez.

---

## 4. Mimari değerlendirme

Modüler ajan yapısı bileşenlerin bağımsız geliştirilip test edilmesine izin
veriyor ve sisteme yeni ajanlar (harita, drone) eklemeyi ucuzlatıyor.

Bilinen zayıflıklar `reid/README.md` içindeki "Bilinen sınırlar" bölümünde
listelidir; en önemlisi kafa dedektörünün olmaması ve eşiğin kalibre
edilmemiş olması.
