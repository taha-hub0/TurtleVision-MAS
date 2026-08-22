"""
Adim 5.1 - Kafa kirpma onbellegi

Egitim sirasinda her epoch'ta 2000x1333 JPEG cozmek CPU'da en buyuk
maliyettir ve her epoch ayni isi tekrarlar. Kirpmalar bir kez cikarilip
kucuk JPEG olarak diske yazilir; egitim bunlari okur.

Kirpma geometrisi embed.py / embedding_model.py ile ayni (square_crop_box,
margin 0.25). Onbellek 256 px'te tutulur: egitimde 224'e rastgele kirpma
(augmentasyon) icin pay birakir.
"""

import argparse
import os
from concurrent.futures import ProcessPoolExecutor, as_completed

import pandas as pd
from PIL import Image

from embed import square_crop_box

Image.MAX_IMAGE_PIXELS = None

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_IMAGE_ROOT = os.environ.get(
    'TURTLE_IMAGE_ROOT',
    # SeaTurtleID2022 bu depoda tutulmuyor (8.729 fotograf, ~3 GB).
    # images/ klasorunu iceren dizini TURTLE_IMAGE_ROOT ile gosterin.
    os.path.abspath(os.path.join(HERE, '..', '..', 'turtle_projesi')))


def _crop_one(args):
    image_root, out_dir, row, size, margin, region = args
    image_id, file_name, w, h, hx, hy, hw, hh, tx, ty, tw, th = row

    out_path = os.path.join(out_dir, f'{image_id}.jpg')
    if os.path.exists(out_path):
        return image_id, 'cached'

    src = os.path.join(image_root, str(file_name).replace('/', os.sep))
    try:
        with Image.open(src) as im:
            im = im.convert('RGB')

            if region == 'full':
                # Uygulamanin cikarim yolu: transforms.Resize(256) kisa kenari
                # 256'ya cekip en-boy oranini korur, sonra CenterCrop(224).
                # Onbellek de ayni geometride tutulur ki egitim ile cikarim
                # ayni goruntuyu gorsun.
                iw, ih = im.size
                olcek = size / min(iw, ih)
                im = im.resize((max(1, round(iw * olcek)), max(1, round(ih * olcek))),
                               Image.BILINEAR)
                used = 'full'
            else:
                # Kafa yoksa turtle bbox'ina, o da yoksa tum kareye dus
                if hw and hw > 0:
                    box = square_crop_box(hx, hy, hw, hh, w, h, margin)
                    used = 'head'
                elif tw and tw > 0:
                    box = square_crop_box(tx, ty, tw, th, w, h, margin)
                    used = 'turtle'
                else:
                    box, used = (0, 0, int(w), int(h)), 'fullframe-fallback'
                im = im.crop(box).resize((size, size), Image.BILINEAR)

            im.save(out_path, 'JPEG', quality=95)
        return image_id, used
    except Exception as e:
        return image_id, f'error: {e}'


def main():
    ap = argparse.ArgumentParser(description='Kafa kirpmalarini onbellege al')
    ap.add_argument('--catalog', default=os.path.join(HERE, 'data', 'catalog.csv'))
    ap.add_argument('--image-root', default=DEFAULT_IMAGE_ROOT)
    ap.add_argument('--out-dir', default=os.path.join(HERE, 'data', 'crops'))
    ap.add_argument('--region', default='head', choices=['head', 'full'],
                    help="head: kafa bbox'i kirpilir (en guclu sinyal). "
                         "full: tum kare, kisa kenar `size`'a olceklenir - "
                         "uygulamanin Resize(256)+CenterCrop(224) yoluyla uyumlu.")
    ap.add_argument('--size', type=int, default=256)
    ap.add_argument('--margin', type=float, default=0.25)
    ap.add_argument('--workers', type=int, default=os.cpu_count() or 4)
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    df = pd.read_csv(args.catalog)

    cols = ['id', 'file_name', 'width', 'height',
            'head_x', 'head_y', 'head_w', 'head_h',
            'turtle_x', 'turtle_y', 'turtle_w', 'turtle_h']
    rows = df[cols].fillna(0).itertuples(index=False, name=None)
    tasks = [(args.image_root, args.out_dir, r, args.size, args.margin, args.region)
             for r in rows]

    print(f'{len(tasks)} goruntu ({args.region}), {args.workers} surec, '
          f'hedef {args.out_dir}')
    counts, done = {}, 0
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        futures = [ex.submit(_crop_one, t) for t in tasks]
        for f in as_completed(futures):
            _, status = f.result()
            key = status if not status.startswith('error') else 'error'
            counts[key] = counts.get(key, 0) + 1
            done += 1
            if done % 1000 == 0:
                print(f'  {done}/{len(tasks)}', flush=True)

    print('bolge dagilimi:', counts)
    total = sum(os.path.getsize(os.path.join(args.out_dir, f))
                for f in os.listdir(args.out_dir))
    print(f'onbellek boyutu: {total / (1024*1024):.0f} MB')


if __name__ == '__main__':
    main()
