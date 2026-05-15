
import axios from 'axios'
import type { PredictRequest, PredictResponse, RecoRequest, RecoResponse } from '../types/energy'
 
// ── Instancia de Axios con configuracion base ─────────────────────────
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',          // el proxy de Vite lo redirige al gateway
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,         
})
 
// ── Interceptor de errores global ─────────────────────────────────────
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.code === 'ECONNREFUSED') {
      throw new Error('No se puede conectar al servidor. Verifica que Docker este corriendo.')
    }
    if (error.response?.status === 422) {
      throw new Error('Datos invalidos. Revisa que todos los campos esten completos.')
    }
    if (error.response?.status === 500) {
      throw new Error('Error interno del servidor. El modelo puede no estar en Production.')
    }
    throw error
  }
)
 
// ── Endpoint 1: prediccion de consumo ─────────────────────────────────
export async function predictConsumo(data: PredictRequest): Promise<PredictResponse> {
  const response = await api.post<PredictResponse>('/predict', data)
  return response.data
}
 
// ── Endpoint 2: recomendaciones con IA ───────────────────────────────
export async function getRecomendaciones(data: RecoRequest): Promise<RecoResponse> {
  const response = await api.post<RecoResponse>('/recommendations', data)
  return response.data
}
 
// ── Endpoint 3: health check ──────────────────────────────────────────
export async function checkHealth(): Promise<boolean> {
  try {
    await api.get('/health')
    return true
  } catch {
    return false
  }
}
