import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api/axios'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  const accessToken = ref(localStorage.getItem('access_token') || null)
  const refreshToken = ref(localStorage.getItem('refresh_token') || null)
  const loading = ref(false)
  const error = ref(null)

  // Getters
  const isAuthenticated = computed(() => !!accessToken.value)
  const userRole = computed(() => user.value?.role || null)
  const userName = computed(() => user.value?.full_name || user.value?.username || '')
  const isSuperAdmin = computed(() => user.value?.role === 'superadmin')

  // Actions
  async function login(empleadoId, password) {
    loading.value = true
    error.value = null

    try {
      const { data } = await api.post('/auth/login/', {
        empleado_id: empleadoId,
        password: password,
      })

      // Store tokens and user data
      accessToken.value = data.access
      refreshToken.value = data.refresh
      user.value = data.user

      localStorage.setItem('access_token', data.access)
      localStorage.setItem('refresh_token', data.refresh)
      localStorage.setItem('user', JSON.stringify(data.user))

      return { success: true }
    } catch (err) {
      const message =
        err.response?.data?.detail ||
        err.response?.data?.non_field_errors?.[0] ||
        'Error de conexión con el servidor.'
      error.value = message
      return { success: false, message }
    } finally {
      loading.value = false
    }
  }

  function logout() {
    user.value = null
    accessToken.value = null
    refreshToken.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
  }

  return {
    user,
    accessToken,
    refreshToken,
    loading,
    error,
    isAuthenticated,
    userRole,
    userName,
    isSuperAdmin,
    login,
    logout,
  }
})
