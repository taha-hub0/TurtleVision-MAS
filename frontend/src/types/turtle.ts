// Turtle related types
export interface Turtle {
  id: string
  species: 'GREEN_TURTLE' | 'LEATHERBACK' | 'LOGGERHEAD' | 'HAWKSBILL'
  biometric_code: string
  biometric_vector?: number[]
  location: {
    latitude: number
    longitude: number
    accuracy?: number
  }
  registeredAt: string
  lastSightings?: Sighting[]
  sightingsCount: number
  measurements?: {
    shell_length: number
    shell_width: number
    weight: number
  }
  health?: {
    wounds: string[]
    diseases: string[]
    parasites: string[]
    condition: 'HEALTHY' | 'INJURED' | 'ILL'
  }
  metadata?: Record<string, any>
}

export interface Sighting {
  id: string
  turtleId: string
  location: {
    latitude: number
    longitude: number
  }
  dateSighted: string
  observerName: string
  notes?: string
  imageHash?: string
  waterTemperature?: number
  weather?: string
  waterClarity?: string
}

export interface AnalysisResult {
  success: boolean
  species: string
  confidence: number
  turtle_type: string
  biometric_code: string
  biometric_vector?: number[]
  features?: Array<{ name: string; value: number }>
  quality_score: number
  extraction_method: string
  measurements?: {
    shell_length: number
    shell_width: number
    weight: number
  }
  health?: {
    wounds: string[]
    diseases: string[]
    parasites: string[]
    condition: string
  }
  error?: string
}

export interface MatchingResult {
  success: boolean
  classification: 'EXISTING_RECORD' | 'NEW_INDIVIDUAL'
  matches: Array<{
    turtleId: string
    species: string
    recordedAt: string
    similarity: number
  }>
  topMatch?: {
    turtleId: string
    species: string
    recordedAt: string
    similarity: number
    sightings_count?: number
  }
  confidence: number
  threshold: number
  matchMethod: 'hamming' | 'cosine'
}

export interface ProcessingStep {
  id: 'validation' | 'analysis' | 'matching' | 'reporting'
  label: string
  status: 'pending' | 'processing' | 'success' | 'error'
  data?: any
  error?: string
  duration?: number
}

export interface Report {
  report_id: string
  timestamp: string
  observation: {
    captured_at: string
    location: { latitude: number; longitude: number; accuracy_m: number }
    observer: { name: string; email: string; organization?: string }
    conditions?: { waterTemperature: number; weather: string; waterClarity: string }
  }
  biological_analysis: {
    species: string
    confidence: number
    biometric_code: string
    extraction_method: string
    quality_score: number
  }
  matching_result: MatchingResult
  matched_individual?: {
    turtle_id: string
    first_recorded: string
    similarity_score: number
    previous_sightings_count: number
  }
  methodology: any
  conclusions: {
    primary_finding: string
    conservation_value: string
    recommended_actions: string[]
  }
  quality_metrics: {
    image_quality: number
    analysis_confidence: number
    matching_confidence: number
    overall_reliability: number
  }
}

export interface IdentificationSession {
  id: string
  imageBase64: string
  species?: string
  metadata?: {
    timestamp: string
    location?: { latitude: number; longitude: number; accuracy?: number }
    observer?: { name: string; email: string; organization?: string }
    conditions?: { waterTemperature?: number; weather?: string; waterClarity?: string }
  }
  analysisResult?: AnalysisResult
  matchingResult?: MatchingResult
  report?: Report
  processingSteps: ProcessingStep[]
  createdAt: string
}
