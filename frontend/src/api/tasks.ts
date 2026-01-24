import api from './index'

export interface Task {
  id: number
  source_id: number
  status: 'pending' | 'recording' | 'completed' | 'failed' | 'interrupted'
  started_at: string | null
  ended_at: string | null
  file_path: string | null
  file_size: number | null
  duration: number | null
  error_message: string | null
  created_at: string
  source_name?: string
  source?: {
    id: number
    name: string
    category?: {
      id: number
      name: string
      sort_order: number
    }
  }
}

export const tasksApi = {
  list: () => api.get<Task[]>('/tasks'),
  get: (id: number) => api.get<Task>(`/tasks/${id}`),
  startRecording: (sourceId: number) => api.post<Task>(`/sources/${sourceId}/record/start`),
  stopRecording: (sourceId: number) => api.post<Task>(`/sources/${sourceId}/record/stop`)
}
