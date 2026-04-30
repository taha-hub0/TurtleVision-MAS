import { apiClient } from '../client'
import type { ApiResponse } from '../../types/api'

export const matchingService = {
  // Find matching turtles
  findMatch: async (
    biometricCode: string,
    criteria?: { threshold?: number; topN?: number; method?: string }
  ): Promise<ApiResponse<any>> => {
    const response = await apiClient.post('/matching/find', {
      biometricCode,
      matchingCriteria: criteria || { threshold: 0.9, topN: 5, method: 'hamming' },
    })
    return response.data
  },

  // Batch matching
  batchMatch: async (
    biometricCodes: string[],
    criteria?: any
  ): Promise<ApiResponse<any>> => {
    const response = await apiClient.post('/matching/batch', {
      biometricCodes,
      matchingCriteria: criteria || { threshold: 0.9 },
    })
    return response.data
  },

  // Check health
  checkHealth: async (): Promise<any> => {
    const response = await apiClient.get('/matching/health')
    return response.data
  },
}

export default matchingService
