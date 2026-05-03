import os
import sys
import glob
import cv2
import base64
import requests
import logging

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from src.models.turtle_model import TurtleIdentificationModel
from src.processing.image_processor import ImageProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def import_specific_folders():
    base_dir = r"C:\Users\lenovo\Desktop\images"
    # Sadece t001 ile t011 arasındaki klasör adlarını seç
    target_folders = ["t001", "t002", "t003", "t004", "t006", "t007", "t008", "t009", "t011"]
    
    print("Yapay Zeka Modeli yükleniyor...")
    model = TurtleIdentificationModel()
    processor = ImageProcessor()
    
    total_processed = 0
    
    for folder in target_folders:
        folder_path = os.path.join(base_dir, folder)
        if not os.path.exists(folder_path):
            continue
            
        images = glob.glob(os.path.join(folder_path, "*.[jp][pn]*"))
        logger.info(f"Klasör: {folder} ({len(images)} görsel bulundu)")
        
        for idx, img_path in enumerate(images):
            try:
                # Görüntüyü oku
                img = cv2.imread(img_path)
                if img is None:
                    continue
                
                # ÖNEMLİ: Görüntüyü yapay zekaya uygun hale getir (Preprocess)
                processed_img = processor.preprocess(img)
                
                # 1. Biyometrik vektörü çıkar
                features = model.extract_features(processed_img).tolist()
                
                # 2. Resmi Base64 formatına çevir (Galeriye kaydetmek için)
                with open(img_path, "rb") as f:
                    base64_data = base64.b64encode(f.read()).decode('utf-8')
                
                # Benzersiz bir ID oluştur (Örn: t001_01)
                turtle_id = f"{folder}_{idx+1:02d}"
                
                # 3. API'ye gönder
                payload = {
                    "turtle_id": turtle_id,
                    "biometric_vector": features,
                    "image": base64_data
                }
                
                res = requests.post("http://localhost:5000/api/register", json=payload)
                if res.status_code == 200:
                    logger.info(f"Başarıyla eklendi: {turtle_id}")
                    total_processed += 1
                else:
                    logger.error(f"Hata ({turtle_id}): {res.text}")
                    
            except Exception as e:
                logger.error(f"Görsel işlenirken hata oluştu {img_path}: {e}")
                
    print(f"\nİşlem Tamamlandı! Toplam {total_processed} görsel başarıyla sisteme ve galeriye eklendi.")

if __name__ == "__main__":
    import_specific_folders()
