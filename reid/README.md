# reid/ — Offline re-ID araç zinciri

Bu klasör **çalışma zamanı servisi değildir**. Kaplumbağa bireylerini
fotoğraftan ayırt eden modeli veri setinden üreten ve doğruluğunu ölçen
araçları barındırır. Servisler yalnızca çıktısını (bir checkpoint dosyası)
kullanır.

## Neden ayrı bir katman gerekti

Sistemin ilk hâlinde tanımlama katmanı bir taslaktı:

| Bileşen | Eski davranış | Sonuç |
|---|---|---|
| `TurtleIdentificationModel.extract_features` | `np.random.randn(512)` | Aynı fotoğraf iki kez gönderilince iki farklı "öznitelik" |
| `TurtleIdentificationModel.identify_turtle` | Sabit `('turtle_001', 'Chelonia mydas', 0.92)` | Görüntüden bağımsız cevap |
| Biolytics `extract_biometric_code` | Canny kenarlarından değişken uzunlukta rakam dizisi | Poz/ışık değişince tamamen farklı kod |
| DB `similarity-search` | `SELECT * FROM turtles LIMIT 10` | Benzerlik hiç hesaplanmıyor |

Elde 8.729 fotoğraf ve 438 birey içeren SeaTurtleID2022 veri seti duruyordu
ama kod tabanında bu verinin adı bile geçmiyordu.

## Veri seti

`turtles-data/data/` altında:

- `metadata_splits.csv` — 8.729 satır; `identity` (t001…t438), tarih ve
  üç resmî bölünme
- `annotations.json` — 185 MB COCO; `turtle` / `flipper` / `head`
  kategorileri için RLE segmentasyon + bbox
- `images/` — 438 klasör, bireye göre gruplanmış

Bölünmeler eşdeğer değildir:

- `split_closed` — **zamansal** (yıl bazlı). Gerçekçi senaryo: modeli geçmiş
  yılların fotoğraflarıyla kurup yeni sezonda tanımlama yapmak.
- `split_closed_random` — rastgele. Aynı günün kareleri hem galeriye hem
  sorguya düşer, yani model bireyi değil çekim koşullarını eşleştirerek de
  yüksek skor alabilir. **Bu bölünmedeki skorlar iyimserdir.**
- `split_open` — açık-set: sorguların bir kısmının galeride karşılığı yok.
  Sahadaki asıl soruya bu karşılık gelir: "bu daha önce kaydettiğimiz bir
  birey mi, yoksa yeni mi?"

## Boru hattı

```
prepare_data.py   annotations.json + metadata_splits.csv -> data/catalog.csv
      |           (185 MB dosya belleğe yüklenmez; bbox'lar streaming ile çıkarılır)
      v
cache_crops.py    kafa kırpmalarını 256 px JPEG olarak önbelleğe alır
      |           (her epoch'ta 2000x1333 JPEG çözmek CPU'da en büyük maliyet)
      v
train.py          ArcFace ile metrik öğrenme -> data/arcface_best.pt
      |
      v
embed.py          tüm veri setini gömer -> data/embeddings_*.npz
      |
      v
evaluate.py       top-1 / top-5 / mAP + açık-set eşik taraması
```

### Sadece modeli kullanmak istiyorsanız

Eğitmeye gerek yok — hazır checkpoint bir GitHub Release'inde:

```bash
python reid/fetch_model.py
```

Betik dosyayı `image-analysis-agent/src/models/weights/arcface_best.pt`
konumuna indirir ve SHA256'sını doğrular. Checkpoint depoda tutulmuyor:
44 MB'lık ikili bir dosya ve model yeniden eğitilecek; git geçmişi kalıcı
olduğu için her iterasyon depoyu geri alınamaz biçimde büyütürdü.

> **Model ile galeri birbirine bağlıdır.** `kaggle_db.json` içindeki gömüler
> belirli bir modelle üretilmiştir. Model değişirse galeri de
> `build_gallery.py` ile yeniden gömülmelidir; aksi halde boyutlar uyuşmaz ve
> sistem **her fotoğrafa "yeni birey" der**. Bu durumda `/health` ucu
> `degraded` + HTTP 503 döner ve nedenini söyler.

### Sıfırdan eğitmek

```bash
cd reid
pip install -r requirements.txt

python prepare_data.py                              # ~2 dk

# Profil seçimi — çıkarım tarafıyla AYNI olmalı:
#   full : uygulamanın bugünkü yolu (Resize(256) -> CenterCrop(224), tüm kare)
#   head : kafa kırpma (daha güçlü sinyal, ama çıkarımda kafa bbox'i gerekir)
python cache_crops.py --region full --out-dir data/crops_full
python train.py --profile full --crop-dir data/crops_full \
                --backbone resnet18 --epochs 30    # GPU'da ~10 dk

python embed.py --region full --weights data/arcface_best.pt
python evaluate.py --embeddings data/embeddings_arcface_full.npz

# Galeriyi yeni modelle yeniden göm
python build_gallery.py --images-root <veri-seti-yolu> --model-path data/arcface_best.pt
```

## Tasarım kararları

