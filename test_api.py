import requests
import base64
import json

def test():
    with open(r"C:\Users\lenovo\Desktop\x1.png", "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode('utf-8')
    
    print("Testing /api/analyze...")
    res = requests.post("http://localhost:5000/api/analyze", json={"image": img_b64})
    print("Status:", res.status_code)
    try:
        print("Response:", json.dumps(res.json(), indent=2))
    except:
        print("Response text:", res.text)
        
    if res.status_code == 200:
        features = res.json().get('features')
        print("Testing /api/match...")
        res2 = requests.post("http://localhost:5000/api/match", json={"biometric_vector": features})
        print("Status:", res2.status_code)
        try:
            print("Response:", json.dumps(res2.json(), indent=2))
        except:
            print("Response text:", res2.text)

if __name__ == "__main__":
    test()
