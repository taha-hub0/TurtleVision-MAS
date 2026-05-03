import type { Turtle, Sighting } from '../../types/turtle'

// Deniz kaplumbağası görselleri - Wikimedia Commons & Unsplash (açık lisans)
const placeholderImages = [
  // Yeşil kaplumbağalar
  'https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Chelonia_mydas_%28green_sea_turtle%29.jpg/640px-Chelonia_mydas_%28green_sea_turtle%29.jpg',
  'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c6/Sea_turtle_%28Chelonia_mydas%29_near_Watamu%2C_Kenya.jpg/640px-Sea_turtle_%28Chelonia_mydas%29_near_Watamu%2C_Kenya.jpg',

  // Loggerhead kaplumbağalar
  'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/Loggerhead_sea_turtle_%28Caretta_caretta%29.jpg/640px-Loggerhead_sea_turtle_%28Caretta_caretta%29.jpg',
  'https://upload.wikimedia.org/wikipedia/commons/thumb/9/9d/Caretta_caretta_%28Loggerhead_Sea_Turtle%29_%285249894178%29.jpg/640px-Caretta_caretta_%28Loggerhead_Sea_Turtle%29_%285249894178%29.jpg',

  // Deri kaplumbağalar
  'https://upload.wikimedia.org/wikipedia/commons/thumb/6/6c/Leatherback_sea_turtle_nesting%2C_Playa_Grande%2C_Costa_Rica.jpg/640px-Leatherback_sea_turtle_nesting%2C_Playa_Grande%2C_Costa_Rica.jpg',
  'https://upload.wikimedia.org/wikipedia/commons/thumb/6/6a/Dermochelys_coriacea.jpg/640px-Dermochelys_coriacea.jpg',

  // Şahin kaplumbağalar
  'https://upload.wikimedia.org/wikipedia/commons/thumb/7/7a/Eretmochelys_imbricata2.jpg/640px-Eretmochelys_imbricata2.jpg',
  'https://upload.wikimedia.org/wikipedia/commons/thumb/1/14/Hawksbill_turtle_%28Eretmochelys_imbricata%29.jpg/640px-Hawksbill_turtle_%28Eretmochelys_imbricata%29.jpg',
]

