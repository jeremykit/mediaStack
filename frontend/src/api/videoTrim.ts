import api from './index'

export type TrimTaskStatus = 'pending' | 'processing' | 'completed' | 'failed'

export interface TrimTask {
  id: number
  video_id: number
  status: TrimTaskStatus
  start_time: number
  end_time: number
  extract_audio: boolean
  keep_original: boolean
  audio_bitrate: string
  trimmed_video_path: string | null
  extracted_audio_path: string | null
  created_at: string
  completed_at: string | null
  error_message: string | null
}

export interface TrimVideoRequest {
  start_time: number
  end_time: number
  extract_audio: boolean
  keep_original: boolean
}

export const videoTrimApi = {
  // Start trimming a video
  trimVideo: (videoId: number, data: TrimVideoRequest) =>
    api.post<TrimTask>(`/videos/${videoId}/trim`, data),

  // Get all trim tasks for a video
  getTrimTasks: (videoId: number) =>
    api.get<TrimTask[]>(`/videos/${videoId}/trim/tasks`),

  // Get a specific trim task by ID (for polling)
  getTrimTask: (taskId: number) =>
    api.get<TrimTask>(`/videos/trim/tasks/${taskId}`),

  // Cancel an ongoing trim task
  cancelTrimTask: (taskId: number) =>
    api.delete(`/videos/trim/tasks/${taskId}`)
}
