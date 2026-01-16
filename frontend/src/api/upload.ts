import api from './index'

export interface UploadInitRequest {
  filename: string
  file_size: number
  chunk_size?: number
}

export interface UploadInitResponse {
  task_id: string
  chunk_size: number
  total_chunks: number
}

export interface UploadStatusResponse {
  task_id: string
  filename: string
  file_size: number
  chunk_size: number
  total_chunks: number
  uploaded_chunks: number
  status: 'uploading' | 'completed' | 'failed'
  uploaded_chunk_indices: number[]
  created_at: string
}

export interface UploadCompleteRequest {
  title?: string
  category_id?: number
  tag_ids?: number[]
}

export interface UploadChunkResponse {
  chunk_index: number
  uploaded_chunks: number
  total_chunks: number
}

export const uploadApi = {
  init: (data: UploadInitRequest) => api.post<UploadInitResponse>('/upload/init', data),
  uploadChunk: (taskId: string, chunkIndex: number, chunk: Blob) => {
    const formData = new FormData()
    formData.append('chunk_index', chunkIndex.toString())
    formData.append('chunk', chunk)
    return api.post<UploadChunkResponse>(`/upload/${taskId}/chunk`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 60000 // 60 seconds for chunk upload
    })
  },
  getStatus: (taskId: string) => api.get<UploadStatusResponse>(`/upload/${taskId}/status`),
  complete: (taskId: string, data?: UploadCompleteRequest) =>
    api.post(`/upload/${taskId}/complete`, data || {}),
  cancel: (taskId: string) => api.delete(`/upload/${taskId}`)
}
