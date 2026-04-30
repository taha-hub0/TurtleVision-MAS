# Turtle-ID MAS - Geliştirme Rehberi

## Sistem Komponenti Genel Bakış

Turtle-ID Multi-Agent System üç ana komponenten oluşur:

```
┌──────────────────────────────────────────────────────────────┐
│                    CLIENT APPLICATION                         │
│                   (Web/Mobile Frontend)                       │
└───────────────────────────┬──────────────────────────────────┘
                            │
                   HTTP REST API (Port 3000)
                            │
                ┌───────────▼─────────────┐
                │ COORDINATOR AGENT       │
                │ (Node.js + Express.js)  │
                │ • Route Management      │
                │ • Request Handling      │
                │ • Health Monitoring     │
                └───────┬────────┬────────┘
                        │        │
        ┌───────────────┘        └──────────────────┐
        │                                           │
        │ HTTP (Port 5000)              HTTP (Port 5001)
        │                                           │
   ┌────▼──────────────────┐     ┌──────────────────▼────┐
   │ IMAGE ANALYSIS AGENT   │     │ DATABASE AGENT       │
   │ (Python + OpenCV)      │     │ (Python + MySQL)     │
   │                        │     │                      │
   │ • Image Preprocessing  │     │ • Data Storage       │
   │ • ML Model Inference   │     │ • Similarity Search  │
   │ • Feature Extraction   │     │ • Query Processing   │
   │ • Pattern Recognition  │     │ • Transactions       │
   └────────────────────────┘     └──────────────────────┘
```

## Agent Mimarisi Detayları

### 1️⃣ Koordinatör Agent (Node.js)

**Dosyalar:**
```
backend/
├── src/
│   ├── index.js                    # Entry point
│   ├── services/agentService.js    # Agent komünikasyon
│   └── routes/
│       ├── health.js               # Sistem durumu
│       ├── identification.js       # Kaplumbağa analiz
│       └── turtle.js               # Veri sorguları
├── package.json                    # Dependencies
└── .env                            # Yapılandırma
```

**Sorumluluklar:**
- REST API endpoint'lerini expose et
- Client isteklerini doğrula
- Image Agent'a görüntü gönder
- Sonuçları Database Agent'dan al
- Yanıtları birleştir ve döndür

**API Routes:**
```
POST   /api/identification/identify      → Kaplumbağa tanımla
POST   /api/identification/register      → Yeni kaplumbağa kaydet
GET    /api/turtle/:id                   → Kaplumbağa bilgisi
GET    /api/turtle                       → Tüm kaplumbağaları listele
PUT    /api/turtle/:id                   → Kaplumbağa güncelle
GET    /api/health                       → Sistem durumu
```

### 2️⃣ Görüntü Analiz Agent (Python)

**Dosyalar:**
```
image-analysis-agent/
├── app.py                          # Flask uygulaması
├── config.py                       # Yapılandırma
├── src/
│   ├── models/
│   │   ├── turtle_model.py         # ML model wrapper
│   │   └── weights/
│   │       └── best_model.pt       # Pre-trained YOLOv8
│   └── processing/
│       └── image_processor.py      # OpenCV işlemleri
├── requirements.txt                # Python packages
└── .env                            # Yapılandırma
```

**Sorumluluklar:**
- Görüntü decode et (Base64 → numpy)
- Ön işleme yap (resize, normalize, enhance)
- ML model ile inference yap
- Kaplumbağa özelliklerini çıkar
- Güven puanı hesapla
- Benzerleme için feature vector'ü çıkar

**API Routes:**
```
POST   /api/analyze                 → Görüntü analiz et
POST   /api/features                → Özellik vektörü çıkar
GET    /api/health                  → Sağlık kontrolü
GET    /api/model/info              → Model bilgisi
```

### 3️⃣ Veritabanı Agent (Python)

**Dosyalar:**
```
database-agent/
├── app.py                          # Flask uygulaması
├── config.py                       # Yapılandırma
├── migrate.py                      # Database setup
├── src/
│   ├── database.py                 # MySQL manager
│   └── models/
│       └── turtle.py               # Turtle model
├── requirements.txt                # Python packages
└── .env                            # Yapılandırma
```

**Database Schema:**
```sql
CREATE TABLE turtles (
    id VARCHAR(36) PRIMARY KEY,
    image_base64 LONGTEXT,
    analysis_result JSON,
    metadata JSON,
    species VARCHAR(100),
    location VARCHAR(200),
    registered_at DATETIME,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE sightings (
    id VARCHAR(36) PRIMARY KEY,
    turtle_id VARCHAR(36),
    location VARCHAR(200),
    date_sighted DATETIME,
    observer_name VARCHAR(100),
    notes TEXT,
    FOREIGN KEY (turtle_id) REFERENCES turtles(id)
);

CREATE TABLE turtle_features (
    id VARCHAR(36) PRIMARY KEY,
    turtle_id VARCHAR(36),
    feature_vector LONGBLOB,
    FOREIGN KEY (turtle_id) REFERENCES turtles(id)
);
```

