import api from './index'

export type AudioTaskStatus = 'pending' | 'processing' | 'completed' | 'failed'

export interface AudioTask {
  id: number
  video_id: number
  status: AudioTaskStatus
  output_path: string | null
  format: string
  bitrate: string
  created_at: string
  completed_at: string | null
}

export interface AudioInfo {
  has_audio: boolean
  task: AudioTask | null
  download_url: string | null
  file_size: number | null
}

export interface ExtractAudioRequest {
  format?: string
  bitrate?: string
}

export interface ExtractAudioResponse {
  task_id: number
  status: AudioTaskStatus
  message: string
}

export const audioApi = {
  // Extract audio from video
  extractAudio: (videoId: number, format?: string, bitrate?: string) => {
    const data: ExtractAudioRequest = {}
    if (format) data.format = format
    if (bitrate) data.bitrate = bitrate
    return api.post<ExtractAudioResponse>(`/videos/${videoId}/extract-audio`, data)
  },

  // Get audio info and task status
  getAudioInfo: (videoId: number) =>
    api.get<AudioInfo>(`/videos/${videoId}/audio`),

  // Get download URL (returns the URL string, not an API call)
  getDownloadUrl: (videoId: number) =>
    `/api/videos/${videoId}/audio/download`
}
