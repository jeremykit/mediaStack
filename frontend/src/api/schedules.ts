import api from './index'

export interface Schedule {
  id: number
  source_id: number
  cron_expr: string
  is_active: boolean
  last_run_at: string | null
  next_run_at: string | null
  created_at: string
  source_name?: string
}

export interface ScheduleCreate {
  source_id: number
  cron_expr: string
  is_active?: boolean
}

export interface ScheduleUpdate {
  cron_expr?: string
  is_active?: boolean
}

export const schedulesApi = {
  list: () => api.get<Schedule[]>('/schedules'),
  create: (data: ScheduleCreate) => api.post<Schedule>('/schedules', data),
  update: (id: number, data: ScheduleUpdate) => api.put<Schedule>(`/schedules/${id}`, data),
  delete: (id: number) => api.delete(`/schedules/${id}`)
}
