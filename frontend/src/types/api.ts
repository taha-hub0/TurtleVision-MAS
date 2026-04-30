export interface ApiResponse<T = any> {
  success?: boolean
  data?: T
  error?: string
  message?: string
  requestId?: string
  timestamp?: string
  details?: any
}

export interface HealthStatus {
  coordinator: 'OK' | 'FAILED'
  imageAnalysisAgent: 'OK' | 'FAILED'
  databaseAgent: 'OK' | 'FAILED'
  timestamp: string
  allAgentsHealthy: boolean
}

export interface PaginationParams {
  limit?: number
  offset?: number
  filter?: {
    location?: string
    species?: string
  }
}

export interface ValidationResponse {
  success: boolean
  validated_metadata?: any
  errors?: string[]
  warnings?: string[]
  requestId?: string
}
