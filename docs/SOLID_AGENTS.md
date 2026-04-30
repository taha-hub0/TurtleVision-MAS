# Turtle-ID SOLID Mimarı: Yeni Agent'lar

## 📋 Genel Bakış

Turtle-ID Multi-Agent System'e **SOLID prensiplerine uygun** dört yeni ajan eklenmiştir:

```
┌──────────────────────────────────────────────────────────────────┐
│                        Client Request                            │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                ┌────────▼──────────┐
                │ Gatekeeper Agent  │ ◄─── 1. Metadata Validation
                │ (Validation)      │
                └────────┬──────────┘
                         │ ✓ Valid
                ┌────────▼──────────┐
                │ Biolytics Agent   │ ◄─── 2. Species & Features
                │ (Strategy Pattern)│      (Green Turtle / Leatherback)
                └────────┬──────────┘
                         │ Biometric Code
                ┌────────▼──────────┐
                │ Matching Agent    │ ◄─── 3. Similarity (%90)
                │ (%90 Threshold)   │      Old Record / New Individual
                └────────┬──────────┘
                         │
                ┌────────▼──────────┐
                │ Reporter Agent    │ ◄─── 4. Report Generation
                │ (DEKAMER Std)     │      JSON / PDF (Non-invasive)
                └────────┬──────────┘
                         │
                    ◄────► Database Agent (MySQL)
                         │
                ┌────────▼──────────┐
                │  Client Response  │
                └───────────────────┘
```

---

## 1️⃣ Gatekeeper Agent (Node.js)

### Görev
Gelen fotoğraf ve metadata'yı doğrula. GPS, tarih ve gözlemci bilgilerini kontrol et.

### SOLID Prensiplerine Uyumu
- **S (Single Responsibility)**: Sadece doğrulama işi yapar
- **O (Open/Closed)**: Yeni validasyon kuralları eklenebilir
- **I (Interface Segregation)**: `validateMetadata()` tek bir yapıya odaklanır

### API Endpoint'leri

#### POST `/api/validation/validate`
Metadata doğrulama

**Request:**
```json
{
  "imageBase64": "iVBORw0KGgo...",
  "timestamp": "2024-01-15T10:30:00Z",
  "location": {
    "latitude": 36.7138,
    "longitude": 31.2327,
    "accuracy": 10.5
  },
  "observer": {
    "name": "Dr. John Doe",
    "email": "john@example.com",
    "organization": "Marine Research Institute"
  },
  "conditions": {
    "waterTemperature": 24.5,
    "weather": "sunny",
    "waterClarity": "clear"
  }
}
```

**Response (200):**
```json
{
  "success": true,
  "validated_metadata": {
    "captured_at": "2024-01-15T10:30:00Z",
    "latitude": 36.7138,
    "longitude": 31.2327,
    "accuracy": 10.5,
    "observer_name": "Dr. John Doe",
    "observer_email": "john@example.com",
    "organization": "Marine Research Institute",
    "water_temperature": 24.5,
    "weather": "sunny",
    "water_clarity": "clear",
    "validated_at": "2024-01-15T10:35:00Z"
  },
  "warnings": [],
  "validated_at": "2024-01-15T10:35:00Z"
}
```

**Error Response (400):**
```json
{
  "success": false,
  "errors": [
    "Invalid latitude",
    "GPS location is required"
  ],
  "warnings": [
    "Observer information not provided"
  ]
}
```

#### GET `/api/validation/health`
Gatekeeper Agent durumu

---

## 2️⃣ Biolytics Agent (Python)

### Görev
**Strategy Pattern** kullanarak deniz kaplumbağalarını türlerine göre tanımlama:
- **Yeşil Kaplumbağa (Chelonia mydas)**: Post-ocular scutes analizi
- **Deri Sırtlı (Dermochelys coriacea)**: Pineal spot analizi

### SOLID Prensiplerine Uyumu
- **S**: Her strateji tek sorumluluğa sahip
- **O**: Yeni türler (stratejiler) kolayca eklenebilir
- **L**: Tüm stratejiler `TurtleIdentificationStrategy` interface'ini implement eder
- **I**: İnce arayüzler - her strateji gerekli metodları içerir
- **D**: `BiolyticsAgent` soyut stratejilere bağımlı (somut sınıflara değil)

### Strategy Mimarı

```
┌─────────────────────────────────┐
│ TurtleIdentificationStrategy    │ (Abstract)
│ - identify()                    │
│ - extract_biometric_code()      │
│ - get_distinctive_features()    │
└────────────┬────────────────────┘
             │
      ┌──────┴──────┐
      │             │
      ▼             ▼
┌──────────────┐ ┌──────────────────┐
│ GreenTurtle  │ │  Leatherback     │
│ Strategy     │ │ Strategy         │
│              │ │                  │
│ Post-ocular  │ │ Pineal spot      │
│ scutes       │ │ (pink mark)      │
└──────────────┘ └──────────────────┘

      Both implement interface
           │
      ▼─────┴─────▼
   Biometric Code
   (Sayısal Kod)
```

