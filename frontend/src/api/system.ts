import api from './index'

export interface SystemStatus {
  cpu_percent: number
  memory_percent: number
  disk_total: number
  disk_used: number
  disk_free: number
  disk_percent: number
}

export const systemApi = {
  getStatus: () => api.get<SystemStatus>('/system/status')
}
