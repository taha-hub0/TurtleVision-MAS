import sys
import os
import logging

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from src.data.kaggle_loader import KaggleDatasetLoader
from src.models.turtle_model import TurtleIdentificationModel

logging.basicConfig(level=logging.INFO)

def main():
    print("=== KAGGLE DATASET INDIRME VE ISLEME ===")
    print("Bu islem internet hizina bagli olarak birkac GB indirme yapacak,")
    print("Ardindan tum fotograflari ResNet50'den gecirecektir. (1-2 saat surebilir)")
    print("Devam etmek icin lutfen bekleyin...\n")
    
    # 1. Modeli Yukle
    print("Yapay zeka modeli yukleniyor...")
    model = TurtleIdentificationModel()
    
    # 2. Loader'i Yukle
    loader = KaggleDatasetLoader(data_dir="data/kaggle_seaturtle")
    
    # 3. Indirme Islemi
    try:
        print("\nVeri seti indiriliyor... (Lutfen bekleyin, yuzdelik dilimi goreceksiniz)")
        loader.download_dataset()
    except Exception as e:
        print(f"\n[HATA] Indirme sirasinda bir sorun olustu: {e}")
        print("Lutfen C:\\Users\\lenovo\\.kaggle\\kaggle.json dosyanizin var oldugundan emin olun.")
        return
        
    # 4. Ozellik Cikarma ve Veritabani Olusturma
    print("\nIndirme tamamlandi. Simdi fotograflardan Biyometrik Vektorler cikariliyor...")
    print("Bu islem bilgisayarinizin gucune gore cok uzun surebilir.")
    loader.build_database_from_dataset(model)
    
    print("\n=== ISLEM BASARIYLA TAMAMLANDI! ===")
    print("Tum Kaggle kaplumbagalari kaggle_db.json dosyasina eklendi.")
    print("Lutfen islemi bitirdikten sonra ana Python sunucusunu yeniden baslatmayi unutmayin.")

if __name__ == "__main__":
    main()
