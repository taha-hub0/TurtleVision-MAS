"""
Galeri veritabanini (kaggle_db.json) yeniden gom.

Neden gerekli
-------------
Kayitli vektorler, `turtle_model.py`'nin egitilmemis rastgele projeksiyonuyla
uretilmisti; o katman her surec baslangicinda degistigi icin vektorler zaten
gecersizdi. Projeksiyon kaldirildiktan sonra gomu boyutu da degisti
(128 -> 2048), dolayisiyla eski kayitlar hem anlamsiz hem uyumsuz.

Bu betik galeriyi SeaTurtleID2022'den yeniden kurar.

ONEMLI - ayni kod yolu
----------------------
Gomuler `TurtleIdentificationModel.extract_features` ile uretilir, yani
/api/analyze endpoint'inin kullandigi yolun aynisi (Resize(256) ->
CenterCrop(224) -> ImageNet normalizasyonu, tum kare). Galeri ile sorgu
ayni on islemeden gecmezse kosinus benzerligi anlamsizlasir - bu yuzden
burada reid/embed.py'nin kafa kirpmali yolu KULLANILMAZ.

Kullanim
--------
    python reid/build_gallery.py --images-root /path/to/turtle_projesi \\
                                 --per-identity 2
"""

import argparse
import hashlib
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone

import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
AGENT = os.path.abspath(os.path.join(HERE, '..', 'image-analysis-agent'))
sys.path.insert(0, AGENT)

from src.models.turtle_model import TurtleIdentificationModel  # noqa: E402


def dosya_sha256(yol, blok=1 << 20):
    """Checkpoint parmak izi - galerinin hangi modelle uretildigini kaydeder."""
    if not yol or not os.path.exists(yol):
        return None
    h = hashlib.sha256()
    with open(yol, 'rb') as f:
        for parca in iter(lambda: f.read(blok), b''):
            h.update(parca)
    return h.hexdigest()


def meta_yaz(out, model, kayit_sayisi, birey_sayisi):
    """Galerinin yanina uyum kaydi birak.

    Gomu boyutu tek basina yetmiyor: flip-TTA acik/kapali ayni boyutu
    uretir ama farkli vektorler verir (kosinus ~0.965). Model dosyasi ya da
    cikarim ayari degistiginde galeri de yeniden gomulmeli; app.py acilista
    bu dosyayi model bilgisiyle karsilastirip uyusmazsa 503 doner.
    """
    meta = {
        'embedding_dim': model.embedding_dim,
        'backbone': getattr(model, 'backbone_name', None),
        'fine_tuned': model.fine_tuned,
        'preprocess_profile': getattr(model, 'profile', 'full'),
        'flip_tta': getattr(model, 'flip_tta', None),
        'model_sha256': dosya_sha256(model.model_path),
        'record_count': kayit_sayisi,
        'identity_count': birey_sayisi,
        'built_at': datetime.now(timezone.utc).isoformat(timespec='seconds'),
    }
    yol = os.path.splitext(out)[0] + '.meta.json'
    with open(yol, 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    return yol, meta


def toplanan_fotograflar(images_root, per_identity):
    """images/<identity>/<foto>.JPG duzeninden birey basina N fotograf sec."""
    kok = os.path.join(images_root, 'images')
    if not os.path.isdir(kok):
        sys.exit(f'HATA: {kok} yok. --images-root degerini kontrol edin.')

    secilen = defaultdict(list)
    for identity in sorted(os.listdir(kok)):
        klasor = os.path.join(kok, identity)
        if not os.path.isdir(klasor):
            continue
        dosyalar = sorted(f for f in os.listdir(klasor)
                          if f.lower().endswith(('.jpg', '.jpeg', '.png')))
        for f in dosyalar[:per_identity]:
            secilen[identity].append(os.path.join(klasor, f))
    return secilen


def main():
    ap = argparse.ArgumentParser(description='Galeri veritabanini yeniden gom')
    ap.add_argument('--images-root',
                    default=os.environ.get('TURTLE_IMAGE_ROOT', ''),
                    help='images/ klasorunu iceren dizin')
    ap.add_argument('--per-identity', type=int, default=2,
                    help='birey basina kac fotograf indekslensin')
    ap.add_argument('--model-path', default=None,
                    help='ArcFace checkpoint (yoksa ImageNet govdesi)')
    ap.add_argument('--out', default=os.path.join(
        AGENT, 'data', 'kaggle_seaturtle', 'kaggle_db.json'))
    args = ap.parse_args()

    if not args.images_root:
        sys.exit('HATA: --images-root veya TURTLE_IMAGE_ROOT gerekli.')

    secilen = toplanan_fotograflar(args.images_root, args.per_identity)
    toplam = sum(len(v) for v in secilen.values())
    print(f'{len(secilen)} birey, {toplam} fotograf indekslenecek')

    model = TurtleIdentificationModel(model_path=args.model_path)
    print(f'gomu boyutu: {model.embedding_dim} | fine_tuned: {model.fine_tuned} '
          f'| flip_tta: {model.flip_tta}')

    db, hatali, islenen = {}, 0, 0
    for identity, yollar in secilen.items():
        for i, yol in enumerate(yollar):
            img = cv2.imread(yol)
            if img is None:
                hatali += 1
                continue
            try:
                vec = model.extract_features(img)
            except Exception as e:
                print(f'  atlandi {yol}: {e}')
                hatali += 1
                continue

            kayit_id = f'{identity.upper()}_{i}'
            db[kayit_id] = {
                'turtle_id': kayit_id,
                'identity': identity,          # ayni bireyin kareleri bunu paylasir
                'species': 'Caretta caretta',  # SeaTurtleID2022 tek turden olusur
                'biometric_vector': [float(x) for x in vec],
                'location': 'Zakynthos, Greece',
                'first_recorded': '2022-01-01',
                'sightings': len(yollar),
                'quality_score': 1.0,
                'source_image': os.path.relpath(yol, args.images_root).replace(os.sep, '/'),
            }
            islenen += 1
            if islenen % 100 == 0:
                print(f'  {islenen}/{toplam}', flush=True)

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False)

    meta_yolu, meta = meta_yaz(args.out, model, len(db), len(secilen))

    print(f'-> {args.out}')
    print(f'   {len(db)} kayit yazildi, {hatali} okunamadi')
    print(f'   gomu boyutu: {model.embedding_dim} | flip_tta: {meta["flip_tta"]}')
    print(f'-> {meta_yolu}')


if __name__ == '__main__':
    main()
