"""
Adim 5.2 - ArcFace ile metrik ogrenme

ImageNet on-egitimli oznitelikler birey ayirt etmede yetersiz kaldi
(top-1 %4.6; ayni birey 0.742 / farkli birey 0.670, Cohen d = 0.33).
Beklenen bir sonuc: ImageNet siniflari "kaplumbaga"yi ayirmayi ogretir,
"su kaplumbagasi"yi degil. Ayirt edici sinyal bireysel pul deseninde ve
o desen ImageNet kayibinda hicbir gradyan almiyor.

ArcFace, siniflandirma kaybini acisal marj ile duzenler: ayni bireyin
gomulerini bir yone toplar, farkli bireyleri en az `m` radyan iter.
Cikti dogrudan kosinus ile karsilastirilabilir - bu boru hattinin
ihtiyaci olan sey.

Bolunme disiplini: yalnizca split_closed == 'train' egitimde kullanilir.
'valid' erken durdurma icin, 'test' hic dokunulmadan evaluate.py'ye kalir.
"""

import argparse
import json
import math
import os
import time

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
from torchvision.models import (ResNet18_Weights, ResNet50_Weights, resnet18,
                                resnet50)

HERE = os.path.dirname(os.path.abspath(__file__))

BACKBONES = {
    'resnet18': (resnet18, ResNet18_Weights.IMAGENET1K_V1, 512),
    'resnet50': (resnet50, ResNet50_Weights.IMAGENET1K_V2, 2048),
}

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


# --------------------------------------------------------------------------- #
# Veri
# --------------------------------------------------------------------------- #

class CropDataset(Dataset):
    """Onbellekteki kafa kirpmalarini okur (cache_crops.py ciktisi)."""

    def __init__(self, df, crop_dir, label_map, size=224, train=True,
                 profile='head'):
        """
        profile: on isleme profili. Egitim ile CIKARIM ayni profili kullanmali,
        aksi halde model ogrendiginden farkli bir goruntu dagilimiyla
        karsilasir ve kazanc buyuk olcude kaybolur.

          'head' - onbellekteki kare kafa kirpmasi dogrudan `size`'a olceklenir.
                   reid/embed.py --region head ile eslesir.
          'full' - tum kare; dogrulama/cikarim yolu Resize(size*256/224) ->
                   CenterCrop(size), yani image-analysis-agent'in
                   turtle_model.extract_features yolunun aynisi.
        """
        self.df = df.reset_index(drop=True)
        self.crop_dir = crop_dir
        self.label_map = label_map
        self.profile = profile

        renk = transforms.ColorJitter(brightness=0.25, contrast=0.25,
                                      saturation=0.25, hue=0.03)
        son = [transforms.ToTensor(),
               transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD)]

        if profile == 'full':
            kisa_kenar = int(round(size * 256 / 224))     # 224 -> 256
            if train:
                # CenterCrop'un gorecegi bolgeye yakin ama jitterli kirpma
                self.tf = transforms.Compose([
                    transforms.RandomResizedCrop(size, scale=(0.55, 1.0),
                                                 ratio=(0.85, 1.18)),
                    transforms.RandomHorizontalFlip(),
                    renk,
                    *son,
                    transforms.RandomErasing(p=0.25, scale=(0.02, 0.15)),
                ])
            else:
                # Cikarimla birebir ayni
                self.tf = transforms.Compose([
                    transforms.Resize(kisa_kenar),
                    transforms.CenterCrop(size),
                    *son,
                ])
        else:
            if train:
                self.tf = transforms.Compose([
                    transforms.RandomResizedCrop(size, scale=(0.7, 1.0),
                                                 ratio=(0.9, 1.11)),
                    transforms.RandomHorizontalFlip(),
                    renk,
                    *son,
                    transforms.RandomErasing(p=0.25, scale=(0.02, 0.15)),
                ])
            else:
                self.tf = transforms.Compose([
                    transforms.Resize((size, size)),
                    *son,
                ])

    def __len__(self):
        return len(self.df)

    def __getitem__(self, i):
        row = self.df.iloc[i]
        path = os.path.join(self.crop_dir, f"{int(row['id'])}.jpg")
        with Image.open(path) as im:
            tensor = self.tf(im.convert('RGB'))
        return tensor, self.label_map[row['identity']]


