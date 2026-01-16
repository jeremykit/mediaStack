import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

api.interceptors.request.use((config) => {
  const auth = useAuthStore()
  if (auth.token) {
    config.headers.Authorization = `Bearer ${auth.token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      const auth = useAuthStore()
      auth.logout()
      window.location.href = '/login'
    } else if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
      ElMessage.error('请求超时，请检查网络连接')
    } else if (!error.response) {
      ElMessage.error('网络连接失败，请检查网络设置')
    }
    return Promise.reject(error)
  }
)

export default api
