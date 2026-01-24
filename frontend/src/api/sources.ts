import api from './index'

export interface Source {
  id: number
  name: string
  protocol: 'rtmp' | 'hls'
  url: string
  retention_days: number
  is_active: boolean
  is_online: boolean
  last_check_time: string | null
  is_recording: boolean
  created_at: string
  updated_at: string
  category?: {
    id: number
    name: string
    sort_order: number
  }
}

export interface SourceCreate {
  name: string
  protocol: 'rtmp' | 'hls'
  url: string
  retention_days?: number
  is_active?: boolean
  category_id?: number
}

export interface SourceUpdate {
  name?: string
  protocol?: 'rtmp' | 'hls'
  url?: string
  retention_days?: number
  is_active?: boolean
  category_id?: number
}

export interface SourceStatus {
  online: boolean
  message: string
}

export const sourcesApi = {
  list: () => api.get<Source[]>('/sources'),
  get: (id: number) => api.get<Source>(`/sources/${id}`),
  create: (data: SourceCreate) => api.post<Source>('/sources', data),
  update: (id: number, data: SourceUpdate) => api.put<Source>(`/sources/${id}`, data),
  delete: (id: number) => api.delete(`/sources/${id}`),
  checkStatus: (id: number) => api.get<SourceStatus>(`/sources/${id}/status`),
  bulkUpdateCategory: (sourceIds: number[], categoryId: number) =>
    api.post('/sources/bulk-update-category', {
      source_ids: sourceIds,
      category_id: categoryId
    })
}
