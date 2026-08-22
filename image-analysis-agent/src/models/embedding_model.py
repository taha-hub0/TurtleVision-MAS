"""
TurtleEmbedder - gercek biyometrik gomu uretici

Bu sinif, `turtle_model.TurtleIdentificationModel`in yerini alir:
eskisi np.random.randn(512) donduruyordu, yani her cagrida farkli bir vektor.
Burada pretrained bir CNN backbone ile deterministik, L2-normalize edilmis
oznitelik vektoru uretilir; iki foto arasindaki kosinus benzerligi dogrudan
"ayni birey mi" sorusuna karsilik gelir.

Kirpma bolgesi kafadir (post-ocular scutes). Bir kafa bbox'i verilirse o
kullanilir; verilmezse tum kare islenir ve dogruluk ciddi olcude duser
(SeaTurtleID2022'de kafa, karenin medyanda %1.3'u).

Offline degerlendirme icin: reid/evaluate.py
"""

import logging
import os
import threading
from typing import Dict, Optional, Sequence

import numpy as np

logger = logging.getLogger(__name__)

IMAGENET_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
IMAGENET_STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)

BACKBONE_DIMS = {'resnet50': 2048, 'resnet18': 512}


def square_crop_box(x, y, w, h, iw, ih, margin=0.25):
    """bbox'i margin kadar genislet, kareye tamamla, goruntu sinirlarina kirp.

    reid/embed.py ile ayni geometri - offline galeri ile online sorgu
    ayni on islemeden gecmezse kosinus benzerligi anlamsizlasir.
    """
    cx, cy = x + w / 2.0, y + h / 2.0
    side = max(w, h) * (1.0 + margin)
    side = min(side, min(iw, ih))
    half = side / 2.0
    left = min(max(cx - half, 0), iw - side)
    top = min(max(cy - half, 0), ih - side)
    return (int(round(left)), int(round(top)),
            int(round(left + side)), int(round(top + side)))


def _build_backbone_only(backbone, torch):
    """ImageNet on-egitimli govde, siniflandirma katmani cikarilmis."""
    import torch.nn as nn
    from torchvision import models

    if backbone == 'resnet50':
        net = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V2)
    else:
        net = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
    net.fc = nn.Identity()
    return net


def _build_embedding_net(backbone, embedding_dim, torch):
    """reid/train.py'deki EmbeddingNet ile AYNI mimari.

    Ikisi birlikte degismelidir; uyusmazlik durumunda load_state_dict
    strict=True ile hata verir (sessiz yanlis gomu uretmez).
    """
    import torch.nn as nn

    body = _build_backbone_only(backbone, torch)
    feat_dim = BACKBONE_DIMS[backbone]

    class EmbeddingNet(nn.Module):
        def __init__(self):
            super().__init__()
            self.backbone = body
            self.neck = nn.Sequential(
                nn.Dropout(0.2),
                nn.Linear(feat_dim, embedding_dim),
                nn.BatchNorm1d(embedding_dim),
            )

        def forward(self, x):
            return self.neck(self.backbone(x))

    return EmbeddingNet()


