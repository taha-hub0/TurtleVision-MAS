import json
import requests
import base64
import os

def fix():
    img_path = r"C:\Users\lenovo\Desktop\x1.png"
    if not os.path.exists(img_path):
        print("x1.png not found!")
        return

    with open(img_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode('utf-8')
    
    # Sunucuya gönderip gerçek vektörü al
    res = requests.post("http://localhost:5000/api/analyze", json={"image": img_b64})
    if res.status_code != 200:
        print("API error:", res.text)
        return
        
    features = res.json().get('features')
    
    # DB'yi güncelle
    db_path = r"C:\Users\lenovo\Desktop\turtle-id-mas\image-analysis-agent\data\kaggle_seaturtle\kaggle_db.json"
    
    db_records = {}
    db_records["TURTLE_X1_TEST"] = {
        'turtle_id': "TURTLE_X1_TEST",
        'species': 'GREEN_TURTLE',
        'biometric_vector': features,
        'location': 'API Generated',
        'first_recorded': '2026-05-02T12:00:00',
        'sightings': 1,
        'quality_score': 0.99
    }

    with open(db_path, "w", encoding="utf-8") as f:
        json.dump(db_records, f, indent=4)
        
    print("Veritabani sunucu verileriyle senkronize edildi!")

if __name__ == "__main__":
    fix()
