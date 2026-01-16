import api from './index'

export interface ViewCode {
  id: number
  code: string
  is_active: boolean
  created_at: string
  expires_at: string | null
  category_ids: number[]
  category_names: string[]
}

export interface ViewCodeCreate {
  code: string
  is_active?: boolean
  expires_at?: string | null
  category_ids?: number[]
}

export interface ViewCodeUpdate {
  is_active?: boolean
  expires_at?: string | null
  category_ids?: number[]
}

export interface ViewCodeVerifyResponse {
  valid: boolean
  category_ids: number[]
  expires_at: string | null
}

export const viewCodesApi = {
  list: () => api.get<ViewCode[]>('/view-codes'),
  create: (data: ViewCodeCreate) => api.post<ViewCode>('/view-codes', data),
  update: (id: number, data: ViewCodeUpdate) => api.put<ViewCode>(`/view-codes/${id}`, data),
  delete: (id: number) => api.delete(`/view-codes/${id}`),
  verify: (code: string) => api.post<ViewCodeVerifyResponse>('/view-codes/verify', { code })
}
