import { useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'

export default function AuthCallback() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const { setToken, loadUser } = useAuthStore()

  useEffect(() => {
    const token = searchParams.get('token')
    
    if (token) {
      setToken(token)
      loadUser().then(() => {
        navigate('/dashboard', { replace: true })
      })
    } else {
      navigate('/', { replace: true })
    }
  }, [searchParams, setToken, loadUser, navigate])

  return (
    <div className="min-h-[60vh] flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin h-12 w-12 border-4 border-primary-500 border-t-transparent rounded-full mx-auto mb-4" />
        <h2 className="text-xl font-semibold text-gray-900 mb-2">
          Signing you in...
        </h2>
        <p className="text-gray-500">Please wait while we complete authentication.</p>
      </div>
    </div>
  )
}
