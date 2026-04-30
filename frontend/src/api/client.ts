import axios, { type AxiosInstance, type AxiosError } from 'axios'
import { API_BASE_URL } from '../utils/constants'

const createApiClient = (): AxiosInstance => {
  const client = axios.create({
    baseURL: API_BASE_URL,
    timeout: 30000,
    headers: {
      'Content-Type': 'application/json',
    },
  })

  // Request interceptor
  client.interceptors.request.use(
    (config) => {
      // Add auth token if available
      const token = localStorage.getItem('authToken')
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
      return config
    },
    (error) => Promise.reject(error)
  )

  // Response interceptor
  client.interceptors.response.use(
    (response) => response,
    (error: AxiosError) => {
      if (error.response?.status === 401) {
        // Handle unauthorized - redirect to login
        localStorage.removeItem('authToken')
        window.location.href = '/'
      }
      return Promise.reject(error)
    }
  )

  return client
}

export const apiClient = createApiClient()

export default apiClient
