# Turtle-ID Development Başlangıç Rehberi

## 🎯 Mevcut Sistem Durumu

```
✅ Backend Coordinator (Express.js) - Port 3000
✅ Image Analysis Agent (Python/Flask) - Port 5000
✅ Database Agent (Python/Flask) - Port 5001
✅ SOLID Agents (4 adet):
   ├─ Gatekeeper: Metadata validation
   ├─ Biolytics: Species identification (Strategy Pattern)
   ├─ Matching: Biometric similarity (%90)
   └─ Reporter: DEKAMER-standard reports
```

## 📚 SOLID Mimarı Belgeleri
- [SOLID_AGENTS.md](./docs/SOLID_AGENTS.md) - Tüm 4 ajan detayları
- [DATABASE_SCHEMA.md](./docs/DATABASE_SCHEMA.md) - Tablo yapısı
- [API.md](./docs/API.md) - Tüm endpoint'ler

---

## Hızlı Başlangıç

### Option 1: Docker (Önerilen - 2 dakika)
```bash
cd turtle-id-mas
docker-compose up -d
```

### Option 2: Manual Kurulum (10-15 dakika)

#### 1. Setup Script'i Çalıştır
```bash
# Linux/macOS:
bash setup-dev.sh

# Windows:
setup-dev.bat
```

#### 2. Environment Dosyalarını Yapılandır
Her `.env` dosyasını düzenle

#### 3. MySQL Veritabanını Kur
```bash
# Sadece ilk kez
cd database-agent
python migrate.py
```

#### 4. Tüm Agent'ları Başlat (Ayrı terminallerde)

**Terminal 1 - Koordinatör:**
```bash
cd backend
npm run dev
```

**Terminal 2 - Görüntü Analiz:**
```bash
cd image-analysis-agent
source venv/bin/activate  # Windows: venv\Scripts\activate
python app.py
```

**Terminal 3 - Veritabanı:**
```bash
cd database-agent
source venv/bin/activate  # Windows: venv\Scripts\activate
python app.py
```

## Sistem Kontrol

```bash
# Health check
curl http://localhost:3000/api/health
```

Beklenen çıktı:
```json
{
  "coordinator": "OK",
  "imageAnalysisAgent": "OK", 
  "databaseAgent": "OK",
  "allAgentsHealthy": true
}
```

## Erişim Noktaları

- **API**: http://localhost:3000
- **Image Agent**: http://localhost:5000
- **Database Agent**: http://localhost:5001
- **MySQL**: localhost:3306

## Test Etme

### cURL ile Test
```bash
# API health check
curl http://localhost:3000/api/health

# Tüm kaplumbağaları getir
curl http://localhost:3000/api/turtle
```

### Python/JavaScript ile Test
```bash
# Bkz: docs/ klasöründeki örnekler
```

## Sorun Giderme

### Port Çakışması
```bash
# Hangi process port'u kullanıyor?
lsof -i :3000    # macOS/Linux
netstat -ano | findstr :3000  # Windows
```

### Python Module Hataları
```bash
# Virtual environment'i etkinleştir
source venv/bin/activate
# ve yeniden dene
```

### MySQL Bağlantısı
```bash
# MySQL servisi çalışıyor mu?
mysql -u root -p
```

## Daha Fazla Bilgi

- [Tam Kurulum Rehberi](docs/setup-guide.md)
- [API Spesifikasyonu](docs/api-spec.md)
- [Sistem Mimarisi](docs/architecture.md)
- [Ana README](README.md)

---

**Yaşadığın sorunlar?** → [GitHub Issues](https://github.com/your-repo/issues)
