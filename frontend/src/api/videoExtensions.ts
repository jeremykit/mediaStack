import api from './index'

// Video Image
export interface VideoImage {
  id: number
  video_id: number
  image_path: string
  image_url: string
  sort_order: number
  created_at: string
}

// Video Text
export interface VideoText {
  id: number
  video_id: number
  title: string
  content: string
  sort_order: number
  created_at: string
}

// Video Link
export interface VideoLink {
  id: number
  video_id: number
  title: string
  url: string
  sort_order: number
  created_at: string
}

export interface CreateTextRequest {
  title: string
  content: string
  sort_order?: number
}

export interface UpdateTextRequest {
  title?: string
  content?: string
  sort_order?: number
}

export interface CreateLinkRequest {
  title: string
  url: string
  sort_order?: number
}

export interface UpdateLinkRequest {
  title?: string
  url?: string
  sort_order?: number
}

export const videoExtensionsApi = {
  // Images
  listImages: (videoId: number) =>
    api.get<VideoImage[]>(`/videos/${videoId}/images`),

  uploadImage: (videoId: number, file: File, sortOrder?: number) => {
    const formData = new FormData()
    formData.append('file', file)
    if (sortOrder !== undefined) {
      formData.append('sort_order', sortOrder.toString())
    }
    return api.post<VideoImage>(`/videos/${videoId}/images`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 60000
    })
  },

  deleteImage: (videoId: number, imageId: number) =>
    api.delete(`/videos/${videoId}/images/${imageId}`),

  // Texts
  listTexts: (videoId: number) =>
    api.get<VideoText[]>(`/videos/${videoId}/texts`),

  createText: (videoId: number, data: CreateTextRequest) =>
    api.post<VideoText>(`/videos/${videoId}/texts`, data),

  updateText: (videoId: number, textId: number, data: UpdateTextRequest) =>
    api.put<VideoText>(`/videos/${videoId}/texts/${textId}`, data),

  deleteText: (videoId: number, textId: number) =>
    api.delete(`/videos/${videoId}/texts/${textId}`),

  // Links
  listLinks: (videoId: number) =>
    api.get<VideoLink[]>(`/videos/${videoId}/links`),

  createLink: (videoId: number, data: CreateLinkRequest) =>
    api.post<VideoLink>(`/videos/${videoId}/links`, data),

  deleteLink: (videoId: number, linkId: number) =>
    api.delete(`/videos/${videoId}/links/${linkId}`)
}
