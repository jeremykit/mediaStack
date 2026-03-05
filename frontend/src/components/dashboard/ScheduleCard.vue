<template>
  <div class="schedule-card" @click="navigateToSchedules">
    <div class="card-header">
      <div class="header-icon">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 8V12L15 15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          <circle cx="12" cy="12" r="8" stroke="currentColor" stroke-width="2"/>
          <path d="M12 2V4M12 20V22M2 12H4M20 12H22" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
      </div>
      <div class="header-title">
        <h3>即将执行</h3>
        <span class="count">{{ schedules.length }}</span>
      </div>
      <div class="header-arrow">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M9 18L15 12L9 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
    </div>

    <div class="card-content">
      <div v-if="schedules.length === 0" class="empty-state">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 8V12L15 15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          <circle cx="12" cy="12" r="8" stroke="currentColor" stroke-width="2" stroke-dasharray="4 4"/>
        </svg>
        <p>暂无定时计划</p>
      </div>

      <div v-else class="schedule-list">
        <div
          v-for="schedule in displaySchedules"
          :key="schedule.id"
          class="schedule-item"
        >
          <div class="schedule-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="12" cy="12" r="3" fill="currentColor"/>
              <path d="M12 2V4M12 20V22M2 12H4M20 12H22" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </div>
          <div class="schedule-info">
            <div class="schedule-name">{{ schedule.source_name }}</div>
            <div class="schedule-meta">
              <span class="next-run">{{ formatNextRun(schedule.next_run) }}</span>
              <span class="cron">{{ schedule.cron_expression }}</span>
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
import type { UpcomingScheduleInfo } from '@/api/dashboard'

interface Props {
  schedules: UpcomingScheduleInfo[]
}

const props = defineProps<Props>()
const router = useRouter()

// Display up to 5 schedules
const displaySchedules = computed(() => {
  return props.schedules.slice(0, 5)
})

const formatNextRun = (dateString: string): string => {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = date.getTime() - now.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 0) {
    return '即将开始'
  } else if (diffMins < 60) {
    return `${diffMins}分钟后`
  } else if (diffHours < 24) {
    return `${diffHours}小时后`
  } else if (diffDays < 7) {
    return `${diffDays}天后`
  } else {
    // Show actual date for distant schedules
    const month = (date.getMonth() + 1).toString().padStart(2, '0')
    const day = date.getDate().toString().padStart(2, '0')
    const hour = date.getHours().toString().padStart(2, '0')
    const minute = date.getMinutes().toString().padStart(2, '0')
    return `${month}-${day} ${hour}:${minute}`
  }
}

const navigateToSchedules = () => {
  router.push('/admin/schedules')
}
</script>

<style scoped>
.schedule-card {
  background: rgba(15, 20, 35, 0.6);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.schedule-card:hover {
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
  background: rgba(233, 69, 96, 0.15);
  color: #E94560;
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

.schedule-card:hover .header-arrow {
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

/* Schedule List */
.schedule-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 280px;
  overflow-y: auto;
  padding-right: 4px;
}

/* Custom Scrollbar */
.schedule-list::-webkit-scrollbar {
  width: 4px;
}

.schedule-list::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 2px;
}

.schedule-list::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 2px;
}

.schedule-list::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}

.schedule-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  transition: all 0.2s ease;
}

.schedule-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.schedule-icon {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  background: rgba(233, 69, 96, 0.15);
  color: #E94560;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.schedule-icon svg {
  width: 16px;
  height: 16px;
}

.schedule-info {
  flex: 1;
  min-width: 0;
}

.schedule-name {
  font-size: 14px;
  font-weight: 500;
  color: #fff;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 4px;
}

.schedule-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
  flex-wrap: wrap;
}

.next-run::before {
  content: '';
  display: inline-block;
  width: 1px;
  height: 10px;
  background: rgba(255, 255, 255, 0.2);
  margin-right: 12px;
}

.cron {
  font-family: 'Courier New', monospace;
  opacity: 0.7;
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .schedule-card {
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

  .schedule-item {
    padding: 10px;
  }

  .schedule-name {
    font-size: 13px;
  }

  .schedule-meta {
    font-size: 11px;
  }
}
</style>
