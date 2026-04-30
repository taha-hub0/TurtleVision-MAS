# Turtle-ID Kurulum Rehberi

## Sistem Gereksinimleri

- **OS**: Windows, macOS, Linux
- **RAM**: Minimum 8GB (önerilen 16GB+)
- **Disk**: 20GB+ (ML modelleri için)
- **GPU**: NVIDIA GPU önerilir (CUDA support)

## Software Gereksinimleri

### 1. Node.js
- [Node.js 16+ indir](https://nodejs.org/)
- Kurulumdan sonra kontrol:
```bash
node --version
npm --version
```

### 2. Python
- [Python 3.9+ indir](https://www.python.org/)
- Kurulumdan sonra kontrol:
```bash
python --version
pip --version
```

### 3. MySQL
- [MySQL 8.0+ indir](https://dev.mysql.com/downloads/mysql/)
- Kurulumdan sonra kontrol:
```bash
mysql --version
```

### 4. Git (İsteğe bağlı)
- [Git indir](https://git-scm.com/)

## Adım Adım Kurulum

### 1. Proje Dosyalarını İndir

```bash
# Git kullanarak
git clone <repository-url> turtle-id-mas
cd turtle-id-mas

# VEYA: Dosyaları manuel olarak indir
```

### 2. MySQL Veritabanını Kur

#### MySQL Server Başlat
```bash
# Windows
net start MySQL80

# macOS
brew services start mysql

# Linux
sudo systemctl start mysql
```

#### Veritabanı Oluştur

```bash
mysql -u root -p

# MySQL prompt'unda:
CREATE DATABASE turtle_id_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'turtle_user'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON turtle_id_db.* TO 'turtle_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

#### Veya otomatik setup:
```bash
mysql -u root -p < database-agent/schema.sql
```

### 3. Backend Kurulumu (Node.js)

```bash
cd backend

# Dependencies yükle
npm install

# .env dosyası oluştur
cp .env.example .env

# .env dosyasını düzenle (proje kökünde)
# Önemli: DATABASE ve PORT ayarlarını kontrol et
```

**.env Ayarları:**
```
PORT=3000
NODE_ENV=development
IMAGE_AGENT_URL=http://localhost:5000
DB_AGENT_URL=http://localhost:5001
DB_HOST=localhost
DB_PORT=3306
DB_USER=turtle_user
DB_PASSWORD=secure_password
DB_NAME=turtle_id_db
```

Backend'i başlat:
```bash
npm run dev
```

✅ Çıktı: `Turtle-ID Coordinator Agent Started Port: 3000`

### 4. Image Analysis Agent Kurulumu (Python)

```bash
cd image-analysis-agent

# Virtual environment oluştur
python -m venv venv

# Virtual environment'i etkinleştir
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Dependencies yükle
pip install -r requirements.txt

# .env dosyası oluştur
cp .env.example .env

# Pre-trained model indir (ilk kez)
# Not: Gerçek modeller ~300MB-1GB olabilir
python -c "
import torch
from torchvision import models
model = models.resnet50(pretrained=True)
torch.save(model.state_dict(), 'src/models/weights/best_model.pt')
print('Model downloaded successfully')
"
```

Agent'ı başlat:
```bash
python app.py
```

✅ Çıktı: `Starting Image Analysis Agent on port 5000`

### 5. Database Agent Kurulumu (Python)

```bash
cd database-agent

# Virtual environment oluştur
python -m venv venv

# Virtual environment'i etkinleştir
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Dependencies yükle
pip install -r requirements.txt

# .env dosyası oluştur
cp .env.example .env

# Database migration'larını çalıştır
python migrate.py
```

Agent'ı başlat:
```bash
python app.py
```

✅ Çıktı: `Starting Database Agent on port 5001`

### 6. Sistem Kontrolü

Tüm agent'lar başladıktan sonra sağlık kontrol:

```bash
curl http://localhost:3000/api/health
```

Beklenen yanıt:
```json
{
  "coordinator": "OK",
  "imageAnalysisAgent": "OK",
  "databaseAgent": "OK",
  "allAgentsHealthy": true,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Kullanarak İlk Test

### 1. Test Görüntüsü Yükle

```bash
# Örnek test scripti oluştur
cat > test_identification.js << 'EOF'
const fs = require('fs');
const axios = require('axios');

async function testIdentification() {
  try {
    // Gerçek görüntü dosyasını base64'e dönüştür
    const imageBuffer = fs.readFileSync('test-image.jpg');
    const imageBase64 = imageBuffer.toString('base64');

    const response = await axios.post(
      'http://localhost:3000/api/identification/identify',
      {
        imageBase64: imageBase64,
        metadata: {
          location: 'Test Beach',
          date: new Date().toISOString().split('T')[0],
          observer: 'Test User'
        }
      }
    );

    console.log('Identification Result:', JSON.stringify(response.data, null, 2));
  } catch (error) {
    console.error('Error:', error.response?.data || error.message);
  }
}

testIdentification();
EOF

node test_identification.js
```

### 2. Veritabanını Kontrol Et

```bash
mysql -u turtle_user -p turtle_id_db

# MySQL prompt'unda:
SHOW TABLES;
DESCRIBE turtles;
SELECT * FROM turtles;
```

## Docker ile Kurulum (Opsiyonel)

### Docker Compose Kullan

```bash
# Proje kökünde docker-compose.yml oluştur
docker-compose up -d

# Logs'u kontrol et
docker-compose logs -f
```

## Sorun Giderme

### 1. MySQL Bağlantısı Başarısız

```bash
# MySQL servisinin çalışıp çalışmadığını kontrol et
mysql -u root -p -e "SELECT 1"

# Bağlantı stringini kontrol et
# .env dosyasında DB_HOST, DB_USER, DB_PASSWORD'ü doğrula
```

### 2. Python Modülleri Bulunamıyor

```bash
# Virtual environment'in aktif olduğundan emin ol
pip install -r requirements.txt

# Spesifik modül yükle
pip install tensorflow opencv-python
```

### 3. Port Zaten Kullanımda

```bash
# Windows: Port kullanımını kontrol et
netstat -ano | findstr :3000

# Linux/macOS:
lsof -i :3000

# Farklı port kullan (.env dosyasında değiştir)
PORT=3001
```

### 4. Model Yükleme Hatası

```bash
# Model dosyasını kontrol et
ls -la image-analysis-agent/src/models/weights/

# Modeli yeniden indir
cd image-analysis-agent
python -c "from src.models.turtle_model import TurtleIdentificationModel"
```

## Performans Optimizasyonu

### GPU Kullanımı (Opsiyonel)

```bash
# CUDA yükle (NVIDIA GPU için)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# GPU'nun çalışıp çalışmadığını kontrol et
python -c "import torch; print(torch.cuda.is_available())"
```

### Memory Ayarları

Python agent'larda:
```python
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '0'  # GPU 0'ı kullan
os.environ['OMP_NUM_THREADS'] = '4'  # CPU thread sayısı
```

## Üretim Dağıtımı

### Geliştirme → Üretim Geçişi

1. **Environment Değişkenleri**
```bash
NODE_ENV=production
DEBUG=false
LOG_LEVEL=info
```

2. **HTTPS Etkinleştir**
```bash
# SSL sertifikası oluştur
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365
```

3. **Nginx Reverse Proxy**
```nginx
upstream coordinator {
  server localhost:3000;
}

server {
  listen 80;
  server_name turtle-id.example.com;
  
  location / {
    proxy_pass http://coordinator;
  }
}
```

4. **Supervisor/PM2 ile Process Yönetimi**
```bash
npm install -g pm2
pm2 start backend/src/index.js --name "turtle-coordinator"
pm2 start image-analysis-agent/app.py --name "turtle-image-agent"
pm2 save
```

## Başka Yardım

Daha fazla bilgi için bakınız:
- [docs/architecture.md](architecture.md)
- [docs/api-spec.md](api-spec.md)
- [README.md](../README.md)

**Sorunlar veya sorular için**: GitHub Issues
