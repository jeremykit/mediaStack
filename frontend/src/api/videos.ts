import api from './index'

export interface VideoCategory {
  id: number
  name: string
  sort_order: number
}

export interface VideoTag {
  id: number
  name: string
}

export interface Video {
  id: number
  task_id: number | null
  category_id: number | null
  title: string
  file_path: string
  file_size: number | null
  duration: number | null
  thumbnail: string | null
  view_count: number
  source_type: 'recorded' | 'uploaded'
  file_type: 'video' | 'audio'
  created_at: string
  category: VideoCategory | null
  tags: VideoTag[]
}

export interface VideoPlay {
  hls_url: string
}

export interface VideoListParams {
  search?: string
  category_id?: number
  tag_ids?: string
  skip?: number
  limit?: number
}

export const videosApi = {
  list: (params?: VideoListParams) =>
    api.get<Video[]>('/videos', { params }),
  get: (id: number) => api.get<Video>(`/videos/${id}`),
  update: (id: number, data: { title?: string }) => api.put<Video>(`/videos/${id}`, data),
  delete: (id: number) => api.delete(`/videos/${id}`),
  getPlayUrl: (id: number) => api.get<VideoPlay>(`/videos/${id}/play`),
  incrementView: (id: number) => api.post(`/videos/${id}/view`),
  setCategory: (id: number, categoryId: number | null) =>
    api.put<Video>(`/videos/${id}/category`, { category_id: categoryId }),
  setTags: (id: number, tagIds: number[]) =>
    api.put<Video>(`/videos/${id}/tags`, { tag_ids: tagIds })
}
