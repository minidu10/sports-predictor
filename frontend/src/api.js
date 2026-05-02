import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000',
})

export const predictCricket = (data) => api.post('/api/predict/cricket', data)
export const predictFootball = (data) => api.post('/api/predict/football', data)
