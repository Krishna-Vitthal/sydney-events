import { create } from 'zustand'
import { User } from '../types'
import { authApi } from '../api'

interface AuthState {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  token: string | null
  
  setToken: (token: string) => void
  loadUser: () => Promise<void>
  login: () => Promise<void>
  logout: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isLoading: true,
  isAuthenticated: false,
  token: localStorage.getItem('token'),

  setToken: (token: string) => {
    localStorage.setItem('token', token)
    set({ token, isAuthenticated: true })
  },

  loadUser: async () => {
    const token = localStorage.getItem('token')
    if (!token) {
      set({ isLoading: false, isAuthenticated: false, user: null })
      return
    }

    try {
      const user = await authApi.getCurrentUser()
      set({ user, isAuthenticated: true, isLoading: false })
    } catch (error) {
      localStorage.removeItem('token')
      set({ user: null, isAuthenticated: false, isLoading: false, token: null })
    }
  },

  login: async () => {
    const authUrl = await authApi.getLoginUrl()
    window.location.href = authUrl
  },

  logout: () => {
    localStorage.removeItem('token')
    set({ user: null, isAuthenticated: false, token: null })
  },
}))
