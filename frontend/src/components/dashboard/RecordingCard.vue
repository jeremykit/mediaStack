<template>
  <div class="recording-card" @click="navigateToTasks">
    <div class="card-header">
      <div class="header-icon recording">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="12" cy="12" r="6" fill="currentColor"/>
          <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="2"/>
        </svg>
      </div>
      <div class="header-title">
        <h3>录制中</h3>
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
          <circle cx="12" cy="12" r="8" stroke="currentColor" stroke-width="2" stroke-dasharray="4 4"/>
          <path d="M12 8V12L15 15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
        <p>暂无录制中任务</p>
      </div>

      <div v-else class="task-list">
        <div
          v-for="task in tasks"
          :key="task.id"
          class="task-item"
        >
          <div class="task-indicator"></div>
          <div class="task-info">
            <div class="task-name">{{ task.source_name }}</div>
            <div class="task-meta">
              <span class="start-time">{{ formatStartTime(task.started_at) }}</span>
              <span class="duration">{{ formatDuration(task.duration) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import type { RecordingTaskInfo } from '@/api/dashboard'

interface Props {
  tasks: RecordingTaskInfo[]
}

const props = defineProps<Props>()
const router = useRouter()
const now = ref(Date.now())
let timer: ReturnType<typeof setInterval> | null = null

const formatStartTime = (dateString: string): string => {
  const date = new Date(dateString)
  const hours = date.getHours().toString().padStart(2, '0')
  const minutes = date.getMinutes().toString().padStart(2, '0')
  return `${hours}:${minutes}`
}

const formatDuration = (seconds: number): string => {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = seconds % 60

  if (hours > 0) {
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }
  return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

// Calculate current duration based on started_at time
const getCurrentDuration = (startedAt: string, baseDuration: number): number => {
  const startTime = new Date(startedAt).getTime()
  const elapsed = Math.floor((now.value - startTime) / 1000)
  return Math.max(0, baseDuration + elapsed)
}

// Compute tasks with real-time duration
const tasks = computed(() => {
  return props.tasks.map(task => ({
    ...task,
    duration: getCurrentDuration(task.started_at, task.duration)
  }))
})

const navigateToTasks = () => {
  router.push('/admin/tasks')
}

onMounted(() => {
  // Update current time every second to trigger duration recalculation
  timer = setInterval(() => {
    now.value = Date.now()
  }, 1000)
})

onUnmounted(() => {
  if (timer) {
    clearInterval(timer)
    timer = null
  }
})
</script>

<style scoped>
.recording-card {
  background: rgba(15, 20, 35, 0.6);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.recording-card:hover {
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
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.header-icon svg {
  width: 20px;
  height: 20px;
}

.header-icon.recording {
  background: rgba(233, 69, 96, 0.15);
  color: #E94560;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
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

.recording-card:hover .header-arrow {
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
  gap: 12px;
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
  background: #E94560;
  flex-shrink: 0;
  animation: blink 1.5s ease-in-out infinite;
}

@keyframes blink {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.3;
  }
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
}

.start-time::before {
  content: '';
  display: inline-block;
  width: 1px;
  height: 10px;
  background: rgba(255, 255, 255, 0.2);
  margin-right: 12px;
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .recording-card {
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
}
</style>
