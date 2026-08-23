import requests
import base64
import json

def check():
    with open(r"C:\Users\lenovo\Desktop\x1.png", "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode('utf-8')
    
    res1 = requests.post("http://localhost:5000/api/analyze", json={"image": img_b64}).json()
    res2 = requests.post("http://localhost:5000/api/analyze", json={"image": img_b64}).json()
    
    f1 = res1.get("features")
    f2 = res2.get("features")
    
    diff = sum([abs(a - b) for a, b in zip(f1, f2)])
    print("Difference between two API calls with same image:", diff)

if __name__ == "__main__":
    check()
