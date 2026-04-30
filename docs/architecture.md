# Turtle-ID Multi-Agent System - Mimarı Dökümanı

## Sistem Mimarisi Genel Bakış

Turtle-ID Multi-Agent System (MAS), deniz kaplumbağalarını fotoğraflarından tanımlamak için tasarlanmış dağıtılmış bir sistem mimarisidir.

### MAS Bileşenleri

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Application                        │
│                   (Web/Mobile Frontend)                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                ┌────────▼────────┐
                │ Coordinator     │
                │ Agent (Node.js) │
                │ - Req. Manager  │
                │ - Orchestration │
                │ - Result Merge  │
                └────┬────────┬───┘
                     │        │
         ┌───────────┘        └────────────────┐
         │                                      │
    ┌────▼──────────────────┐   ┌─────────────▼─────┐
    │ Image Analysis Agent  │   │ Database Agent    │
    │ (Python/OpenCV)       │   │ (Python/MySQL)    │
    │                       │   │                   │
    │ - Image Processing    │   │ - Data Storage    │
    │ - Model Inference     │   │ - Similarity      │
    │ - Feature Extraction  │   │   Search          │
    │ - Quality Assessment  │   │ - Query Handling  │
    └───────────────────────┘   └───────────────────┘
```

### Agent'lar ve Sorumlulukları

#### 1. Koordinatör Agent (Node.js + Express.js)

**Görevler:**
- İstemci isteklerini alır ve yönlendirir
- Diğer agent'lar arasında iletişimi yönetir
- Paralel işlemleri koordine eder
- Sistem sağlığını izler
- Cache yönetimi

**API Endpoints:**
- `POST /api/identification/identify` - Kaplumbağa tanımlama
- `POST /api/identification/register` - Yeni kaplumbağa kaydı
- `GET /api/turtle/:id` - Kaplumbağa bilgisi
- `GET /api/turtle` - Tüm kaplumbağaları listele
- `PUT /api/turtle/:id` - Kaplumbağa güncelle
- `GET /api/health` - Sistem durumu

#### 2. Görüntü Analiz Agent (Python + OpenCV + TensorFlow)

**Görevler:**
- Yüklenen görüntüleri işler
- Karapaksı (shell) algılaması yapar
- Deniz kaplumbağası özelliklerini çıkar
- Eşik değerlerine göre güven puanı hesaplar
- Benzerlik araması için özellikleri çıkar

**API Endpoints:**
- `POST /api/analyze` - Görüntü analiz et
- `POST /api/features` - Özellik çıkar
- `GET /api/health` - Sağlık kontrolü
- `GET /api/model/info` - Model bilgisi

#### 3. Veritabanı Agent (Python + MySQL)

**Görevler:**
- Tanımlanan kaplumbağaları depolar
- Avistama verilerini kaydeder
- Benzerlik araması yapar
- Sorguları işler
- Veri tutarlılığını sağlar

**Database Schema:**
```
- turtles (id, image_base64, analysis_result, species, location, ...)
- sightings (id, turtle_id, location, date_sighted, observer_name, ...)
- turtle_features (id, turtle_id, feature_vector, ...)
```

## Teknoloji Stack

| Katman | Teknoloji | Açıklama |
|--------|-----------|---------|
| **Backend/Orkestra** | Node.js, Express.js | REST API ve koordinasyon |
| **Görüntü Analiz** | Python, OpenCV, TensorFlow/PyTorch | ML tabanlı görüntü işleme |
| **Veritabanı** | MySQL | İlişkisel veri depolaması |
| **Agent İletişimi** | HTTP/REST, WebSockets | Senkron/asenkron haberleşme |
| **Containerization** | Docker | Dağıtım ve yönetim |

## Veri Akışı

### Turtle Identification Flow

```
1. Client
   ├── POST /api/identification/identify
   └── Sends: imageBase64, metadata

2. Coordinator Agent
   ├── Validates request
   ├── Generates requestId
   └── Forwards to Image Analysis Agent

3. Image Analysis Agent
   ├── Decodes image
   ├── Preprocesses (resize, normalize)
   ├── Runs ML model inference
   ├── Extracts features
   └── Returns: analysis_result, confidence, features

4. Coordinator Agent
   ├── Receives analysis result
   ├── Forwards features to Database Agent
   └── Requests: similarity_search

5. Database Agent
   ├── Compares feature vector
   ├── Searches for similar turtles
   └── Returns: matches with similarity scores

