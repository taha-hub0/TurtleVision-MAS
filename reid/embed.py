"""
Adim 3.2 - Gomu (embedding) cikarimi

Her fotograftan kafa bolgesini kirpip pretrained bir CNN backbone ile
L2-normalize edilmis oznitelik vektoru uretir.

Neden kafa? SeaTurtleID2022'de kafa bbox'i goruntunun medyanda %1.3'unu
kapliyor. Post-ocular scutes (goz arkasi pul dizilimi) deniz kaplumbagasi
photo-ID'sinin standart biyometrik isareti; tum kareyi vermek sinyali
arka plan/deniz dokusu icinde bogar.

Cikti: reid/data/embeddings_<backbone>_<region>.npz
       (embeddings [N, D] float32, image_id, identity, file_name, split_*)
"""

import argparse
import os
import sys

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from PIL import Image
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
from torchvision.models import resnet50, ResNet50_Weights, resnet18, ResNet18_Weights

Image.MAX_IMAGE_PIXELS = None

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_IMAGE_ROOT = os.environ.get(
    'TURTLE_IMAGE_ROOT',
    # SeaTurtleID2022 bu depoda tutulmuyor (8.729 fotograf, ~3 GB).
    # images/ klasorunu iceren dizini TURTLE_IMAGE_ROOT ile gosterin.
    os.path.abspath(os.path.join(HERE, '..', '..', 'turtle_projesi')))


def square_crop_box(x, y, w, h, iw, ih, margin=0.25):
    """bbox'i margin kadar genislet, kareye tamamla, goruntu sinirlarina kirp."""
    cx, cy = x + w / 2.0, y + h / 2.0
    side = max(w, h) * (1.0 + margin)
    side = min(side, min(iw, ih))          # goruntuden buyuk olamaz
    half = side / 2.0
    left = min(max(cx - half, 0), iw - side)
    top = min(max(cy - half, 0), ih - side)
    return (int(round(left)), int(round(top)),
            int(round(left + side)), int(round(top + side)))


class TurtleCropDataset(Dataset):
    """catalog.csv satirlarindan kirpilmis, normalize edilmis tensor uretir."""

    def __init__(self, df, image_root, region='head', size=224, margin=0.25):
        self.df = df.reset_index(drop=True)
        self.image_root = image_root
        self.region = region
        self.margin = margin
        self.tf = transforms.Compose([
            transforms.Resize((size, size)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225]),
        ])

    def __len__(self):
        return len(self.df)

    def _box_for(self, row):
        """Istenen bolge -> yoksa turtle bbox -> o da yoksa tum kare."""
        order = ['head', 'turtle'] if self.region == 'head' else ['turtle', 'head']
        for name in order:
            x, y, w, h = (row[f'{name}_{k}'] for k in ('x', 'y', 'w', 'h'))
            if pd.notna(x) and w > 0 and h > 0:
                return square_crop_box(x, y, w, h, row['width'], row['height'],
                                       self.margin), name
        return (0, 0, int(row['width']), int(row['height'])), 'full'

    def __getitem__(self, i):
        row = self.df.iloc[i]
        path = os.path.join(self.image_root, str(row['file_name']).replace('/', os.sep))
        box, used = self._box_for(row)
        try:
            with Image.open(path) as im:
                im = im.convert('RGB').crop(box)
                tensor = self.tf(im)
            ok = 1
        except Exception:
            tensor = torch.zeros(3, 224, 224)
            ok = 0
        return tensor, int(row['id']), ok


BACKBONES = {
    'resnet50': (resnet50, ResNet50_Weights.IMAGENET1K_V2, 2048),
    'resnet18': (resnet18, ResNet18_Weights.IMAGENET1K_V1, 512),
}


def build_backbone(name, weights_path=None):
    """Gomu uretici govdeyi kur.

    weights_path verilirse reid/train.py'nin ArcFace checkpoint'i yuklenir
    (backbone + BN-neck). Mimari checkpoint'ten okunur, cikarim boyutu da
    oradan gelir. Verilmezse ImageNet on-egitimli govde kullanilir.
    """
    if weights_path:
        if not os.path.exists(weights_path):
            sys.exit(f'HATA: checkpoint yok -> {weights_path}')
        ckpt = torch.load(weights_path, map_location='cpu')
        if 'state_dict' not in ckpt:
            sys.exit(f'HATA: {weights_path} train.py checkpointi degil')

        # Mimari, cikarim servisiyle ayni yerden kurulur ki ikisi ayrismasin.
        sys.path.insert(0, os.path.abspath(
            os.path.join(HERE, '..', 'image-analysis-agent')))
        from src.models.embedding_model import _build_embedding_net

        backbone = ckpt.get('backbone', name)
        dim = int(ckpt.get('embedding_dim', 512))
        model = _build_embedding_net(backbone, dim, torch)
        model.load_state_dict(ckpt['state_dict'], strict=True)
        model.eval()
        print(f'  fine-tuned checkpoint: {backbone}, dim={dim}, '
              f'epoch={ckpt.get("epoch")}, valid_top1={ckpt.get("valid_top1")}')
        return model, dim

    ctor, weights, dim = BACKBONES[name]
    model = ctor(weights=weights)
    model.fc = nn.Identity()          # 2048/512-d global average pool ciktisi
    model.eval()
    return model, dim


