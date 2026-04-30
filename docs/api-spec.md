# Turtle-ID API Specification

## Base URL
```
http://localhost:3000/api
```

## Authentication
Şu anda kimlik doğrulaması yapılmamaktadır. Üretim ortamında JWT kullanılmalıdır.

## Response Format

Tüm API yanıtları JSON formatındadır:

```json
{
  "success": true/false,
  "data": {...},
  "error": "error message",
  "timestamp": "ISO 8601 timestamp",
  "requestId": "unique request identifier"
}
```

## Endpoints

### 1. Health Check

#### GET /health
Sistem durumu kontrolü

**Response (200):**
```json
{
  "coordinator": "OK",
  "imageAnalysisAgent": "OK",
  "databaseAgent": "OK",
  "allAgentsHealthy": true,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

### 2. Identification

#### POST /identification/identify
Görüntüden kaplumbağa tanımlama

**Request:**
```json
{
  "imageBase64": "string (base64 encoded image)",
  "metadata": {
    "location": "string (optional)",
    "date": "string (YYYY-MM-DD, optional)",
    "observer": "string (optional)"
  }
}
```

**Response (200):**
```json
{
  "requestId": "uuid",
  "success": true,
  "identification": {
    "turtle_id": "string",
    "species": "string",
    "confidence": 0.92,
    "shell_pattern": "string",
    "characteristics": {
      "shell_color": "string",
      "size_estimate": "string",
      "distinctive_marks": ["string"]
    }
  },
  "similarMatches": [
    {
      "turtle_id": "string",
      "similarity": 0.89,
      "species": "string"
    }
  ],
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Errors:**
- 400: Missing or invalid imageBase64
- 500: Image analysis failed

---

#### POST /identification/register
Tanımlanan kaplumbağayı kaydet

**Request:**
```json
{
  "imageBase64": "string",
  "analysisResult": {
    "turtle_id": "string",
    "species": "string",
    "confidence": 0.92
  },
  "metadata": {
    "location": "string (optional)",
    "observer": "string (optional)"
  }
}
```

**Response (201):**
```json
{
  "success": true,
  "requestId": "uuid",
  "turtle": {
    "id": "uuid",
    "species": "string",
    "location": "string",
    "registered_at": "2024-01-15T10:30:00Z"
  },
  "message": "Turtle registered successfully"
}
```

---

### 3. Turtle Information

#### GET /turtle/:id
Kaplumbağa bilgisini getir

**Parameters:**
- `id` (path): Turtle ID

**Response (200):**
```json
{
  "success": true,
  "turtle": {
    "id": "uuid",
    "species": "Chelonia mydas",
    "location": "Dalyan Beach",
    "registered_at": "2024-01-15T10:30:00Z",
    "metadata": {
      "observer": "John Doe",
      "notes": "string"
    }
  }
}
```

**Errors:**
- 404: Turtle not found

---

#### GET /turtle
Tüm kaplumbağaları listele (filtreleme ile)

**Query Parameters:**
- `limit` (int, default: 50): Kaç sonuç döndür
- `offset` (int, default: 0): Offset
- `location` (string, optional): Konum ile filtrele
- `species` (string, optional): Tür ile filtrele

**Response (200):**
```json
{
  "success": true,
  "count": 10,
  "turtles": [
    {
      "id": "uuid",
      "species": "string",
      "location": "string",
      "registered_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

---

#### PUT /turtle/:id
Kaplumbağa bilgisini güncelle

**Parameters:**
- `id` (path): Turtle ID

**Request:**
```json
{
  "metadata": {
    "notes": "string",
    "observer": "string"
  },
  "species": "string (optional)",
  "location": "string (optional)"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Turtle updated successfully",
  "turtle": {
    "id": "uuid",
    "species": "string",
    "location": "string",
    "updated_at": "2024-01-15T10:30:00Z"
  }
}
```

---

## Error Codes

| Code | Message | Description |
|------|---------|-------------|
| 200 | OK | Başarılı |
| 201 | Created | Kaynak oluşturuldu |
| 400 | Bad Request | Geçersiz istek |
| 404 | Not Found | Kaynak bulunamadı |
| 500 | Internal Server Error | Server hatası |
| 503 | Service Unavailable | Servis kullanılamıyor |

## Rate Limiting

Currently: No rate limiting (Implement in production)

Planned:
- 100 requests per minute per IP
- 10 requests per second per user

## Versioning

API version: v1
Future versions: /api/v2, /api/v3, etc.

## Examples

### cURL Example - Identify Turtle

```bash
curl -X POST http://localhost:3000/api/identification/identify \
  -H "Content-Type: application/json" \
  -H "X-Request-ID: request-123" \
  -d @- << 'EOF'
{
  "imageBase64": "iVBORw0KGgoAAAANSUhEUg...",
  "metadata": {
    "location": "Dalyan Beach",
    "date": "2024-01-15",
    "observer": "John Doe"
  }
}
EOF
```

### JavaScript Example - Register Turtle

```javascript
const response = await fetch('http://localhost:3000/api/identification/register', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    imageBase64: imageData,
    analysisResult: {
      turtle_id: 'turtle_001',
      species: 'Chelonia mydas',
      confidence: 0.92
    },
    metadata: {
      location: 'Dalyan Beach',
      observer: 'John Doe'
    }
  })
});

const result = await response.json();
```

### Python Example - Query Turtles

```python
import requests

response = requests.get(
    'http://localhost:3000/api/turtle',
    params={
        'limit': 20,
        'location': 'Dalyan Beach',
        'offset': 0
    }
)

turtles = response.json()['turtles']
```

## Changelog

### v1.0.0 (2024-01-15)
- Initial release
- Basic identification
- Turtle registration
- Query capabilities