class TurtleEmbedder:
    """Tek goruntuden biyometrik gomu cikarir (thread-safe)."""

    def __init__(self, backbone: str = 'resnet50', size: int = 224,
                 margin: float = 0.25, flip_tta: bool = True,
                 weights_path: Optional[str] = None):
        if backbone not in BACKBONE_DIMS:
            raise ValueError(f'Bilinmeyen backbone: {backbone}')

        self.backbone_name = backbone
        self.size = size
        self.margin = margin
        self.flip_tta = flip_tta
        self.weights_path = weights_path
        self._lock = threading.Lock()

        import torch

        self._torch = torch
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        checkpoint = None
        if weights_path and os.path.exists(weights_path):
            checkpoint = torch.load(weights_path, map_location='cpu')
        elif weights_path:
            logger.warning('weights_path bulunamadi, ImageNet agirliklari '
                           'kullaniliyor: %s', weights_path)

        if checkpoint is not None and 'state_dict' in checkpoint:
            # reid/train.py ciktisi: backbone + BN-neck, ArcFace ile egitilmis.
            # Mimari ve girdi boyutu checkpoint'ten okunur; egitimde ne
            # kullanildiysa cikarimda da o kullanilmali.
            self.backbone_name = checkpoint.get('backbone', backbone)
            self.dim = int(checkpoint.get('embedding_dim', 512))
            self.size = int(checkpoint.get('size', size))
            net = _build_embedding_net(self.backbone_name, self.dim, torch)
            # strict=True: mimari ile checkpoint uyusmazsa sessizce yanlis
            # gomu uretmektense hemen hata versin.
            net.load_state_dict(checkpoint['state_dict'], strict=True)
            self.fine_tuned = True
            logger.info('Fine-tuned model yuklendi: %s (epoch %s, valid_top1=%s)',
                        weights_path, checkpoint.get('epoch'),
                        checkpoint.get('valid_top1'))
        else:
            self.backbone_name = backbone
            self.dim = BACKBONE_DIMS[backbone]
            net = _build_backbone_only(backbone, torch)
            if checkpoint is not None:
                net.load_state_dict(checkpoint, strict=False)
            self.fine_tuned = False

        net.eval().to(self.device)
        self.net = net
        logger.info('TurtleEmbedder hazir: %s, dim=%d, fine_tuned=%s, device=%s',
                    self.backbone_name, self.dim, self.fine_tuned, self.device)

    # ------------------------------------------------------------------ #

    def _preprocess(self, image_bgr: np.ndarray, box: Optional[Sequence[float]]):
        """BGR uint8 -> normalize edilmis [1, 3, H, W] tensor.

        Yeniden boyutlandirma PIL ile yapilir, cv2 ile DEGIL: cv2.INTER_LINEAR
        kucultmede antialias uygulamadigi icin ayni kirpmadan PIL'e gore
        ~0.95 kosinusluk farkli bir gomu cikariyor. Galeri (reid/embed.py)
        PIL kullaniyor; ikisi ayni olmazsa benzerlik esigi anlamsizlasir.
        """
        from PIL import Image

        ih, iw = image_bgr.shape[:2]
        if box is not None and len(box) == 4 and box[2] > 0 and box[3] > 0:
            x1, y1, x2, y2 = square_crop_box(*box, iw=iw, ih=ih, margin=self.margin)
            image_bgr = image_bgr[y1:y2, x1:x2]

        if image_bgr.size == 0:
            raise ValueError('Kirpma bos goruntu uretti')

        pil = Image.fromarray(image_bgr[:, :, ::-1])          # BGR -> RGB
        pil = pil.resize((self.size, self.size), Image.BILINEAR, reducing_gap=None)
        arr = np.asarray(pil, dtype=np.float32) / 255.0
        arr = (arr - IMAGENET_MEAN) / IMAGENET_STD
        arr = np.transpose(arr, (2, 0, 1))[None]
        return self._torch.from_numpy(np.ascontiguousarray(arr))

    def embed(self, image_bgr: np.ndarray,
              box: Optional[Sequence[float]] = None) -> np.ndarray:
        """Goruntuden L2-normalize gomu dondur. box = [x, y, w, h] (kafa)."""
        torch = self._torch
        tensor = self._preprocess(image_bgr, box).to(self.device)

        with self._lock, torch.no_grad():
            out = self.net(tensor)
            if self.flip_tta:
                out = (out + self.net(torch.flip(tensor, dims=[3]))) / 2.0
            out = torch.nn.functional.normalize(out, dim=1)

        return out.cpu().numpy()[0].astype(np.float32)

    @staticmethod
    def similarity(a: np.ndarray, b: np.ndarray) -> float:
        """Iki L2-normalize gomu arasi kosinus benzerligi [-1, 1]."""
        a = np.asarray(a, dtype=np.float32).ravel()
        b = np.asarray(b, dtype=np.float32).ravel()
        if a.shape != b.shape or a.size == 0:
            return 0.0
        na, nb = np.linalg.norm(a), np.linalg.norm(b)
        if na == 0 or nb == 0:
            return 0.0
        return float(np.dot(a, b) / (na * nb))

    def info(self) -> Dict:
        return {
            'backbone': self.backbone_name,
            'embedding_dim': self.dim,
            'input_size': self.size,
            'crop_margin': self.margin,
            'flip_tta': self.flip_tta,
            'device': str(self.device),
            'fine_tuned': self.fine_tuned,
        }
