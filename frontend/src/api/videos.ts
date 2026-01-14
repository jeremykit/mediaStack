import api from './index'

export interface Video {
  id: number
  task_id: number | null
  title: string
  file_path: string
  file_size: number | null
  duration: number | null
  thumbnail: string | null
  view_count: number
  source_type: 'recorded' | 'uploaded'
  created_at: string
}

export interface VideoPlay {
  hls_url: string
}

export const videosApi = {
  list: (params?: { search?: string; skip?: number; limit?: number }) =>
    api.get<Video[]>('/videos', { params }),
  get: (id: number) => api.get<Video>(`/videos/${id}`),
  update: (id: number, data: { title?: string }) => api.put<Video>(`/videos/${id}`, data),
  delete: (id: number) => api.delete(`/videos/${id}`),
  getPlayUrl: (id: number) => api.get<VideoPlay>(`/videos/${id}/play`),
  incrementView: (id: number) => api.post(`/videos/${id}/view`)
}
