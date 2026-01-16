import api from './index'

export interface Category {
  id: number
  name: string
  sort_order: number
  created_at: string
  video_count: number
}

export interface CategoryCreate {
  name: string
  sort_order?: number
}

export interface CategoryUpdate {
  name?: string
  sort_order?: number
}

export const categoriesApi = {
  list: () => api.get<Category[]>('/categories'),
  create: (data: CategoryCreate) => api.post<Category>('/categories', data),
  update: (id: number, data: CategoryUpdate) => api.put<Category>(`/categories/${id}`, data),
  delete: (id: number) => api.delete(`/categories/${id}`)
}