### API Endpoint'leri

#### POST `/api/biolytics/analyze`
Belirli strateji ile analiz

**Request:**
```json
{
  "image": "iVBORw0KGgo...",
  "strategy": "green"  // "green" veya "leatherback"
}
```

**Response (Green Turtle - 200):**
```json
{
  "success": true,
  "analysis": {
    "species": "Chelonia mydas",
    "turtle_type": "GREEN_TURTLE",
    "confidence": 0.92,
    "features": {
      "shell_color": "dark_green",
      "post_ocular_scutes": 15,
      "head_shape": "rounded",
      "confidence": 0.92
    },
    "biometric_code": "102034560912341111",
    "extraction_method": "post_ocular_scutes_pattern"
  }
}
```

**Response (Leatherback - 200):**
```json
{
  "success": true,
  "analysis": {
    "species": "Dermochelys coriacea",
    "turtle_type": "LEATHERBACK",
    "confidence": 0.90,
    "features": {
      "pineal_spot": {
        "detected": true,
        "size": "large",
        "color_intensity": "high"
      },
      "shell_texture": "leathery",
      "shell_color": "dark_brown",
      "confidence": 0.90
    },
    "biometric_code": "003651001204003456",
    "extraction_method": "pineal_spot_analysis"
  }
}
```

#### POST `/api/biolytics/auto-detect`
Otomatik tür bulma (tüm stratejileri dene)

**Request:**
```json
{
  "image": "iVBORw0KGgo..."
}
```

**Response (200):**
```json
{
  "success": true,
  "selected_strategy": "green",
  "analysis": {
    "species": "Chelonia mydas",
    "turtle_type": "GREEN_TURTLE",
    "confidence": 0.92
  },
  "alternatives": [
    {
      "strategy": "leatherback",
      "confidence": 0.45
    }
  ]
}
```

#### GET `/api/biolytics/health`
Biolytics Agent durumu

---

## 3️⃣ Matching Agent (Node.js)

### Görev
Biyometrik kodu veritabanındaki kayıtlarla %90 benzerlik kuralına göre kıyasla.
- **Eşleşme bulundu**: "ESKI KAYIT" (EXISTING_RECORD)
- **Eşleşme yok**: "YENİ BİREY" (NEW_INDIVIDUAL)

### Algoritma
- **Hamming Distance**: String tabanlı kodlar için (post-ocular scutes)
- **Kosinüs Benzerliği**: Vector tabanlı özellikler için

### SOLID Prensiplerine Uyumu
- **S**: Sadece benzerlik araştırması yapar
- **O**: Yeni matching algoritmaları eklenebilir
- **D**: Database Agent'ına bağımlı (dependency injection)

### API Endpoint'leri

#### POST `/api/matching/find`
Biyometrik kodu ara

**Request:**
```json
{
  "biometricCode": "102034560912341111",
  "matchingCriteria": {
    "threshold": 0.9,
    "topN": 5,
    "method": "hamming"
  }
}
```

**Response - Match Bulundu (200):**
```json
{
  "success": true,
  "matching_result": {
    "success": true,
    "classification": "EXISTING_RECORD",
    "matches": [
      {
        "turtleId": "turtle_uuid_123",
        "species": "Chelonia mydas",
        "recordedAt": "2023-06-15T08:22:00Z",
        "similarity": 0.96
      },
      {
        "turtleId": "turtle_uuid_456",
        "species": "Chelonia mydas",
        "recordedAt": "2023-08-22T14:45:00Z",
        "similarity": 0.78
      }
    ],
    "topMatch": {
      "turtleId": "turtle_uuid_123",
      "species": "Chelonia mydas",
      "recordedAt": "2023-06-15T08:22:00Z",
      "similarity": 0.96
    },
    "confidence": 0.96,
    "threshold": 0.9,
    "matchMethod": "hamming"
  },
  "report": {
    "timestamp": "2024-01-15T10:35:00Z",
    "classification": "ESKI_KAYIT",
    "confidence": 0.96,
    "details": {
      "type": "ESKI_KAYIT",
      "description": "Previously identified individual",
      "matchedTurtle": {
        "turtleId": "turtle_uuid_123",
        "similarity": "96.00%"
      },
      "matchingMethod": "hamming"
    }
  }
}
```

