import api from './index'

export interface ThumbnailResponse {
  video_id: number
  thumbnail_url: string
}

export interface CaptureAtRequest {
  timestamp: number
}

export const thumbnailApi = {
  // Auto capture thumbnail from video (at default position)
  autoCapture: (videoId: number) =>
    api.post<ThumbnailResponse>(`/videos/${videoId}/thumbnail/auto`),

  // Upload custom thumbnail
  upload: (videoId: number, file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post<ThumbnailResponse>(`/videos/${videoId}/thumbnail/upload`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 60000
    })
  },

  // Capture thumbnail at specific timestamp (in seconds)
  captureAt: (videoId: number, timestamp: number) =>
    api.post<ThumbnailResponse>(`/videos/${videoId}/thumbnail/capture`, { timestamp })
}
