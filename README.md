# Turtle-ID Multi-Agent System (MAS)

Deniz kaplumbağalarını fotoğraflarından tanımlamak için geliştirilmiş bir Multi-Agent System mimarisi.

## Sistem Mimarisi

```
┌─────────────────────────────────────────────────────┐
│              Client Application                      │
└────────────┬────────────────────────────────────────┘
             │
     ┌───────▼───────┐
     │ Coordinator   │
     │ Agent         │
     │ (Express.js)  │
     └───┬───────┬───┘
         │       │
    ┌────▼───┐   │
    │ Image  │   │
    │Analysis│   │
    │Agent   │   │
    │(Python)│   │
    └────┬───┘   │
         │       │
    ┌────▼──────▼┐
    │ Database   │
    │ Agent      │
    │ (MySQL)    │
    └────────────┘
```

## Teknoloji Yığını

- **Backend/Orkestra**: Node.js + Express.js
- **Görüntü Analiz**: Python + OpenCV + TensorFlow/PyTorch
- **Veritabanı**: MySQL
- **Agent İletişimi**: REST API / WebSockets

## Proje Yapısı

```
turtle-id-mas/
├── backend/                  # Node.js Koordinatör Agent
│   ├── src/
│   │   ├── agents/          # Agent yönetimi
│   │   ├── routes/          # API endpointleri
│   │   ├── services/        # İş mantığı
│   │   └── middleware/      # Express middleware
│   ├── package.json
│   └── .env
│
├── image-analysis-agent/    # Python Görüntü Analiz Agent
│   ├── src/
│   │   ├── models/          # ML modelleri
│   │   ├── processing/      # Görüntü işleme
│   │   └── services/        # İş mantığı
│   ├── requirements.txt
│   └── config.py
│
├── database-agent/          # Veritabanı Agent
│   ├── src/
│   │   ├── models/          # Veritabanı modelleri
│   │   ├── queries/         # SQL sorguları
│   │   └── services/        # DB servisleri
│   ├── migrations/          # Database migrations
│   └── config.py
│
└── docs/                    # Dokümantasyon
    ├── architecture.md
    ├── api-spec.md
    └── setup-guide.md
```

## Kurulum

### 1. Backend Setup (Node.js)
```bash
cd backend
npm install
npm run dev
```

### 2. Python Agents Setup
```bash
cd image-analysis-agent
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

### 3. Veritabanı Kurulumu
```bash
cd database-agent
pip install -r requirements.txt
python migrate.py
```

## API Endpoints

- `POST /api/turtle/identify` - Kaplumbağa tanımlama
- `GET /api/turtle/:id` - Kaplumbağa bilgisi
- `POST /api/turtle/register` - Yeni kaplumbağa kaydı
- `GET /api/health` - Sistem durumu kontrolü

## Lisans

MIT
