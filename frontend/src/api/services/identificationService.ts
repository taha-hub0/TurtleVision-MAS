import { apiClient } from '../client'
import type { ApiResponse, ValidationResponse } from '../../types/api'

export const identificationService = {
  // Validate metadata (Gatekeeper)
  validateMetadata: async (data: any): Promise<ValidationResponse> => {
    const response = await apiClient.post<ValidationResponse>('/validation/validate', data)
    return response.data
  },

  // Identify turtle from image
  identifyTurtle: async (imageBase64: string, metadata: any): Promise<ApiResponse<any>> => {
    const response = await apiClient.post('/identification/identify', {
      imageBase64,
      metadata,
    })
    return response.data
  },

  // Register identified turtle
  registerTurtle: async (data: any): Promise<ApiResponse<any>> => {
    const response = await apiClient.post('/identification/register', data)
    return response.data
  },

  // Validate health
  validateHealth: async (): Promise<any> => {
    const response = await apiClient.get('/validation/health')
    return response.data
  },
}

export default identificationService
