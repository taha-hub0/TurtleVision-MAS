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
    Deniz kaplumbağası tanımlama modeli
    Pre-trained model (ResNet50 feature extractor)
    Kaggle veri seti entegrasyonu için gerçek 128D özellik vektörü üretir.
    """

    def __init__(self, model_path: str = None):
        """
        Model initialization
        
        Args:
            model_path: Pre-trained model weights path
        """
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model_path = model_path
        self.model = None
        
        self._load_model()

    def _load_model(self):
        """
        Model yükleme (ResNet50)
        ResNet50'nin son katmanını 128 boyutlu çıkış verecek şekilde değiştiriyoruz.
        """
        try:
            # Feature extractor (ResNet50)
            self.model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
            
            # Son FC (Fully Connected) katmanını 128 boyutlu vektör üretecek şekilde değiştir
            num_ftrs = self.model.fc.in_features
            self.model.fc = nn.Linear(num_ftrs, 128)
            
            self.model = self.model.to(self.device)
            self.model.eval()
            
            # Görüntü ön işleme (Image preprocessing)
            self.transform = transforms.Compose([
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ])
            
            logger.info(f"Real ResNet50 model initialized for 128D feature extraction on {self.device}")
            
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
            'model_type': 'PyTorch-ResNet50',
            'device': str(self.device),
            'model_path': self.model_path,
            'input_size': (224, 224, 3),
            'output_dimension': 128
        }
