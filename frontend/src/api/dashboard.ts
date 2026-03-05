import api from './index'

// ============= Dashboard Overview Types =============

export interface RecordingTaskInfo {
  id: number
  source_name: string
  started_at: string
  duration: number  // seconds
}

export interface SourceStats {
  total: number
  online: number
  offline: number
  recording: number
}

export interface SystemStats {
  cpu_percent: number
  memory_percent: number
  disk_percent: number
}

export interface DashboardOverview {
  recording_tasks: RecordingTaskInfo[]
  recording_count: number
  pending_video_count: number
  sources: SourceStats
  system: SystemStats
}

// ============= Dashboard Statistics Types =============

export interface CategoryStorageInfo {
  name: string
  count: number
  size: number  // bytes
}

export interface StorageStats {
  total_files: number
  total_size: number  // bytes
  by_category: CategoryStorageInfo[]
}

export type TrafficPeriod = 'today' | 'week' | 'month'

export interface TrafficStats {
  period: TrafficPeriod
  video_views: number
  audio_views: number
  video_downloads: number
  audio_downloads: number
}

export interface DashboardStatistics {
  storage: StorageStats
  traffic_by_period: TrafficStats[]
}

// ============= Dashboard Activity Types =============

export interface RecentTaskInfo {
  id: number
  source_name: string
  status: string
  completed_at: string
  duration: number  // seconds
  file_size: number  // bytes
}

export interface UpcomingScheduleInfo {
  id: number
  source_name: string
  next_run: string
  cron_expression: string
}

export interface DashboardActivity {
  recent_tasks: RecentTaskInfo[]
  upcoming_schedules: UpcomingScheduleInfo[]
}

// ============= Dashboard API Client =============

export const dashboardApi = {
  // Get dashboard overview statistics
  getOverview: () => api.get<DashboardOverview>('/admin/dashboard/overview'),

  // Get dashboard statistics (storage and traffic)
  getStatistics: () => api.get<DashboardStatistics>('/admin/dashboard/statistics'),

  // Get dashboard activity (recent tasks and upcoming schedules)
  getActivity: () => api.get<DashboardActivity>('/admin/dashboard/activity')
}
