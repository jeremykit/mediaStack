import api from './index'

export interface Tag {
  id: number
  name: string
  created_at: string
  video_count: number
}

export interface TagCreate {
  name: string
}

export const tagsApi = {
  list: () => api.get<Tag[]>('/tags'),
  create: (data: TagCreate) => api.post<Tag>('/tags', data),
  delete: (id: number) => api.delete(`/tags/${id}`)
}
