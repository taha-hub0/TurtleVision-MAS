import os
import cv2
import base64
import numpy as np
from src.models.turtle_model import TurtleIdentificationModel
from src.processing.image_processor import ImageProcessor
from src.matching.turtle_matcher import calculate_cosine_similarity

def test():
    img_path = r"C:\Users\lenovo\Desktop\x1.png"
    
    # 1. Imread pipeline (add_test_turtle.py style)
    processor = ImageProcessor()
    model = TurtleIdentificationModel()
    
    img_read = cv2.imread(img_path)
    proc1 = processor.preprocess(img_read)
    feat1 = model.extract_features(proc1)
    
    # 2. Base64 pipeline (app.py style)
    with open(img_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode('utf-8')
        
    img_data = base64.b64decode(b64)
    nparr = np.frombuffer(img_data, np.uint8)
    img_decode = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    proc2 = processor.preprocess(img_decode)
    feat2 = model.extract_features(proc2)
    
    # Compare raw images
    diff_raw = np.abs(img_read.astype(int) - img_decode.astype(int)).sum()
    print("Raw image diff:", diff_raw)
    
    # Compare preprocessed images
    diff_proc = np.abs(proc1 - proc2).sum()
    print("Processed image diff:", diff_proc)
    
    # Compare features
    diff_feat = np.abs(feat1 - feat2).sum()
    print("Feature diff:", diff_feat)
    
    # Cosine Similarity
    sim = calculate_cosine_similarity(feat1, feat2)
    print("Mapped Cosine Similarity:", sim)

if __name__ == "__main__":
    test()