**API Routes:**
```
POST   /api/turtle                  → Yeni kaplumbağa kaydet
GET    /api/turtle/:id              → Kaplumbağa bilgisi getir
GET    /api/turtles                 → Tüm kaplumbağaları listele
PUT    /api/turtle/:id              → Kaplumbağa güncelle
POST   /api/turtle/save             → Kaplumbağa kaydet
POST   /api/turtle/similarity-search → Benzer kaplumbağaları ara
GET    /api/health                  → Sağlık kontrolü
```

## Veri Akışı Örnekleri

### Example 1: Kaplumbağa Tanımlama

```
1. Client gönderir:
   POST /api/identification/identify
   {
     "imageBase64": "iVBORw0KGgo...",
     "metadata": {"location": "Dalyan", "date": "2024-01-15"}
   }

2. Koordinatör Agent:
   ✓ Requestu doğrula
   ✓ requestId üret
   → Image Agent'a gönder

3. Image Analysis Agent:
   ✓ Görüntüyü decode et
   ✓ Ön işleme yap
   ✓ ML model çalıştır
   ✓ Özellikleri çıkar
   → {"turtle_id": "turtle_001", "confidence": 0.92, "features": [...]}

4. Koordinatör Agent:
   → Database Agent'a gönder (similarity search için)

5. Database Agent:
   ✓ Feature vektörü compare et
   ✓ Benzer kaplumbağaları ara
   → [{"turtle_id": "turtle_002", "similarity": 0.89}, ...]

6. Koordinatör Agent:
   ✓ Sonuçları birleştir
   → Client'a gönder

7. Client alır:
   {
     "success": true,
     "identification": {...},
     "similarMatches": [...],
     "timestamp": "2024-01-15T10:30:00Z"
   }
```

### Example 2: Yeni Kaplumbağa Kaydı

```
1. Client:
   POST /api/identification/register
   {"imageBase64": "...", "analysisResult": {...}, "metadata": {...}}

2. Koordinatör → Database Agent:
   ✓ Kaplumbağa kaydını oluştur
   ✓ Image Base64'ü sakla
   ✓ Analysis sonuçlarını sakla

3. Database Agent:
   ✓ UUID üret: "turtle_uuid_123"
   ✓ Turtles tablosuna ekle
   ✓ Metadata ve analiz sonuçlarını sakla

4. Koordinatör:
   → Client'a başarı yanıtı gönder
   {
     "success": true,
     "turtle": {"id": "turtle_uuid_123", "species": "...", ...},
     "message": "Turtle registered successfully"
   }
```

## Kurulum ve Çalıştırma

### Docker ile (Önerilen)
```bash
docker-compose up -d
```

### Manual Kurulum
```bash
# Setup script'i çalıştır
bash setup-dev.sh        # Linux/macOS
setup-dev.bat            # Windows

# Tüm agent'ları ayrı terminallerde başlat
cd backend && npm run dev
cd image-analysis-agent && python app.py
cd database-agent && python app.py
```

## Yapılandırma

### Backend .env
```
PORT=3000
IMAGE_AGENT_URL=http://localhost:5000
DB_AGENT_URL=http://localhost:5001
DB_HOST=localhost
DB_NAME=turtle_id_db
```

### Image Agent .env
```
PORT=5000
MODEL_PATH=./src/models/weights/best_model.pt
CONFIDENCE_THRESHOLD=0.85
```

### Database Agent .env
```
PORT=5001
DB_HOST=localhost
DB_USER=turtle_user
DB_PASSWORD=secure_password
DB_NAME=turtle_id_db
```

## Performance Tuning

### Image Analysis
- Model'i GPU'da çalıştır
- Batch processing ile throughput artır
- Image caching uygulaması

### Database
- Index'leri optimize et
- Connection pool size ayarla
- Query optimization

### Koordinatör
- Request caching
- Async processing
- Rate limiting

## Testing

### Unit Tests
```bash
cd backend && npm test
cd image-analysis-agent && pytest tests/
```

### Integration Tests
```bash
npm run test:integration
```

### Health Check
```bash
curl http://localhost:3000/api/health
```

## Scaling Stratejileri

1. **Horizontal Scaling**: Birden fazla Koordinatör instance'ı
2. **Load Balancing**: Nginx/HAProxy frontend
3. **Caching**: Redis cache layer
4. **Database Replication**: MySQL master-slave
5. **Async Processing**: Message queue (RabbitMQ)

## Monitoring

- **Logs**: Winston, Python logging
- **Metrics**: Prometheus
- **Tracing**: Jaeger
- **Dashboards**: Grafana

## Güvenlik

- JWT authentication
- HTTPS/SSL
- Input validation
- Rate limiting
- CORS configuration
- Database encryption

## Contributing

1. Fork repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## Lisans

MIT

---

**Sorular?** Bakınız: [docs/](docs/) klasörü