**Response - Yeni Birey (200):**
```json
{
  "success": true,
  "matching_result": {
    "success": true,
    "classification": "NEW_INDIVIDUAL",
    "matches": [
      {
        "turtleId": "turtle_uuid_789",
        "similarity": 0.72
      }
    ],
    "topMatch": null,
    "confidence": 0,
    "threshold": 0.9
  },
  "report": {
    "classification": "YENİ_BİREY",
    "details": {
      "type": "YENİ_BİREY",
      "description": "New individual detected",
      "possibleMatches": [
        {
          "turtleId": "turtle_uuid_789",
          "similarity": 0.72
        }
      ],
      "closestMatch": {
        "turtleId": "turtle_uuid_789",
        "similarity": 0.72
      }
    }
  }
}
```

#### POST `/api/matching/batch`
Toplu eşleştirme

**Request:**
```json
{
  "biometricCodes": [
    "102034560912341111",
    "103045670913351222",
    "104056781014361333"
  ],
  "matchingCriteria": {
    "threshold": 0.9
  }
}
```

#### GET `/api/matching/health`
Matching Agent durumu

---

## 4️⃣ Reporter Agent (Node.js)

### Görev
**DEKAMER standartlarına** uygun JSON/PDF rapor üret.

**DEKAMER Standartı**: Deniz Kaplumbağaları Araştırma Enstitüsü
- Non-invaziv (zararsız) biyometrik tanımlama
- Geleneksel markalamaya göre daha ucuz ve güvenilir

### Rapor İçeriği
1. **Gözlem Bilgileri**: Tarih, konum, gözlemci
2. **Biyolojik Analiz**: Tür, özellikleri, sağlık durumu
3. **Biyometrik İmza**: Tanımlama kodu, kalite skoru
4. **Eşleştirme Sonuçları**: ESKI_KAYIT / YENİ_BİREY
5. **Metodoloji**: Non-invaziv yöntemin avantajları
6. **DEKAMER Uygunluğu**: Standart kontrolü
7. **Sonuç ve Öneriler**: Koruma değeri, eylem önerileri

### API Endpoint'leri

#### POST `/api/reporting/generate`
Rapor oluştur

**Request:**
```json
{
  "format": "json",
  "analysisData": {
    "analysis": {
      "species": "Chelonia mydas",
      "turtle_type": "GREEN_TURTLE",
      "confidence": 0.92
    },
    "biometric_code": "102034560912341111",
    "extraction_method": "post_ocular_scutes_pattern",
    "quality_score": 0.95,
    "metadata": {
      "timestamp": "2024-01-15T10:30:00Z",
      "location": {
        "latitude": 36.7138,
        "longitude": 31.2327,
        "accuracy": 10.5
      },
      "observer": {
        "name": "Dr. John Doe",
        "email": "john@example.com"
      },
      "conditions": {
        "waterTemperature": 24.5
      }
    },
    "measurements": {
      "shell_length": 85.5,
      "shell_width": 75.0,
      "weight": 150
    },
    "health": {
      "wounds": [],
      "diseases": [],
      "parasites": [],
      "condition": "GOOD"
    }
  },
  "matchingData": {
    "classification": "EXISTING_RECORD",
    "confidence": 0.96,
    "threshold": 0.9,
    "topMatch": {
      "turtleId": "turtle_uuid_123",
      "similarity": 0.96,
      "recordedAt": "2023-06-15T08:22:00Z"
    }
  }
}
```

**Response (200):**
```json
{
  "success": true,
  "format": "json",
  "report": {
    "report_id": "uuid-here",
    "timestamp": "2024-01-15T10:35:00Z",
    "observation": { ... },
    "biological_analysis": { ... },
    "matching_result": { ... },
    "matched_individual": { ... },
    "methodology": {
      "title": "Non-Invaziv Biyometrik Tanımlama - DEKAMER Standardı",
      "advantages": [
        {
          "title": "Zararsız (Non-invasive)",
          "description": "Hayvanın bedensel bütünlüğünü koruyarak tanımlama yapılır."
        },
        {
          "title": "Maliyet Etkin",
          "description": "Geleneksel markalama yöntemine kıyasla çok daha ekonomiktir."
        },
        {
          "title": "Güvenilir",
          "description": "Yapay zeka destekli görüntü analizi sayesinde yüksek doğruluk sağlar."
        },
        {
          "title": "İleri İzleme",
          "description": "Populasyon dinamiklerinin uzun vadeli izlenmesine olanak tanır."
        }
      ]
    },
    "compliance": {
      "standard": "DEKAMER",
      "compliant": true
    }
  }
}
```

#### GET `/api/reporting/health`
Reporter Agent durumu

---

## 🔄 Tam İş Akışı Örneği

### Senaryo: Yeni Kaplumbağa Tanımlama