**Neden kafa kırpılıyor?** Kafa bbox'i görüntünün medyanda **%1,3'ünü**
kaplıyor. Deniz kaplumbağası photo-ID'sinin standart biyometrik işareti
post-ocular scutes (göz arkası pul dizilimi); tüm kareyi modele vermek bu
sinyali deniz dokusu ve arka plan içinde boğar. Veri setinin `head`
segmentasyonu tam olarak bu bölgeyi veriyor — 8.526 fotoğrafta kafa,
200'ünde gövde bbox'ine, 3'ünde tüm kareye düşülüyor.

**Neden ArcFace?** ImageNet ön-eğitimli öznitelikler bireyleri ayırt
edemiyor (aşağıdaki tabloya bakın). Sınıflandırma kaybı "kaplumbağa"yı
ayırmayı öğretir, "*bu* kaplumbağa"yı değil. ArcFace açısal marj ekleyerek
aynı bireyin gömülerini bir yöne toplar ve farklı bireyleri en az `m` radyan
iter; çıktısı doğrudan kosinüs ile karşılaştırılabilir — sistemin ihtiyacı
olan tam da bu.

**Ön işleme pariteliği.** Galeri gömüleri (`embed.py`) ile çalışma zamanı
sorguları (`embedding_model.py`) **birebir aynı** ön işlemeden geçmelidir.
Bunu bir kez ihlal ettik: galeri PIL, çalışma zamanı `cv2.INTER_LINEAR`
kullanıyordu; cv2 küçültmede antialias uygulamadığı için aynı kırpma
0,95 kosinüslük farklı bir gömü veriyordu — eşleştirme eşiğiyle aynı
mertebede bir gürültü. İkisi de PIL'e alındı, parite 1,000000 doğrulandı.
`square_crop_box` geometrisi de aynı sebeple ortaktır.

**Bölünme disiplini.** `train.py` yalnızca `train` bölümünü görür;
`valid` erken durdurma için, `test` yalnızca `evaluate.py`'ye kalır.

## Sonuçlar

ImageNet ön-eğitimli ResNet50 (temel çizgi, eğitim yok):

| Bölünme | top-1 | top-5 | mAP |
|---|---|---|---|
| `split_closed` (zamansal) | %4,60 | %13,15 | %1,56 |
| `split_closed_random` | %22,26 | %36,78 | %3,96 |

Ayrışma ölçüsü: aynı birey kosinüs ortalaması 0,742 — farklı birey 0,670
(Cohen d = 0,33). Dağılımlar neredeyse tamamen üst üste, yani bu gömülerle
kurulan herhangi bir eşik ya çok fazla yanlış eşleşme ya çok fazla kaçırma
üretir.

`split_closed_random`'ın 4,6'dan 22'ye fırlaması da bunu doğruluyor: o
bölünme aynı günün karelerini sızdırıyor.

ArcFace ile ince ayar (`--profile full`, ResNet18, 30 epoch), test bölünmesi:

| Bölünme | top-1 | top-5 | mAP |
|---|---:|---:|---:|
| `split_closed` (zamansal) | %10,75 | %18,43 | %7,66 |
| `split_closed_random` | %71,28 | %79,90 | %31,36 |

Canlı API üzerinden (galeri 875 kayıt / 438 birey, sorgu her bireyin
galeride bulunmayan bir fotoğrafı, n=40):

| Senaryo | ImageNet gövdesi | ArcFace |
|---|---:|---:|
| Aynı gün (iyimser) | %10,0 | %85,0 |
| Farklı gün (gerçekçi) | %2,5 | %32,5 |

"Farklı gün" sahadaki gerçek senaryodur: sorgu, galeriyle aynı çekim
seansından değildir.

### Bu sayıların söylediği

`split_closed_random` (%71,28) ile `split_closed` (%10,75) arasındaki
uçurum modelin ne öğrendiğini ele veriyor. Rastgele bölünme aynı günün
karelerini hem galeriye hem sorguya sızdırıyor; model bireyi değil **çekim
seansını** (ışık, su rengi, arka plan, poz) eşleştirerek de yüksek skor
alabiliyor. Eğitim doğruluğunun %94,5 iken doğrulama top-1'inin %16,8'de
kalması da aynı şeyi gösteriyor.

Sebebi tüm karenin modele verilmesi: kestirme yol açık kalıyor. Kafa
kırpmalı bir ön denemede doğrulama top-1'i **4 epoch'ta %28**'e ulaşmıştı;
bu tam kare koşusu **30 epoch'ta %16,8**'de kaldı. Kafa dedektörü bu yüzden
sonraki adım.

## Bilinen sınırlar

- **Kafa dedektörü yok.** Çalışma zamanında bbox çağıran tarafından
  verilmelidir; verilmezse tüm kare gömülür ve doğruluk ciddi ölçüde düşer.
  Veri setinin `head` maskeleri bir dedektör eğitmek için yeterli
  (8.526 örnek) — sonraki adım burasıdır.
- **Tür sınıflandırıcı yok.** Veri seti tek türden (*Caretta caretta*)
  oluşuyor; ondan tür sınıflandırıcı öğrenilemez. Bu yüzden servis
  `species: null` döndürür, uydurma bir tür değil.
- **CPU'da eğitildi.** `resnet18` @224 seçimi donanım kısıtından; GPU ile
  `resnet50` ve daha yüksek çözünürlük belirgin kazanç sağlar.
