<template>
  <div class="recent-activity-card" @click="navigateToTasks">
    <div class="card-header">
      <div class="header-icon">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 8V12L15 15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          <circle cx="12" cy="12" r="8" stroke="currentColor" stroke-width="2"/>
        </svg>
      </div>
      <div class="header-title">
        <h3>近期活动</h3>
        <span class="count">{{ tasks.length }}</span>
      </div>
      <div class="header-arrow">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M9 18L15 12L9 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
    </div>

    <div class="card-content">
      <div v-if="tasks.length === 0" class="empty-state">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M9 12H15M12 9V15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          <circle cx="12" cy="12" r="8" stroke="currentColor" stroke-width="2" stroke-dasharray="4 4"/>
        </svg>
        <p>暂无最近活动</p>
      </div>

      <div v-else class="task-list">
        <div
          v-for="task in displayTasks"
          :key="task.id"
          class="task-item"
        >
          <div class="task-indicator" :class="getStatusClass(task.status)"></div>
          <div class="task-info">
            <div class="task-name">{{ task.source_name }}</div>
            <div class="task-meta">
              <span class="completion-time">{{ formatCompletionTime(task.completed_at) }}</span>
              <span class="duration">{{ formatDuration(task.duration) }}</span>
              <span class="file-size">{{ formatFileSize(task.file_size) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import type { RecentTaskInfo } from '@/api/dashboard'

interface Props {
  tasks: RecentTaskInfo[]
}

const props = defineProps<Props>()
const router = useRouter()

// Display up to 5 tasks
const displayTasks = computed(() => {
  return props.tasks.slice(0, 5)
})

const formatCompletionTime = (dateString: string): string => {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) {
    return '刚刚'
  } else if (diffMins < 60) {
    return `${diffMins}分钟前`
  } else if (diffHours < 24) {
    return `${diffHours}小时前`
  } else if (diffDays < 7) {
    return `${diffDays}天前`
  } else {
    // Show actual date for older tasks
    const month = (date.getMonth() + 1).toString().padStart(2, '0')
    const day = date.getDate().toString().padStart(2, '0')
    return `${month}-${day}`
  }
}

const formatDuration = (seconds: number): string => {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)

  if (hours > 0) {
    return `${hours}小时${minutes}分`
  }
  return `${minutes}分钟`
}

const formatFileSize = (bytes: number): string => {
  const mb = bytes / (1024 * 1024)
  if (mb < 1) {
    return `${(bytes / 1024).toFixed(1)}KB`
  } else if (mb < 1024) {
    return `${mb.toFixed(1)}MB`
  } else {
    return `${(mb / 1024).toFixed(1)}GB`
  }
}

const getStatusClass = (status: string): string => {
  switch (status) {
    case 'completed':
      return 'completed'
    case 'failed':
      return 'failed'
    case 'interrupted':
      return 'interrupted'
    default:
      return ''
  }
}

const navigateToTasks = () => {
  router.push('/admin/tasks')
}
</script>

<style scoped>
.recent-activity-card {
  background: rgba(15, 20, 35, 0.6);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.recent-activity-card:hover {
  border-color: rgba(233, 69, 96, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(233, 69, 96, 0.15);
}

/* Card Header */
.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.header-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: rgba(139, 92, 246, 0.15);
  color: #8B5CF6;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.header-icon svg {
  width: 20px;
  height: 20px;
}

.header-title {
  flex: 1;
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.header-title h3 {
  font-size: 16px;
  font-weight: 600;
  color: #fff;
  margin: 0;
}

.header-title .count {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.5);
}

.header-arrow {
  color: rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
}

.recent-activity-card:hover .header-arrow {
  color: rgba(255, 255, 255, 0.6);
  transform: translateX(4px);
}

.header-arrow svg {
  width: 20px;
  height: 20px;
}

/* Card Content */
.card-content {
  min-height: 80px;
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px 0;
  color: rgba(255, 255, 255, 0.3);
}

.empty-state svg {
  width: 32px;
  height: 32px;
  margin-bottom: 12px;
  opacity: 0.5;
}

.empty-state p {
  margin: 0;
  font-size: 14px;
}

/* Task List */
.task-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 280px;
  overflow-y: auto;
  padding-right: 4px;
}

/* Custom Scrollbar */
.task-list::-webkit-scrollbar {
  width: 4px;
}

.task-list::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 2px;
}

.task-list::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 2px;
}

.task-list::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}

.task-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  transition: all 0.2s ease;
}

.task-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.task-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.task-indicator.completed {
  background: #22C55E;
}

.task-indicator.failed {
  background: #EF4444;
}

.task-indicator.interrupted {
  background: #F59E0B;
}

.task-info {
  flex: 1;
  min-width: 0;
}

.task-name {
  font-size: 14px;
  font-weight: 500;
  color: #fff;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 4px;
}

.task-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
  flex-wrap: wrap;
}

.completion-time::before {
  content: '';
  display: inline-block;
  width: 1px;
  height: 10px;
  background: rgba(255, 255, 255, 0.2);
  margin-right: 12px;
}

.duration::before {
  content: '';
  display: inline-block;
  width: 1px;
  height: 10px;
  background: rgba(255, 255, 255, 0.2);
  margin-right: 12px;
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .recent-activity-card {
    padding: 16px;
  }

  .header-icon {
    width: 36px;
    height: 36px;
  }

  .header-icon svg {
    width: 18px;
    height: 18px;
  }

  .header-title h3 {
    font-size: 14px;
  }

  .task-item {
    padding: 10px;
  }

  .task-name {
    font-size: 13px;
  }

  .task-meta {
    font-size: 11px;
  }
}
</style>