```
1. Client gönderir:
   POST /api/validation/validate
   {
     "imageBase64": "...",
     "timestamp": "2024-01-15T10:30:00Z",
     "location": {"latitude": 36.7138, "longitude": 31.2327},
     "observer": {"name": "Dr. John", "email": "john@example.com"}
   }

2. Gatekeeper Agent doğrular ✓

3. Client gönderir:
   POST /api/biolytics/auto-detect
   {"image": "..."}

4. Biolytics Agent analiz eder (Strategy: Green Turtle)
   → Biometric Code: "102034560912341111"
   → Species: Chelonia mydas
   → Confidence: 0.92

5. Client gönderir:
   POST /api/matching/find
   {"biometricCode": "102034560912341111"}

6. Matching Agent arar
   → Result: NEW_INDIVIDUAL (Similarity: 0.72 < 0.90)

7. Client gönderir:
   POST /api/reporting/generate
   {
     "format": "json",
     "analysisData": {...},
     "matchingData": {...}
   }

8. Reporter Agent üretir
   → DEKAMER Standard Rapor
   → JSON Format
   → Non-invasive Analiz

9. Client alır:
   {
     "success": true,
     "report": {
       "classification": "YENİ_BİREY",
       "methodology": "Non-Invaziv Biyometrik Tanımlama"
     }
   }
```

---

## 📊 Karşılaştırma: Non-Invazif vs. Geleneksel Markalama

| Kriter | Geleneksel Markalama | Non-Invazif Biyometri |
|--------|---------------------|----------------------|
| **Hayvan İçin** | İnvazif (hasar) | Zararsız |
| **Maliyet** | Yüksek (malzeme, geri yakalama) | Düşük (dijital) |
| **Güvenilirlik** | Orta (iz kaybolabilir) | Yüksek (AI destekli) |
| **Uzun Vadeli İzleme** | Sınırlı | Kapsamlı |
| **Çevre Dostu** | Hayır (hayvan stres) | Evet |
| **Hız** | Yavaş | Hızlı |

---

## 🧪 Test Etme

### 1. Gatekeeper Validation
```bash
curl -X POST http://localhost:3000/api/validation/validate \
  -H "Content-Type: application/json" \
  -d '{
    "imageBase64": "iVBORw0KGgo...",
    "timestamp": "2024-01-15T10:30:00Z",
    "location": {"latitude": 36.7138, "longitude": 31.2327},
    "observer": {"name": "John", "email": "john@example.com"}
  }'
```

### 2. Biolytics Analysis
```bash
curl -X POST http://localhost:5000/api/biolytics/auto-detect \
  -H "Content-Type: application/json" \
  -d '{"image": "iVBORw0KGgo..."}'
```

### 3. Matching
```bash
curl -X POST http://localhost:3000/api/matching/find \
  -H "Content-Type: application/json" \
  -d '{
    "biometricCode": "102034560912341111",
    "matchingCriteria": {"threshold": 0.9}
  }'
```

### 4. Reporting
```bash
curl -X POST http://localhost:3000/api/reporting/generate \
  -H "Content-Type: application/json" \
  -d '{
    "format": "json",
    "analysisData": {...},
    "matchingData": {...}
  }'
```

---

## 📁 Proje Yapısı

```
backend/src/agents/
├── gatekeeperAgent.js      # Validation
├── matchingAgent.js        # Similarity (%90)
└── reporterAgent.js        # DEKAMER Reports

image-analysis-agent/src/agents/
└── biolytics.py            # Strategy Pattern
    ├── TurtleIdentificationStrategy (ABC)
    ├── GreenTurtleStrategy
    ├── LeatherbackStrategy
    └── BiolyticsAgent (Context)
```

---

## 🎯 SOLID Prensipleri Uygulanması

### Single Responsibility
- Gatekeeper: Sadece doğrulama
- Biolytics: Sadece tanımlama
- Matching: Sadece benzerlik
- Reporter: Sadece rapor

### Open/Closed
- Biolytics: Yeni stratejiler eklenebilir
- Matching: Yeni algoritma eklenebilir
- Reporter: Yeni format eklenebilir

### Liskov Substitution
- Tüm stratejiler `TurtleIdentificationStrategy` yerine kullanılabilir

### Interface Segregation
- Her ajan sadece ihtiyaç duyduğu metodlar vardır

### Dependency Inversion
- Concrete sınıflara değil, interface'lere bağımlı

---

## 📚 Referanslar

- [SOLID Prensipleris](https://en.wikipedia.org/wiki/SOLID)
- [Strategy Pattern](https://refactoring.guru/design-patterns/strategy)
- [DEKAMER Standartları](https://example.com)

---

**Sorular?** Bkz: [docs/](../docs/) klasörü
