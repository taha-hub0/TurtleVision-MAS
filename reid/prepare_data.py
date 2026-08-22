"""
Adim 3.1 - Veri hazirlama

SeaTurtleID2022 veri setinden re-ID pipeline'inin ihtiyac duydugu kompakt
tabloyu uretir:

  metadata_splits.csv  (id, file_name, identity, split_closed, ...)
        +
  annotations.json     (COCO; kategoriler: 1=turtle, 2=flipper, 3=head)
        =
  reid/data/catalog.csv

annotations.json 185 MB ve segmentasyonlar RLE oldugu icin dosya belleğe
komple yuklenmez; bbox alanlari streaming regex ile cikarilir.
"""

import argparse
import csv
import os
import re
import sys

import pandas as pd

# annotations.json icindeki kayit basi: {"id": N, "image_id": M, "category_id": C,
RE_HEADER = re.compile(rb'\{"id":\s*(\d+),\s*"image_id":\s*(\d+),\s*"category_id":\s*(\d+),')
# ... ayni kaydin ilerisinde: "bbox": [x, y, w, h]
RE_BBOX = re.compile(rb'"bbox":\s*\[([^\]]*)\]')

CHUNK = 4 << 20      # 4 MB
OVERLAP = 512        # sinirda bolunen pattern'ler icin


def stream_annotations(path, verbose=True):
    """annotations.json'u parca parca okuyup (ann_id, image_id, category_id, bbox) uretir."""
    seen = set()
    pending = None          # bbox'ini bekleyen basli kayit
    leftover = b''
    consumed = 0

    size = os.path.getsize(path)
    with open(path, 'rb') as f:
        while True:
            chunk = f.read(CHUNK)
            if not chunk:
                break
            buf = leftover + chunk

            # Header ve bbox eslesmelerini konum sirasina gore harmanla:
            # her kayitta once header, sonra bbox gelir.
            events = []
            for m in RE_HEADER.finditer(buf):
                events.append((m.start(), 'h', m.groups()))
            for m in RE_BBOX.finditer(buf):
                events.append((m.start(), 'b', m.group(1)))
            events.sort()

            for _, kind, payload in events:
                if kind == 'h':
                    ann_id, image_id, cat_id = (int(x) for x in payload)
                    pending = (ann_id, image_id, cat_id)
                elif pending is not None:
                    ann_id, image_id, cat_id = pending
                    pending = None
                    if ann_id in seen:
                        continue          # overlap bolgesinden gelen tekrar
                    seen.add(ann_id)
                    try:
                        x, y, w, h = (float(v) for v in payload.split(b','))
                    except ValueError:
                        continue
                    yield ann_id, image_id, cat_id, (x, y, w, h)

            consumed += len(chunk)
            if verbose and consumed % (40 << 20) < CHUNK:
                pct = 100.0 * consumed / size
                print(f'  ... {consumed >> 20} MB / {size >> 20} MB  ({pct:.0f}%)', flush=True)

            leftover = buf[-OVERLAP:]


def build_catalog(data_dir, out_path):
    ann_path = os.path.join(data_dir, 'annotations.json')
    meta_path = os.path.join(data_dir, 'metadata_splits.csv')

    for p in (ann_path, meta_path):
        if not os.path.exists(p):
            sys.exit(f'HATA: bulunamadi -> {p}')

    print(f'[1/3] metadata_splits.csv okunuyor...')
    meta = pd.read_csv(meta_path)
    print(f'      {len(meta)} satir, {meta["identity"].nunique()} birey')

    print(f'[2/3] annotations.json taraniyor (bbox cikarimi)...')
    # image_id -> kategori basina bbox
    boxes = {}
    n = 0
    for ann_id, image_id, cat_id, bbox in stream_annotations(ann_path):
        n += 1
        slot = boxes.setdefault(image_id, {})
        # Ayni kategoriden birden fazla varsa en buyuk alanlisini tut
        prev = slot.get(cat_id)
        if prev is None or bbox[2] * bbox[3] > prev[2] * prev[3]:
            slot[cat_id] = bbox
    print(f'      {n} anotasyon, {len(boxes)} goruntu icin bbox bulundu')

    print(f'[3/3] catalog.csv yaziliyor...')
    cols = ['id', 'file_name', 'identity', 'date', 'year', 'width', 'height',
            'clarity', 'split_closed', 'split_closed_random', 'split_open']
    cols = [c for c in cols if c in meta.columns]

    rows = []
    missing_head = 0
    for r in meta[cols].itertuples(index=False):
        d = dict(zip(cols, r))
        slot = boxes.get(d['id'], {})
        turtle = slot.get(1)
        head = slot.get(3)
        if head is None:
            missing_head += 1
        for name, box in (('turtle', turtle), ('head', head)):
            for i, k in enumerate(('x', 'y', 'w', 'h')):
                d[f'{name}_{k}'] = round(box[i], 2) if box else ''
        rows.append(d)

    out_cols = cols + [f'{n}_{k}' for n in ('turtle', 'head') for k in ('x', 'y', 'w', 'h')]
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=out_cols)
        w.writeheader()
        w.writerows(rows)

    print(f'      -> {out_path}  ({len(rows)} satir)')
    print(f'      head bbox eksik: {missing_head} goruntu '
          f'({100.0 * missing_head / max(len(rows), 1):.1f}%)')
    return out_path


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    default_data = os.environ.get(
        'TURTLE_DATA_DIR',
        os.path.abspath(os.path.join(here, '..', '..', 'turtle_projesi',
                                     'turtles-data', 'data')))

    ap = argparse.ArgumentParser(description='SeaTurtleID2022 -> reid catalog.csv')
    ap.add_argument('--data-dir', default=default_data,
                    help='annotations.json ve metadata_splits.csv klasoru')
    ap.add_argument('--out', default=os.path.join(here, 'data', 'catalog.csv'))
    args = ap.parse_args()

    build_catalog(args.data_dir, args.out)


if __name__ == '__main__':
    main()
