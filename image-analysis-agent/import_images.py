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
    
    # Otomatik olarak tüm alt klasörleri bul
    if not os.path.exists(base_dir):
        logger.error(f"Hata: {base_dir} yolu bulunamadı! Lütfen Masaüstünde 'images' klasörü olduğundan emin olun.")
        return

    target_folders = [f for f in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, f))]
    
    if not target_folders:
        logger.warning("Klasör içinde alt klasör bulunamadı. Direkt ana dizindeki resimlere bakılıyor...")
        target_folders = ["."] # Ana dizini de tara
    
    print(f"Yapay Zeka Modeli yükleniyor... ({len(target_folders)} klasör bulundu)")
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
                
                # Benzersiz ve temiz bir ID oluştur
                clean_folder = folder.replace(".", "main").replace(" ", "_")
                turtle_id = f"{clean_folder}_{idx+1:02d}"
                
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
