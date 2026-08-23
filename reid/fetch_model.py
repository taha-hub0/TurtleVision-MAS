"""
Egitilmis re-ID modelini GitHub Release'inden indir.

Checkpoint depoda tutulmaz: 44 MB'lik ikili bir dosya ve model kafa
dedektoru eklendiginde yeniden egitilecek. Git gecmisi kalicidir, her
yeniden egitim depoyu bir 44 MB daha buyutur ve bir daha kucultulemez.
Release asset'leri ise surumlenebilir ve silinebilir.

Kullanim:
    python reid/fetch_model.py                 # varsayilan surumu indir
    python reid/fetch_model.py --tag v0.2-...  # belirli bir surum
    python reid/fetch_model.py --force         # mevcut dosyanin uzerine yaz
"""

import argparse
import hashlib
import os
import shutil
import sys
import tempfile
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
HEDEF = os.path.abspath(os.path.join(
    HERE, '..', 'image-analysis-agent', 'src', 'models', 'weights', 'arcface_best.pt'))

REPO = 'taha-hub0/TurtleVision-MAS'
VARSAYILAN_TAG = 'v0.1-reid-fullframe'
DOSYA = 'arcface_best.pt'

# Bilinen surumlerin SHA256'lari. Indirilen dosyanin butunlugunu dogrular;
# yarim inen ya da degistirilmis bir checkpoint sessizce yuklenmemeli.
SHA256 = {
    'v0.1-reid-fullframe':
        '3252475a3606b59332964723c7e0a6039728dc027d1612435cd5face9061a31c',
}


def dosya_sha256(yol, blok=1 << 20):
    h = hashlib.sha256()
    with open(yol, 'rb') as f:
        for parca in iter(lambda: f.read(blok), b''):
            h.update(parca)
    return h.hexdigest()


def indir(url, hedef_gecici):
    def ilerleme(sayi, blok, toplam):
        if toplam > 0:
            yuzde = min(100, 100 * sayi * blok / toplam)
            mb = toplam / (1024 * 1024)
            print(f'\r  {yuzde:5.1f}%  ({mb:.0f} MB)', end='', flush=True)

    urllib.request.urlretrieve(url, hedef_gecici, reporthook=ilerleme)
    print()


def main():
    ap = argparse.ArgumentParser(description='re-ID checkpoint indirici')
    ap.add_argument('--tag', default=VARSAYILAN_TAG)
    ap.add_argument('--out', default=HEDEF)
    ap.add_argument('--force', action='store_true',
                    help='dosya varsa uzerine yaz')
    args = ap.parse_args()

    if os.path.exists(args.out) and not args.force:
        mevcut = dosya_sha256(args.out)
        beklenen = SHA256.get(args.tag)
        if beklenen and mevcut == beklenen:
            print(f'Model zaten mevcut ve dogru: {args.out}')
            return 0
        print(f'Model mevcut ama {args.tag} ile ayni degil: {args.out}')
        print('Uzerine yazmak icin --force kullanin.')
        return 0

    url = f'https://github.com/{REPO}/releases/download/{args.tag}/{DOSYA}'
    print(f'Indiriliyor: {url}')

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    fd, gecici = tempfile.mkstemp(suffix='.pt', dir=os.path.dirname(args.out))
    os.close(fd)

    try:
        indir(url, gecici)
    except urllib.error.HTTPError as e:
        os.unlink(gecici)
        print(f'HATA: indirilemedi ({e.code} {e.reason})', file=sys.stderr)
        print(f'Surumleri kontrol edin: https://github.com/{REPO}/releases',
              file=sys.stderr)
        return 1
    except Exception as e:
        os.unlink(gecici)
        print(f'HATA: {e}', file=sys.stderr)
        return 1

    beklenen = SHA256.get(args.tag)
    if beklenen:
        gercek = dosya_sha256(gecici)
        if gercek != beklenen:
            os.unlink(gecici)
            print('HATA: SHA256 uyusmuyor - dosya bozuk ya da degistirilmis.',
                  file=sys.stderr)
            print(f'  beklenen: {beklenen}\n  gelen   : {gercek}', file=sys.stderr)
            return 1
        print('SHA256 dogrulandi.')
    else:
        print(f'UYARI: {args.tag} icin bilinen SHA256 yok, butunluk dogrulanmadi.')

    shutil.move(gecici, args.out)      # atomik: yarim dosya birakmaz
    print(f'-> {args.out}')
    print()
    print('Not: galeri gomuleri bu modelle uretilmis olmali. Model degistiyse:')
    print('     python reid/build_gallery.py --images-root <veri-seti-yolu> \\')
    print('            --model-path image-analysis-agent/src/models/weights/arcface_best.pt')
    return 0


if __name__ == '__main__':
    sys.exit(main())
