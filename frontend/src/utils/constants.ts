// API Base Configuration
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000/api'

// Thresholds & Constants
export const SIMILARITY_THRESHOLD = 0.9 // 90%
export const CONFIDENCE_THRESHOLD = 0.85 // 85%
export const SIMILAR_MATCH_THRESHOLD = 0.7 // 70%

// File Upload
export const MAX_FILE_SIZE = 50 * 1024 * 1024 // 50MB
export const ACCEPTED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp']
export const ACCEPTED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp']

// Timeouts (ms)
export const IMAGE_ANALYSIS_TIMEOUT = 30000 // 30s
export const DB_AGENT_TIMEOUT = 10000 // 10s
export const GENERAL_TIMEOUT = 5000 // 5s

// Species Options
export const TURTLE_SPECIES = [
  { value: 'GREEN_TURTLE', label: 'Yeşil Kaplumbağa (Chelonia mydas)', color: 'bg-green-500' },
  { value: 'LEATHERBACK', label: 'Deri Sırtlı (Dermochelys coriacea)', color: 'bg-blue-500' },
  { value: 'LOGGERHEAD', label: 'Başköpek (Caretta caretta)', color: 'bg-orange-500' },
  { value: 'HAWKSBILL', label: 'Şahin Gagalı (Eretmochelys imbricata)', color: 'bg-red-500' },
] as const

// Weather Options
export const WEATHER_OPTIONS = ['sunny', 'cloudy', 'rainy', 'stormy'] as const

// Water Clarity Options
export const WATER_CLARITY_OPTIONS = ['clear', 'turbid', 'murky'] as const

// Health Conditions
export const HEALTH_CONDITIONS = ['GOOD', 'FAIR', 'POOR', 'UNKNOWN'] as const

// Extraction Methods
export const EXTRACTION_METHODS = {
  GREEN_TURTLE: 'post_ocular_scutes',
  LEATHERBACK: 'pineal_spot',
  LOGGERHEAD: 'carapace_pattern',
  HAWKSBILL: 'shell_ridges',
} as const

// Error Messages
export const ERROR_MESSAGES = {
  IMAGE_TOO_LARGE: 'Görüntü dosyası çok büyük (Max 50MB)',
  INVALID_IMAGE_TYPE: 'Geçersiz görüntü formatı (JPG, PNG, WebP)',
  INVALID_GPS: 'Geçersiz GPS koordinatları',
  NETWORK_ERROR: 'Ağ hatası. Lütfen bağlantınızı kontrol edin.',
  AGENT_TIMEOUT: 'Agent yanıt vermiyor. Lütfen tekrar deneyin.',
  VALIDATION_FAILED: 'Metadata doğrulaması başarısız.',
  ANALYSIS_FAILED: 'Görüntü analizi başarısız.',
} as const

// Success Messages
export const SUCCESS_MESSAGES = {
  VALIDATION_SUCCESS: 'Metadata başarıyla doğrulandı.',
  ANALYSIS_SUCCESS: 'Analiz tamamlandı.',
  REGISTRATION_SUCCESS: 'Kaplumbağa başarıyla kaydedildi.',
  MATCHING_SUCCESS: 'Eşleştirme tamamlandı.',
} as const

// Navigation Routes
export const ROUTES = {
  HOME: '/',
  DASHBOARD: '/dashboard',
  IDENTIFICATION: '/identification',
  RESULTS: '/results',
  TURTLE_PROFILE: '/turtle/:id',
  TIMELINE: '/turtle/:id/timeline',
} as const

// Processing Steps
export const PROCESSING_STEPS = [
  { id: 'validation', label: 'Doğrulama', order: 1 },
  { id: 'analysis', label: 'Analiz', order: 2 },
  { id: 'matching', label: 'Eşleştirme', order: 3 },
  { id: 'reporting', label: 'Rapor', order: 4 },
] as const

// Pagination
export const DEFAULT_LIMIT = 50
export const DEFAULT_OFFSET = 0
