import axios from 'axios'
import { EventListResponse, Event, DashboardStats, TicketLead, EventFilter, User } from '../types'

const API_BASE = '/api'

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Auth API
export const authApi = {
  getLoginUrl: async () => {
    const response = await api.get<{ auth_url: string }>('/auth/google/login')
    return response.data.auth_url
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await api.get<User>('/auth/me')
    return response.data
  },

  logout: async () => {
    localStorage.removeItem('token')
    await api.post('/auth/logout')
  },
}

// Events API
export const eventsApi = {
  getEvents: async (filters: EventFilter = {}): Promise<EventListResponse> => {
    const params = new URLSearchParams()
    if (filters.city) params.append('city', filters.city)
    if (filters.keyword) params.append('keyword', filters.keyword)
    if (filters.date_from) params.append('date_from', filters.date_from)
    if (filters.date_to) params.append('date_to', filters.date_to)
    if (filters.status) params.append('status', filters.status)
    if (filters.source) params.append('source', filters.source)
    if (filters.page) params.append('page', filters.page.toString())
    if (filters.per_page) params.append('per_page', filters.per_page.toString())

    const response = await api.get<EventListResponse>(`/events/?${params.toString()}`)
    return response.data
  },

  getEvent: async (id: number): Promise<Event> => {
    const response = await api.get<Event>(`/events/${id}`)
    return response.data
  },

  getSources: async (): Promise<string[]> => {
    const response = await api.get<{ sources: string[] }>('/events/sources')
    return response.data.sources
  },

  getStats: async (): Promise<DashboardStats> => {
    const response = await api.get<DashboardStats>('/events/stats')
    return response.data
  },

  createTicketLead: async (lead: TicketLead) => {
    const response = await api.post('/events/ticket-lead', lead)
    return response.data
  },

  importEvent: async (eventId: number, notes?: string) => {
    const response = await api.post(`/events/${eventId}/import`, { event_id: eventId, notes })
    return response.data
  },

  unimportEvent: async (eventId: number) => {
    const response = await api.delete(`/events/${eventId}/import`)
    return response.data
  },
}

// Scraper API
export const scraperApi = {
  runScrapers: async () => {
    const response = await api.post('/scraper/run')
    return response.data
  },

  getStatus: async () => {
    const response = await api.get('/scraper/status')
    return response.data
  },

  getLogs: async () => {
    const response = await api.get('/scraper/logs')
    return response.data
  },
}

export default api