@torch.no_grad()
def extract(df, image_root, backbone='resnet50', region='head', batch_size=32,
            workers=8, size=224, margin=0.25, flip_tta=True, weights_path=None,
            device=None):
    model, dim = build_backbone(backbone, weights_path)
    torch.set_grad_enabled(False)
    torch.set_num_threads(max(1, os.cpu_count() or 1))

    device = device or torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = model.to(device)
    use_cuda = device.type == 'cuda'
    print(f'  cihaz: {device}')

    ds = TurtleCropDataset(df, image_root, region=region, size=size, margin=margin)
    dl = DataLoader(ds, batch_size=batch_size, shuffle=False, num_workers=workers,
                    pin_memory=use_cuda)

    feats = np.zeros((len(ds), dim), dtype=np.float32)
    ids = np.zeros(len(ds), dtype=np.int64)
    okflags = np.zeros(len(ds), dtype=np.int8)

    done = 0
    total = len(ds)
    for batch, image_ids, ok in dl:
        batch = batch.to(device, non_blocking=use_cuda)
        out = model(batch)
        if flip_tta:                                    # yatay cevirme ortalamasi
            out = out + model(torch.flip(batch, dims=[3]))
            out = out / 2.0
        out = torch.nn.functional.normalize(out, dim=1)  # kosinus icin L2
        n = out.shape[0]
        feats[done:done + n] = out.float().cpu().numpy()
        ids[done:done + n] = image_ids.numpy()
        okflags[done:done + n] = ok.numpy()
        done += n
        if done % (batch_size * 20) < batch_size or done == total:
            print(f'  {done}/{total} ({100.0 * done / total:.0f}%)', flush=True)

    return feats, ids, okflags


def main():
    ap = argparse.ArgumentParser(description='Kaplumbaga re-ID gomu cikarimi')
    ap.add_argument('--catalog', default=os.path.join(HERE, 'data', 'catalog.csv'))
    ap.add_argument('--image-root', default=DEFAULT_IMAGE_ROOT,
                    help='file_name yollarinin koku (images/ klasorunun ust dizini)')
    ap.add_argument('--backbone', default='resnet50', choices=sorted(BACKBONES))
    ap.add_argument('--region', default='head', choices=['head', 'turtle'])
    ap.add_argument('--batch-size', type=int, default=32)
    ap.add_argument('--workers', type=int, default=8)
    ap.add_argument('--size', type=int, default=224)
    ap.add_argument('--margin', type=float, default=0.25)
    ap.add_argument('--no-flip-tta', action='store_true')
    ap.add_argument('--limit', type=int, default=0, help='hizli deneme icin ilk N satir')
    ap.add_argument('--weights', default='',
                    help='reid/train.py checkpoint yolu (ArcFace fine-tune)')
    ap.add_argument('--out', default='')
    args = ap.parse_args()

    if not os.path.exists(args.catalog):
        sys.exit(f'HATA: {args.catalog} yok. Once prepare_data.py calistirin.')

    df = pd.read_csv(args.catalog)
    if args.limit:
        df = df.head(args.limit)

    probe = os.path.join(args.image_root, str(df.iloc[0]['file_name']).replace('/', os.sep))
    if not os.path.exists(probe):
        sys.exit(f'HATA: goruntu bulunamadi -> {probe}\n--image-root degerini kontrol edin.')

    print(f'Backbone: {args.backbone} | bolge: {args.region} | {len(df)} goruntu')
    feats, ids, okflags = extract(
        df, args.image_root, backbone=args.backbone, region=args.region,
        batch_size=args.batch_size, workers=args.workers, size=args.size,
        margin=args.margin, flip_tta=not args.no_flip_tta,
        weights_path=args.weights or None)

    failed = int((okflags == 0).sum())
    if failed:
        print(f'UYARI: {failed} goruntu okunamadi (sifir vektor olarak isaretlendi)')

    tag = 'arcface' if args.weights else args.backbone
    out = args.out or os.path.join(HERE, 'data', f'embeddings_{tag}_{args.region}.npz')
    cols = {c: df[c].to_numpy() for c in
            ('identity', 'file_name', 'split_closed', 'split_closed_random', 'split_open')
            if c in df.columns}
    np.savez_compressed(out, embeddings=feats, image_id=ids, ok=okflags, **cols)
    print(f'-> {out}  shape={feats.shape}')


if __name__ == '__main__':
    main()
