import os
import json
import logging
import cv2
import glob
from pathlib import Path

logger = logging.getLogger(__name__)

class KaggleDatasetLoader:
    """
    Kaggle SeaTurtleID2022 veri setini indiren ve işleyen modül.
    Gereksinimler: pip install kaggle
    Ve ~/.kaggle/kaggle.json (veya C:\\Users\\<User>\\.kaggle\\kaggle.json) dosyasının ayarlanmış olması gerekir.
    """
    
    def __init__(self, data_dir="data/kaggle_seaturtle"):
        self.dataset_name = "wildlifedatasets/seaturtleid2022"  # Kaggle veri seti ID'si
        self.data_dir = data_dir
        self.images_dir = os.path.join(self.data_dir, "images")
        
    def download_dataset(self):
        """Kaggle API kullanarak veri setini indirir."""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir, exist_ok=True)
            
        logger.info(f"Downloading Kaggle dataset {self.dataset_name}...")
        try:
            # kaggle kütüphanesini dinamik import ediyoruz (yoksa hata fırlatır)
            import kaggle
            kaggle.api.authenticate()
            kaggle.api.dataset_download_files(self.dataset_name, path=self.data_dir, unzip=True)
            logger.info("Download completed successfully.")
        except ImportError:
            logger.error("Kaggle kütüphanesi yüklü değil. Terminalde 'pip install kaggle' komutunu çalıştırın.")
            raise
        except Exception as e:
            logger.error(f"Failed to download dataset: {e}")
            raise
            
    def build_database_from_dataset(self, turtle_model):
        """
        Veri setindeki tüm görüntüleri tarar, ResNet50 modelinden geçirerek
        128D özellik vektörlerini çıkarır ve gerçek veritabanı kayıtlarını oluşturur.
        """
        if not os.path.exists(self.images_dir):
            logger.error("Images directory not found. Please run download_dataset() first.")
            return {}
            
        image_files = glob.glob(os.path.join(self.images_dir, "**", "*.jpg"), recursive=True)
        image_files.extend(glob.glob(os.path.join(self.images_dir, "**", "*.png"), recursive=True))
        
        db_records = {}
        
        logger.info(f"Processing {len(image_files)} images through CNN model...")
        
        for img_path in image_files:
            try:
                # Dosya adından ID çıkarma örneği (örn: green_turtle_001_1.jpg)
                filename = os.path.basename(img_path)
                # Basit kural tabanlı bir ID çıkarma (veri seti formatına göre güncellenmelidir)
                parts = filename.split('_')
                if len(parts) >= 2:
                    turtle_id = f"{parts[0]}_{parts[1]}"
                    species = parts[0].upper()
                else:
                    turtle_id = filename.split('.')[0]
                    species = "UNKNOWN"
                
                # Resmi OpenCV ile oku
                image = cv2.imread(img_path)
                if image is None:
                    continue
                    
                # Modelden geçir ve gerçek 128D vektörü al
                biometric_vector = turtle_model.extract_features(image).tolist()
                
                if turtle_id not in db_records:
                    db_records[turtle_id] = {
                        'turtle_id': turtle_id,
                        'species': species,
                        'biometric_vector': biometric_vector,
                        'location': 'Kaggle SeaTurtleID2022',
                        'first_recorded': '2022-01-01T00:00:00',
                        'sightings': 1,
                        'quality_score': 0.95
                    }
                else:
                    # Daha önce kaydedildiyse sighting sayısını artır
                    db_records[turtle_id]['sightings'] += 1
                    
            except Exception as e:
                logger.warning(f"Error processing image {img_path}: {e}")
                
        logger.info(f"Successfully processed {len(db_records)} unique turtles.")
        
        # JSON olarak kaydet
        save_path = os.path.join(self.data_dir, "kaggle_db.json")
        try:
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(db_records, f, indent=4)
            logger.info(f"Database saved to {save_path}")
        except Exception as e:
            logger.error(f"Error saving database to JSON: {e}")
            
        return db_records

