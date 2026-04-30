# Turtle-ID Multi-Agent System - Project Structure

```
turtle-id-mas/
├── README.md                           # Proje açıklaması
├── docker-compose.yml                  # Docker Compose konfigürasyonu
├── start.sh                            # Linux/macOS başlangıç betiği
├── start.bat                           # Windows başlangıç betiği
│
├── backend/                            # 🎯 Koordinatör Agent (Node.js)
│   ├── package.json                    # Dependencies
│   ├── .env.example                    # Environment template
│   ├── Dockerfile                      # Docker image
│   ├── src/
│   │   ├── index.js                    # Main entry point
│   │   ├── services/
│   │   │   └── agentService.js         # Agent communication service
│   │   ├── routes/
│   │   │   ├── health.js               # Health check endpoint
│   │   │   ├── identification.js       # Turtle identification endpoints
│   │   │   └── turtle.js               # Turtle data endpoints
│   │   └── middleware/
│   │       └── (Authentication, validation, etc.)
│   └── logs/                           # Server logs
│
├── image-analysis-agent/               # 🔍 Görüntü Analiz Agent (Python)
│   ├── app.py                          # Flask uygulaması
│   ├── config.py                       # Yapılandırma
│   ├── requirements.txt                # Python dependencies
│   ├── .env.example                    # Environment template
│   ├── Dockerfile                      # Docker image
│   ├── src/
│   │   ├── models/
│   │   │   ├── turtle_model.py         # ML model sınıfı
│   │   │   └── weights/
│   │   │       └── best_model.pt       # Pre-trained model (indir gerekli)
│   │   └── processing/
│   │       └── image_processor.py      # Görüntü işleme
│   └── logs/                           # Agent logs
│
├── database-agent/                     # 💾 Veritabanı Agent (Python)
│   ├── app.py                          # Flask uygulaması
│   ├── config.py                       # Yapılandırma
│   ├── requirements.txt                # Python dependencies
│   ├── .env.example                    # Environment template
│   ├── Dockerfile                      # Docker image
│   ├── migrate.py                      # Database migration scripti
│   ├── src/
│   │   ├── database.py                 # MySQL connection manager
│   │   └── models/
│   │       └── turtle.py               # Turtle data model
│   └── logs/                           # Agent logs
│
└── docs/                               # 📚 Dokümantasyon
    ├── architecture.md                 # Sistem mimarisi
    ├── api-spec.md                     # API spesifikasyonu
    └── setup-guide.md                  # Kurulum rehberi
```

## Bileşen Açıklaması

### Backend (Koordinatör Agent)
- **Rol**: Tüm agent'ları koordine eder, client isteklerini yönlendirir
- **Teknoloji**: Node.js + Express.js
- **Port**: 3000
- **Sorumluluklar**:
  - REST API endpoint'lerini expose eder
  - Agent'lar arasında iletişimi yönetir
  - İstekleri paralel olarak işler
  - Sistem sağlığını izler

### Image Analysis Agent
- **Rol**: Deniz kaplumbağası fotoğraflarını analiz eder
- **Teknoloji**: Python + OpenCV + TensorFlow
- **Port**: 5000
- **Sorumluluklar**:
  - Görüntüleri ön işler (resize, normalize vb.)
  - ML modeli kullanarak kaplumbağa tanımlama yapar
  - Özellik vektörü çıkarır (similarity search için)
  - Güven puanı hesaplar

### Database Agent
- **Rol**: Tüm kaplumbağa verilerini yönetir
- **Teknoloji**: Python + MySQL
- **Port**: 5001
- **Sorumluluklar**:
  - Tanımlanan kaplumbağaları depolar
  - Avistama verilerini kaydeder
  - Benzer kaplumbağaları arar
  - Sorguları işler ve sonuçlar döndürür

## Veri Akışı

```
Client Request
    ↓
Coordinator Agent (validates, routes)
    ↓
┌───────────────────────────────┐
│                               │
Image Analysis Agent   Database Agent
│                               │
└───────────────────────────────┘
    ↓
Coordinator Agent (merges results)
    ↓
Client Response
```

## Kurulum Yöntemleri

### Seçenek 1: Docker Compose (Önerilen)
```bash
docker-compose up -d
```

### Seçenek 2: Manual Kurulum
Bakınız: [docs/setup-guide.md](docs/setup-guide.md)

## API Örnekleri

### 1. Sistem Sağlığını Kontrol Et
```bash
curl http://localhost:3000/api/health
```

### 2. Kaplumbağa Tanımla
```bash
curl -X POST http://localhost:3000/api/identification/identify \
  -H "Content-Type: application/json" \
  -d '{"imageBase64": "...", "metadata": {...}}'
```

### 3. Kaplumbağa Sorgula
```bash
curl http://localhost:3000/api/turtle/turtle_id_123
```

Bakınız: [docs/api-spec.md](docs/api-spec.md)

## Konfigürasyon

Her agent için `.env.example` kopyalanıp `.env` oluşturulmalıdır:

```bash
# Backend
cp backend/.env.example backend/.env

# Image Analysis Agent
cp image-analysis-agent/.env.example image-analysis-agent/.env

# Database Agent
cp database-agent/.env.example database-agent/.env
```

## Sistem Gereksinim Uygulanması

### MAS Mimarı Temel İlkeleri

1. **Özerklik**: Her agent bağımsız olarak çalışır
2. **Heterojenlik**: Farklı teknolojiler kullanılır (Node.js, Python)
3. **Dağıtılılık**: Agent'lar ayrı süreçlerde çalışır
4. **İletişim**: HTTP/REST üzerinden haberleşir
5. **Koordinasyon**: Merkezi koordinatör agent tarafından yönetilir
6. **Güvenilirlik**: Her agent sağlık kontrolü yapılır

### Teknoloji Seçimleri

| İhtiyaç | Teknoloji | Neden? |
|---------|-----------|--------|
| Backend Orkestrasyon | Node.js | Async I/O, hızlı, scalable |
| Görüntü İşleme | Python | ML ecosystem, OpenCV |
| Veritabanı | MySQL | İlişkisel, sorgu desteği |
| Container | Docker | Portability, isolation |
| API | REST | Simple, widely adopted |

## Monitoring ve Logging

- **Koordinatör**: Winston logger
- **Image Agent**: Python logging
- **Database Agent**: Python logging
- **Logs**: `./logs/` dizininde

## Sonraki Adımlar

1. [Kurulum Rehberini Takip Et](docs/setup-guide.md)
2. [Sistem Mimarisini Öğren](docs/architecture.md)
3. [API Spesifikasyonunu Oku](docs/api-spec.md)
4. [İlk Test Yap](#api-örnekleri)

## Lisans

MIT

## İletişim

- **Email**: support@turtle-id.io
- **GitHub**: Issues ve Pull Requests
