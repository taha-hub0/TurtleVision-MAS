import os

import numpy as np
import cv2
import torch
import torchvision.models as models
import torch.nn as nn
from torchvision import transforms
from PIL import Image
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class TurtleIdentificationModel:
    """
    Deniz kaplumbağası tanımlama modeli — biyometrik gömü üretici.

    ÖNEMLİ DÜZELTME
    ---------------
    Önceki sürüm ResNet50'nin son katmanını `nn.Linear(2048, 128)` ile
    değiştiriyordu. Bu katman rastgele ilklenip **hiç eğitilmiyor ve diske
    kaydedilmiyordu**, dolayısıyla her süreç başlangıcında yeni bir rastgele
    projeksiyon oluşuyordu.

    Sonuç: aynı fotoğraf, ajan yeniden başlatıldıktan sonra tamamen farklı
    bir vektör veriyordu (ölçüldü: kosinüs benzerliği **-0.1377**, olması
    gereken 1.0). Yani `kaggle_db.json` içindeki 709 kayıtlı vektör, ajan
    her yeniden başladığında sessizce geçersizleşiyor ve eşleştirme çalışıyor
    gibi görünüp anlamsız sonuç üretiyordu.

    `check_deterministic.py` bunu yakalayamıyordu çünkü yalnızca *aynı süreç
    içindeki* iki çağrıyı karşılaştırıyor; o test her zaman geçer. Süreçler
    arası regresyon testi: `image-analysis-agent/tests/test_determinism.py`.

    Şimdiki davranış
    ----------------
    - `model_path` eğitilmiş bir ArcFace checkpoint'i gösteriyorsa o yüklenir
      (bkz. `reid/train.py`); gömü boyutu checkpoint'ten okunur.
    - Göstermiyorsa ImageNet ResNet50'nin havuzlanmış 2048-d çıktısı
      kullanılır: eğitilmemiş ama **deterministik** — süreçler arası tutarlı.

    Her iki durumda da rastgele, eğitilmemiş bir katman devrede değildir.
    """

    def __init__(self, model_path: str = None):
        """
        Model initialization

        Args:
            model_path: reid/train.py'nin ürettiği ArcFace checkpoint yolu.
                        Yoksa ImageNet gövdesine düşülür.
        """
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model_path = model_path
        self.model = None
        self.embedding_dim = None
        self.fine_tuned = False

        self._load_model()

    def _load_model(self):
        """
        Model yükleme.

        Eğitilmiş checkpoint varsa o; yoksa ImageNet ResNet50'nin havuzlanmış
        çıktısı. Rastgele ilklenmiş bir katman HİÇBİR durumda kullanılmaz —
        sınıfın docstring'indeki gerekçeye bakın.
        """
        try:
            checkpoint = None
            if self.model_path and os.path.exists(self.model_path):
                checkpoint = torch.load(self.model_path, map_location='cpu')
            elif self.model_path:
                logger.warning(
                    "model_path bulunamadi (%s); ImageNet govdesine dusuluyor. "
                    "Birey ayirt etme dogrulugu dusuktur - bkz. reid/README.md",
                    self.model_path)

            if checkpoint is not None and 'state_dict' in checkpoint:
                # reid/train.py ciktisi: ResNet govdesi + BN-neck, ArcFace ile egitilmis
                from .embedding_model import _build_embedding_net

                backbone = checkpoint.get('backbone', 'resnet18')
                self.embedding_dim = int(checkpoint.get('embedding_dim', 512))
                self.model = _build_embedding_net(backbone, self.embedding_dim, torch)
                # strict=True: mimari uyusmazsa sessizce yanlis gomu uretmek yerine hata ver
                self.model.load_state_dict(checkpoint['state_dict'], strict=True)
                self.fine_tuned = True
                self.backbone_name = backbone
                logger.info("Fine-tuned model yuklendi: %s (epoch %s, valid_top1=%s)",
                            self.model_path, checkpoint.get('epoch'),
                            checkpoint.get('valid_top1'))
            else:
                # nn.Linear(2048, 128) DEGIL: o katman egitilmemis ve her
                # baslangicta farkli olurdu. nn.Identity deterministiktir.
                self.model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
                self.model.fc = nn.Identity()
                self.embedding_dim = 2048
                self.fine_tuned = False
                self.backbone_name = 'resnet50'
                logger.info("ImageNet ResNet50 govdesi (2048-d, egitilmemis ama "
                            "deterministik) on %s", self.device)

            self.model = self.model.to(self.device)
            self.model.eval()

            # Görüntü ön işleme (Image preprocessing)
            self.transform = transforms.Compose([
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ])

            logger.info("Gomu boyutu: %d | fine_tuned: %s",
                        self.embedding_dim, self.fine_tuned)

        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise

    def identify_turtle(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Görüntüdeki kaplumbağayı tanımla
        
        Args:
            image: Processed image (numpy array)
            
        Returns:
            Dictionary with identification results
        """
        try:
            features = self.extract_features(image)
            # Normalde bu özellik vektörü veritabanındaki kayıtlarla karşılaştırılır
            # (turtle_matcher.py tarafından yapılıyor)
            
            result = {
                'biometric_vector': features.tolist(),
                'status': 'features_extracted_successfully',
                'dimension': len(features)
            }
            return result
            
        except Exception as e:
            logger.error(f"Error during identification: {e}")
            raise

    def extract_features(self, image: np.ndarray) -> np.ndarray:
        """
        Görüntüden gerçek 128D özellik vektörü çıkar (benzerlik araması için)
        
        Args:
            image: Processed image (OpenCV BGR format)
            
        Returns:
            Feature vector (numpy array - 128D)
        """
        try:
            # OpenCV BGR -> RGB formatına çevir
            if len(image.shape) == 3 and image.shape[2] == 3:
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                image_rgb = image
                
            # PIL Image float32 RGB desteklemediği için uint8'e dönüştür
            if image_rgb.dtype == np.float32 or image_rgb.dtype == np.float64:
                if image_rgb.max() <= 1.0:
                    image_rgb = (image_rgb * 255).astype(np.uint8)
                else:
                    image_rgb = image_rgb.astype(np.uint8)
                    
            pil_image = Image.fromarray(image_rgb)
            
            # Tensor'a dönüştür ve batch dimension ekle
            input_tensor = self.transform(pil_image).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                features = self.model(input_tensor)
                
            # Cosine similarity için vektörü L2 normalize et
            features = torch.nn.functional.normalize(features, p=2, dim=1)
            
            return features.cpu().numpy().flatten()
            
        except Exception as e:
            logger.error(f"Error extracting features: {e}")
            raise

    def batch_identify(self, images: list) -> list:
        """
        Batch tanımlama
        
        Args:
            images: List of images
            
        Returns:
            List of results
        """
        results = []
        for image in images:
            try:
                result = self.identify_turtle(image)
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing image: {e}")
                results.append({'error': str(e)})
        
        return results

    def get_model_info(self) -> Dict[str, Any]:
        """Model bilgisini döndür"""
        return {
            'model_type': f'PyTorch-{getattr(self, "backbone_name", "resnet50")}',
            'device': str(self.device),
            'model_path': self.model_path,
            'input_size': (224, 224, 3),
            # Sabit 128 degil: boyut yuklenen modele gore degisir
            # (fine-tuned checkpoint -> checkpoint'teki deger, aksi halde 2048)
            'output_dimension': self.embedding_dim,
            'fine_tuned': self.fine_tuned,
        }