# --------------------------------------------------------------------------- #
# Model
# --------------------------------------------------------------------------- #

class ArcMarginProduct(nn.Module):
    """ArcFace basligi: kosinus + acisal marj.

    Yalnizca egitimde kullanilir; cikarimda gomu dogrudan backbone'dan alinir.
    """

    def __init__(self, in_features, out_features, scale=30.0, margin=0.30):
        super().__init__()
        self.weight = nn.Parameter(torch.empty(out_features, in_features))
        nn.init.xavier_normal_(self.weight)
        self.scale = scale
        self.margin = margin
        self.cos_m = math.cos(margin)
        self.sin_m = math.sin(margin)
        # theta + m > pi oldugunda kosinus artik monoton degil; o bolgede
        # duzeltilmis (dogrusal) dala geciyoruz - ArcFace makalesindeki easy_margin
        # olmayan kurulum.
        self.th = math.cos(math.pi - margin)
        self.mm = math.sin(math.pi - margin) * margin

    def forward(self, features, labels):
        cosine = F.linear(F.normalize(features), F.normalize(self.weight))
        cosine = cosine.clamp(-1 + 1e-7, 1 - 1e-7)
        sine = torch.sqrt(1.0 - cosine.pow(2))
        phi = cosine * self.cos_m - sine * self.sin_m
        phi = torch.where(cosine > self.th, phi, cosine - self.mm)

        one_hot = torch.zeros_like(cosine)
        one_hot.scatter_(1, labels.view(-1, 1), 1.0)
        output = one_hot * phi + (1.0 - one_hot) * cosine
        return output * self.scale


class EmbeddingNet(nn.Module):
    def __init__(self, backbone='resnet18', embedding_dim=512, dropout=0.2):
        super().__init__()
        ctor, weights, feat_dim = BACKBONES[backbone]
        net = ctor(weights=weights)
        net.fc = nn.Identity()
        self.backbone = net
        self.backbone_name = backbone
        # BN-neck: siniflandirma kaybi ile metrik uzayi arasinda tampon
        self.neck = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(feat_dim, embedding_dim),
            nn.BatchNorm1d(embedding_dim),
        )
        self.embedding_dim = embedding_dim

    def forward(self, x):
        return self.neck(self.backbone(x))


# --------------------------------------------------------------------------- #
# Degerlendirme (valid uzerinde, egitim sirasinda)
# --------------------------------------------------------------------------- #

@torch.no_grad()
def embed_split(model, df, crop_dir, size, batch_size, workers, device,
                profile='head'):
    model.eval()
    ds = CropDataset(df, crop_dir, {i: 0 for i in df['identity'].unique()},
                     size=size, train=False, profile=profile)
    use_cuda = device.type == 'cuda'
    dl = DataLoader(ds, batch_size=batch_size, shuffle=False, num_workers=workers,
                    pin_memory=use_cuda)
    out = []
    for batch, _ in dl:
        emb = model(batch.to(device, non_blocking=use_cuda))
        out.append(F.normalize(emb, dim=1).float().cpu().numpy())
    return np.vstack(out).astype(np.float32)


def rank1_map(gallery, g_ident, query, q_ident):
    """Kapali-set top-1 ve mAP. Galeride karsiligi olmayan sorgular atlanir."""
    known = np.isin(q_ident, np.unique(g_ident))
    query, q_ident = query[known], q_ident[known]
    if len(query) == 0:
        return 0.0, 0.0
    sims = query @ gallery.T
    order = np.argsort(-sims, axis=1)
    hits = g_ident[order] == q_ident[:, None]
    top1 = float(hits[:, 0].mean())
    aps = []
    for i in range(hits.shape[0]):
        idx = np.flatnonzero(hits[i])
        if idx.size == 0:
            aps.append(0.0)
            continue
        aps.append(float(((np.arange(idx.size) + 1) / (idx + 1)).mean()))
    return top1, float(np.mean(aps))