6. Coordinator Agent
   ├── Merges results
   ├── Formats response
   └── Returns to Client
```

### Turtle Registration Flow

```
1. Client
   ├── POST /api/identification/register
   └── Sends: imageBase64, analysisResult, metadata

2. Coordinator Agent
   ├── Validates request
   └── Forwards to Database Agent

3. Database Agent
   ├── Creates turtle record
   ├── Saves image
   ├── Stores analysis results
   └── Returns: turtle_id

4. Coordinator Agent
   ├── Returns success response
   └── Includes: turtle_id, timestamp
```

## Kurulum Adımları

### Prerequisites
- Node.js 16+ ve npm
- Python 3.9+
- MySQL 8.0+
- Git

### 1. Backend Kurulumu

```bash
cd backend
npm install
cp .env.example .env
# .env dosyasını yapılandır
npm run dev
```

### 2. Python Image Analysis Agent Kurulumu

```bash
cd image-analysis-agent
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# .env dosyasını yapılandır
python app.py
```

### 3. Database Agent Kurulumu

```bash
cd database-agent
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# .env dosyasını yapılandır
python migrate.py  # Database migration'larını çalıştır
python app.py
```

## Configuration

### Backend (.env)
```
PORT=3000
IMAGE_AGENT_URL=http://localhost:5000
DB_AGENT_URL=http://localhost:5001
DB_HOST=localhost
DB_NAME=turtle_id_db
```

### Image Analysis Agent (.env)
```
PORT=5000
MODEL_PATH=./src/models/weights/best_model.pt
CONFIDENCE_THRESHOLD=0.85
```

### Database Agent (.env)
```
PORT=5001
DB_HOST=localhost
DB_USER=root
DB_NAME=turtle_id_db
```

## API Kullanım Örnekleri

### 1. Kaplumbağa Tanımlama

```bash
curl -X POST http://localhost:3000/api/identification/identify \
  -H "Content-Type: application/json" \
  -d '{
    "imageBase64": "iVBORw0KGgoAAAANS...",
    "metadata": {
      "location": "Dalyan Beach",
      "date": "2024-01-15"
    }
  }'
```

**Response:**
```json
{
  "requestId": "uuid-here",
  "success": true,
  "identification": {
    "turtle_id": "turtle_001",
    "species": "Chelonia mydas",
    "confidence": 0.92
  },
  "similarMatches": [
    {
      "turtle_id": "turtle_002",
      "similarity": 0.89
    }
  ],
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 2. Yeni Kaplumbağa Kaydı

```bash
curl -X POST http://localhost:3000/api/identification/register \
  -H "Content-Type: application/json" \
  -d '{
    "imageBase64": "iVBORw0KGgoAAAANS...",
    "analysisResult": {...},
    "metadata": {
      "location": "Dalyan Beach",
      "observer": "John Doe"
    }
  }'
```

## Scalability Considerations

1. **Load Balancing**: Nginx/HAProxy ile koordinatör agent'ları scale et
2. **Database Replication**: MySQL master-slave replication
3. **Caching**: Redis cache untuk sık kullanılan sorgular
4. **Message Queue**: RabbitMQ/Kafka için asenkron işlemler
5. **Containerization**: Docker Compose veya Kubernetes

## Security

1. API Authentication: JWT tokens
2. HTTPS/SSL enkripsiyon
3. Input validation ve sanitization
4. Rate limiting
5. CORS configuration
6. Database connection encryption

## Testing

### Unit Tests
```bash
cd backend
npm test

cd image-analysis-agent
pytest tests/
```

### Integration Tests
```bash
npm run test:integration
```

## Monitoring ve Logging

- **Logging**: Winston (Node.js), Python logging
- **Monitoring**: Prometheus + Grafana
- **Tracing**: Jaeger distributed tracing
- **Health Checks**: Her 30 saniyede bir

## Performance Tuning

- Image resize optimization
- Model inference caching
- Database index tuning
- Connection pooling
- Async processing

## Gelecek Geliştirmeler

1. [ ] GPU acceleration for model inference
2. [ ] Real-time WebSocket updates
3. [ ] Multi-model ensemble
4. [ ] Advanced similarity search (FAISS)
5. [ ] Mobile app integration
6. [ ] Blockchain-based verification
7. [ ] Community contribution system

## Katkıda Bulunma

Pull request göndermekten çekinmeyin. Büyük değişiklikler için lütfen önce bir issue açın.

## Lisans

MIT
