import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000  // 默认超时 30 秒
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
    } else if (error.code === 'ECONNABORTED') {
      // 超时错误，标记为已处理
      error.__handled = true
      ElMessage.error('请求超时，请检查网络连接')
    } else if (!error.response && error.code !== 'ERR_CANCELED') {
      // 网络错误（不包括用户取消），标记为已处理
      error.__handled = true
      ElMessage.error('网络连接失败，请检查网络设置')
    }
    return Promise.reject(error)
  }
)

export default api