const mockTurtles: Record<string, Turtle> = {
  'turtle-001': {
    id: 'turtle-001',
    species: 'GREEN_TURTLE',
    biometric_code: '101101011101110110',
    biometric_vector: [0.45, 0.23, 0.89, 0.12, 0.56, 0.78, 0.34, 0.91, 0.67, 0.41],
    registeredAt: '2024-03-15T10:30:00Z',
    lastSightingAt: '2026-04-28T14:22:00Z',
    measurements: {
      shell_length_cm: 85,
      shell_width_cm: 72,
      weight_kg: 65,
    },
    health: {
      status: 'HEALTHY',
      notes: 'Normal kondisyon',
    },
    sightings: [
      {
        id: 's001',
        turtleId: 'turtle-001',
        location: 'Dalyan Plajı',
        dateSighted: '2026-04-28T14:22:00Z',
        observerName: 'Ahmet Yılmaz',
        notes: 'Sol kanat kütlenmiş görülüyor',
        waterTemperature: 18,
        weather: 'Açık',
        waterClarity: 'İyi',
        imageHash: 'hash001',
        imageUrl: placeholderImages[0],
      },
      {
        id: 's002',
        turtleId: 'turtle-001',
        location: 'Ölüdeniz',
        dateSighted: '2026-04-22T10:15:00Z',
        observerName: 'Fatma Kaya',
        notes: 'Sağlıklı görünüş, aktif yüzüş',
        waterTemperature: 19,
        weather: 'Açık',
        waterClarity: 'Mükemmel',
        imageHash: 'hash002',
        imageUrl: placeholderImages[1],
      },
      {
        id: 's003',
        turtleId: 'turtle-001',
        location: 'Patara Plajı',
        dateSighted: '2026-04-15T09:45:00Z',
        observerName: 'Mehmet Demir',
        notes: 'Yavru eşlik etmiyor',
        waterTemperature: 17,
        weather: 'Bulutlu',
        waterClarity: 'Orta',
        imageHash: 'hash003',
        imageUrl: placeholderImages[2],
      },
      {
        id: 's004',
        turtleId: 'turtle-001',
        location: 'Dalyan Plajı',
        dateSighted: '2026-04-08T16:30:00Z',
        observerName: 'Ayşe Şahin',
        notes: 'Sahil yakınında besleniyordu',
        waterTemperature: 16,
        weather: 'Yağışlı',
        waterClarity: 'Zayıf',
        imageHash: 'hash004',
        imageUrl: placeholderImages[3],
      },
      {
        id: 's005',
        turtleId: 'turtle-001',
        location: 'Ekincik Lagünü',
        dateSighted: '2026-03-20T11:00:00Z',
        observerName: 'Ali Çetin',
        notes: 'Görüntü kalitesi %95',
        waterTemperature: 15,
        weather: 'Açık',
        waterClarity: 'Mükemmel',
        imageHash: 'hash005',
        imageUrl: placeholderImages[4],
      },
    ],
  },
  'turtle-002': {
    id: 'turtle-002',
    species: 'LOGGERHEAD',
    biometric_code: '110011001100110011',
    biometric_vector: [0.52, 0.31, 0.72, 0.18, 0.64, 0.85, 0.42, 0.88, 0.59, 0.48],
    registeredAt: '2024-05-20T14:15:00Z',
    lastSightingAt: '2026-04-25T11:30:00Z',
    measurements: {
      shell_length_cm: 72,
      shell_width_cm: 58,
      weight_kg: 45,
    },
    health: {
      status: 'HEALTHY',
      notes: 'İyi kondisyon',
    },
    sightings: [
      {
        id: 's006',
        turtleId: 'turtle-002',
        location: 'Ölüdeniz',
        dateSighted: '2026-04-25T11:30:00Z',
        observerName: 'Fatma Kaya',
        notes: 'Son avistama',
        waterTemperature: 18,
        weather: 'Açık',
        waterClarity: 'Mükemmel',
        imageHash: 'hash006',
        imageUrl: placeholderImages[5],
      },
      {
        id: 's007',
        turtleId: 'turtle-002',
        location: 'Patara Plajı',
        dateSighted: '2026-04-10T13:20:00Z',
        observerName: 'Mehmet Demir',
        notes: 'Aktif yüzüş davranışı',
        waterTemperature: 17,
        weather: 'Bulutlu',
        waterClarity: 'İyi',
        imageHash: 'hash007',
        imageUrl: placeholderImages[6],
      },
    ],
  },
  'turtle-003': {
    id: 'turtle-003',
    species: 'LEATHERBACK',
    biometric_code: '111000111000111000',
    biometric_vector: [0.61, 0.28, 0.79, 0.22, 0.71, 0.92, 0.35, 0.84, 0.63, 0.52],
    registeredAt: '2024-07-10T09:45:00Z',
    lastSightingAt: '2026-04-20T15:45:00Z',
    measurements: {
      shell_length_cm: 95,
      shell_width_cm: 82,
      weight_kg: 85,
    },
    health: {
      status: 'HEALTHY',
      notes: 'Mükemmel kondisyon',
    },
    sightings: [
      {
        id: 's008',
        turtleId: 'turtle-003',
        location: 'Ekincik Lagünü',
        dateSighted: '2026-04-20T15:45:00Z',
        observerName: 'Ali Çetin',
        notes: 'Büyük birey, sağlıklı',
        waterTemperature: 19,
        weather: 'Açık',
        waterClarity: 'Mükemmel',
        imageHash: 'hash008',
        imageUrl: placeholderImages[7],
      },
    ],
  },
}

export async function getTurtleById(id: string): Promise<Turtle | null> {
  // Simulating async API call
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve(mockTurtles[id] || null)
    }, 300)
  })
}

export async function getTurtles(
  filters?: { limit?: number; offset?: number; species?: string }
): Promise<Turtle[]> {
  return new Promise((resolve) => {
    setTimeout(() => {
      let turtles = Object.values(mockTurtles)
      if (filters?.species) {
        turtles = turtles.filter((t) => t.species === filters.species)
      }
      const limit = filters?.limit || 10
      const offset = filters?.offset || 0
      resolve(turtles.slice(offset, offset + limit))
    }, 300)
  })
}

export async function getTurtleSightings(
  turtleId: string,
  limit: number = 10
): Promise<Sighting[]> {
  return new Promise((resolve) => {
    setTimeout(() => {
      const turtle = mockTurtles[turtleId]
      if (!turtle) {
        resolve([])
        return
      }
      resolve(turtle.sightings.slice(0, limit))
    }, 200)
  })
}

export async function getRelatedTurtles(
  biometricCode: string,
  threshold: number = 0.8
): Promise<Array<{ turtle: Turtle; similarity: number }>> {
  return new Promise((resolve) => {
    setTimeout(() => {
      // Simple mock: return random similarity scores
      const related = Object.values(mockTurtles)
        .filter((t) => t.biometric_code !== biometricCode)
        .map((t) => ({
          turtle: t,
          similarity: Math.random() * (1 - threshold) + threshold,
        }))
        .sort((a, b) => b.similarity - a.similarity)
        .slice(0, 3)

      resolve(related)
    }, 400)
  })
}