# --------------------------------------------------------------------------- #

def main():
    ap = argparse.ArgumentParser(description='ArcFace ile kaplumbaga re-ID egitimi')
    ap.add_argument('--catalog', default=os.path.join(HERE, 'data', 'catalog.csv'))
    ap.add_argument('--crop-dir', default=os.path.join(HERE, 'data', 'crops'))
    ap.add_argument('--profile', default='head', choices=['head', 'full'],
                    help='on isleme profili; cikarim tarafiyla AYNI olmali')
    ap.add_argument('--split', default='split_closed')
    ap.add_argument('--backbone', default='resnet18', choices=sorted(BACKBONES))
    ap.add_argument('--embedding-dim', type=int, default=512)
    ap.add_argument('--size', type=int, default=224)
    ap.add_argument('--epochs', type=int, default=15)
    ap.add_argument('--batch-size', type=int, default=48)
    ap.add_argument('--lr', type=float, default=3e-4)
    ap.add_argument('--head-lr', type=float, default=3e-3)
    ap.add_argument('--weight-decay', type=float, default=5e-4)
    ap.add_argument('--margin', type=float, default=0.30)
    ap.add_argument('--scale', type=float, default=30.0)
    ap.add_argument('--workers', type=int, default=6)
    ap.add_argument('--threads', type=int, default=max(1, (os.cpu_count() or 8) - 2))
    ap.add_argument('--eval-every', type=int, default=1)
    ap.add_argument('--out', default=os.path.join(HERE, 'data', 'arcface_best.pt'))
    args = ap.parse_args()

    torch.set_num_threads(args.threads)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    df = pd.read_csv(args.catalog)
    if not os.path.isdir(args.crop_dir):
        raise SystemExit(f'Kirpma onbellegi yok: {args.crop_dir}\n'
                         'Once cache_crops.py calistirin.')

    train_df = df[df[args.split] == 'train'].copy()
    valid_df = df[df[args.split] == 'valid'].copy()

    # ArcFace her sinif icin agirlik vektoru ogrenir; tek fotografli bireyler
    # egitimde sinyal veremez ama sinif sayisini sisirir. Yine de birakiyoruz:
    # sinif sayisi 438 ve tek ornekli bireyler negatif ornek olarak isleve sahip.
    identities = sorted(train_df['identity'].unique())
    label_map = {ident: i for i, ident in enumerate(identities)}

    print(f'backbone={args.backbone} size={args.size} dim={args.embedding_dim} '
          f'profile={args.profile}')
    print(f'egitim {len(train_df)} foto / {len(identities)} birey | '
          f'dogrulama {len(valid_df)} foto')
    print(f'threads={args.threads} workers={args.workers} device={device}')

    use_cuda = device.type == 'cuda'
    train_ds = CropDataset(train_df, args.crop_dir, label_map,
                           size=args.size, train=True, profile=args.profile)
    train_dl = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True,
                          num_workers=args.workers, drop_last=True,
                          pin_memory=use_cuda, persistent_workers=args.workers > 0)

    model = EmbeddingNet(args.backbone, args.embedding_dim).to(device)
    head = ArcMarginProduct(args.embedding_dim, len(identities),
                            scale=args.scale, margin=args.margin).to(device)
    criterion = nn.CrossEntropyLoss(label_smoothing=0.1)

    optimizer = torch.optim.AdamW([
        {'params': model.backbone.parameters(), 'lr': args.lr},
        {'params': model.neck.parameters(), 'lr': args.head_lr},
        {'params': head.parameters(), 'lr': args.head_lr},
    ], weight_decay=args.weight_decay)
    scaler = torch.amp.GradScaler(device.type, enabled=use_cuda)
    scheduler = torch.optim.lr_scheduler.OneCycleLR(
        optimizer, max_lr=[args.lr, args.head_lr, args.head_lr],
        total_steps=args.epochs * max(1, len(train_dl)), pct_start=0.25)

    # Dogrulama icin galeri = train (augmentasyonsuz), sorgu = valid
    gal_ident = train_df['identity'].to_numpy()
    val_ident = valid_df['identity'].to_numpy()

    best = {'top1': -1.0, 'epoch': -1}
    history = []

    for epoch in range(1, args.epochs + 1):
        model.train()
        head.train()
        t0 = time.time()
        total, correct, loss_sum = 0, 0, 0.0

        for step, (batch, labels) in enumerate(train_dl, 1):
            batch = batch.to(device, non_blocking=use_cuda)
            labels = labels.to(device, non_blocking=use_cuda)
            optimizer.zero_grad(set_to_none=True)

            # ArcFace'in acisal aritmetigi (acos/cos yakininda sinir degerler)
            # fp16'da hassasiyet kaybeder; ileri gecis autocast altinda,
            # kayip hesabi fp32'de kalir.
            with torch.autocast(device_type=device.type, enabled=use_cuda):
                emb = model(batch)
            logits = head(emb.float(), labels)
            loss = criterion(logits, labels)

            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(
                list(model.parameters()) + list(head.parameters()), 5.0)
            scaler.step(optimizer)
            scaler.update()
            scheduler.step()

            loss_sum += loss.item() * labels.size(0)
            correct += (logits.argmax(1) == labels).sum().item()
            total += labels.size(0)

            if step % 20 == 0:
                rate = total / (time.time() - t0)
                print(f'  e{epoch} adim {step}/{len(train_dl)} '
                      f'loss={loss_sum/total:.3f} acc={correct/total:.3f} '
                      f'({rate:.1f} foto/s)', flush=True)

        entry = {'epoch': epoch, 'loss': loss_sum / max(total, 1),
                 'train_acc': correct / max(total, 1),
                 'seconds': round(time.time() - t0, 1)}

        if epoch % args.eval_every == 0 or epoch == args.epochs:
            gal = embed_split(model, train_df, args.crop_dir, args.size,
                              args.batch_size, args.workers, device, args.profile)
            val = embed_split(model, valid_df, args.crop_dir, args.size,
                              args.batch_size, args.workers, device, args.profile)
            top1, mAP = rank1_map(gal, gal_ident, val, val_ident)
            entry.update(valid_top1=top1, valid_mAP=mAP)

            if top1 > best['top1']:
                best = {'top1': top1, 'mAP': mAP, 'epoch': epoch}
                torch.save({
                    'state_dict': model.state_dict(),
                    'backbone': args.backbone,
                    'embedding_dim': args.embedding_dim,
                    'size': args.size,
                    'profile': args.profile,
                    'identities': identities,
                    'valid_top1': top1,
                    'valid_mAP': mAP,
                    'epoch': epoch,
                }, args.out)
                entry['saved'] = True

        history.append(entry)
        print(f'epoch {epoch}/{args.epochs} loss={entry["loss"]:.3f} '
              f'acc={entry["train_acc"]:.3f} '
              f'valid_top1={entry.get("valid_top1", float("nan")):.4f} '
              f'valid_mAP={entry.get("valid_mAP", float("nan")):.4f} '
              f'({entry["seconds"]:.0f}s)'
              f'{"  <- kaydedildi" if entry.get("saved") else ""}', flush=True)

        with open(os.path.splitext(args.out)[0] + '_history.json', 'w') as f:
            json.dump({'args': vars(args), 'history': history, 'best': best}, f, indent=2)

    print(f'\nEn iyi: epoch {best["epoch"]} valid_top1={best["top1"]:.4f}')
    print(f'-> {args.out}')


if __name__ == '__main__':
    main()
