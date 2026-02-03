import { Routes, Route } from 'react-router-dom'
import { useEffect } from 'react'
import Layout from './components/Layout'
import HomePage from './pages/HomePage'
import DashboardPage from './pages/DashboardPage'
import AuthCallback from './pages/AuthCallback'
import { useAuthStore } from './store/authStore'

function App() {
  const { loadUser } = useAuthStore()

  useEffect(() => {
    loadUser()
  }, [loadUser])

  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<HomePage />} />
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="auth/callback" element={<AuthCallback />} />
      </Route>
    </Routes>
  )
}

export default App
