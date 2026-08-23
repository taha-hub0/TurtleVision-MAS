import requests
import base64
import sys

def test():
    with open(r"C:\Users\lenovo\Desktop\x1.png", "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode('utf-8')
        
    print("Calling analyze...")
    res = requests.post("http://localhost:5000/api/analyze", json={"image": img_b64})
    if res.status_code != 200:
        print("Analyze failed:", res.text)
        return
        
    features = res.json().get('features')
    print("Features extracted.")
    
    print("Calling register...")
    res2 = requests.post("http://localhost:5000/api/register", json={"biometric_vector": features})
    print("Register Status:", res2.status_code)
    print("Register Response:", res2.text)

if __name__ == "__main__":
    test()