export interface ComparisonResult {
  similarity: number // 0-1
  biometricMatch: number
  measurementsMatch: number
  locationDistance: number // km
  timeDifference: number // days
  verdict: 'SAME' | 'LIKELY_SAME' | 'UNCERTAIN' | 'DIFFERENT'
  reasoning: string[]
}

export async function compareTurtles(turtle1: Turtle, turtle2: Turtle): Promise<ComparisonResult> {
  return new Promise((resolve) => {
    setTimeout(() => {
      // Farklı türse, direkt farklı
      if (turtle1.species !== turtle2.species) {
        resolve({
          similarity: 0,
          biometricMatch: 0,
          measurementsMatch: 0,
          locationDistance: 0,
          timeDifference: 0,
          verdict: 'DIFFERENT',
          reasoning: ['Farklı tür: Kesinlikle farklı bireyler'],
        })
        return
      }

      // Biometric match (biometric code similarity)
      let biometricScore = 0
      const code1 = turtle1.biometric_code.split('')
      const code2 = turtle2.biometric_code.split('')
      const matches = code1.filter((bit, i) => bit === code2[i]).length
      biometricScore = matches / Math.max(code1.length, code2.length)

      // Measurements match
      let measurementsScore = 0
      if (turtle1.measurements && turtle2.measurements) {
        const lengthDiff = Math.abs(turtle1.measurements.shell_length_cm - turtle2.measurements.shell_length_cm)
        const lengthMatch = Math.max(0, 1 - lengthDiff / 100)
        const weightDiff = Math.abs(turtle1.measurements.weight_kg - turtle2.measurements.weight_kg)
        const weightMatch = Math.max(0, 1 - weightDiff / 100)
        measurementsScore = (lengthMatch + weightMatch) / 2
      }

      // Location & time analysis
      const lastSighting1 = turtle1.sightings?.[0]
      const lastSighting2 = turtle2.sightings?.[0]
      let locationDistance = 0
      let timeDifference = 0

      if (lastSighting1 && lastSighting2) {
        // Basit distance simulasyon (gerçekte GPS koordinat hesaplaması olurdu)
        locationDistance = Math.random() * 50
        timeDifference = Math.floor(
          Math.abs(new Date(lastSighting1.dateSighted).getTime() - new Date(lastSighting2.dateSighted).getTime()) /
            (1000 * 60 * 60 * 24)
        )
      }

      // Süreçler
      const reasoning: string[] = []

      // Overall similarity
      let similarity = (biometricScore * 0.5 + measurementsScore * 0.3 + Math.max(0, (50 - locationDistance) / 100) * 0.2) * 0.9 +
        Math.random() * 0.1 // %10 noise

      // Verdict
      let verdict: 'SAME' | 'LIKELY_SAME' | 'UNCERTAIN' | 'DIFFERENT'
      if (similarity >= 0.85) {
        verdict = 'SAME'
        reasoning.push(`✅ Biometrik kod uyumu: ${(biometricScore * 100).toFixed(0)}%`)
        reasoning.push(`✅ Ölçüm uyumu: ${(measurementsScore * 100).toFixed(0)}%`)
        reasoning.push(`✅ Makul konum farkı: ${locationDistance.toFixed(1)}km`)
      } else if (similarity >= 0.70) {
        verdict = 'LIKELY_SAME'
        reasoning.push(`⚠️ İyi biometrik uyumu: ${(biometricScore * 100).toFixed(0)}%`)
        reasoning.push(`⚠️ Ölçüm benzerliği: ${(measurementsScore * 100).toFixed(0)}%`)
        reasoning.push(`ℹ️ Konum farkı: ${locationDistance.toFixed(1)}km`)
      } else if (similarity >= 0.50) {
        verdict = 'UNCERTAIN'
        reasoning.push(`❓ Kısmi biometrik uyumu: ${(biometricScore * 100).toFixed(0)}%`)
        reasoning.push(`❓ Sınırlı ölçüm benzerliği: ${(measurementsScore * 100).toFixed(0)}%`)
      } else {
        verdict = 'DIFFERENT'
        reasoning.push(`❌ Düşük biometrik uyumu: ${(biometricScore * 100).toFixed(0)}%`)
        reasoning.push(`❌ Ölçümleri önemli ölçüde farklı: ${(measurementsScore * 100).toFixed(0)}%`)
      }

      resolve({
        similarity: Math.min(1, Math.max(0, similarity)),
        biometricMatch: biometricScore,
        measurementsMatch: measurementsScore,
        locationDistance,
        timeDifference,
        verdict,
        reasoning,
      })
    }, 600)
  })
}
