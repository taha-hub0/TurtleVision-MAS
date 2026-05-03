import sys
import os
import cv2
import json

# Ekleme scripti, src ve data dizinlerine ulasabilmeli
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from src.models.turtle_model import TurtleIdentificationModel
from src.processing.image_processor import ImageProcessor

def add_test_image():
    image_path = r"C:\Users\lenovo\Desktop\x1.png"
    if not os.path.exists(image_path):
        print(f"File not found: {image_path}")
        return

    # Modelleri yukle
    processor = ImageProcessor()
    model = TurtleIdentificationModel()

    # Fotografi oku ve isleme sok
    image = cv2.imread(image_path)
    if image is None:
        print("Failed to read image with cv2.")
        return

    processed_image = processor.preprocess(image)
    
    # Vektoru cikar
    features = model.extract_features(processed_image)
    biometric_vector = features.tolist()

    # Veritabanina kaydet
    db_dir = os.path.join("data", "kaggle_seaturtle")
    os.makedirs(db_dir, exist_ok=True)
    db_path = os.path.join(db_dir, "kaggle_db.json")

    db_records = {}
    if os.path.exists(db_path):
        with open(db_path, "r", encoding="utf-8") as f:
            try:
                db_records = json.load(f)
            except:
                pass

    turtle_id = "TURTLE_X1_TEST"
    db_records[turtle_id] = {
        'turtle_id': turtle_id,
        'species': 'GREEN_TURTLE',
        'biometric_vector': biometric_vector,
        'location': 'Masaustu (x1.png)',
        'first_recorded': '2026-05-02T12:00:00',
        'sightings': 1,
        'quality_score': 0.99
    }

    with open(db_path, "w", encoding="utf-8") as f:
        json.dump(db_records, f, indent=4)
        
    print(f"Successfully added {turtle_id} to {db_path}!")

if __name__ == "__main__":
    add_test_image()
