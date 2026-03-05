<template>
  <div class="traffic-card">
    <div class="card-header">
      <div class="header-icon">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M13 2L3 14H12L11 22L21 10H12L13 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
      <div class="header-title">
        <h3>访问统计</h3>
      </div>
    </div>

    <div class="card-content">
      <!-- Period Tabs -->
      <div class="period-tabs">
        <button
          v-for="item in traffic"
          :key="item.period"
          class="period-tab"
          :class="{ active: selectedPeriod === item.period }"
          @click="selectedPeriod = item.period"
        >
          {{ getPeriodLabel(item.period) }}
        </button>
      </div>

      <!-- Current Period Stats -->
      <div v-if="currentTraffic" class="traffic-stats">
        <div class="stats-row">
          <div class="stat-item video-views">
            <div class="stat-icon">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect x="2" y="6" width="14" height="12" rx="2" stroke="currentColor" stroke-width="2"/>
                <path d="M16 10L22 7V17L16 14V10Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
              </svg>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ currentTraffic.video_views }}</div>
              <div class="stat-label">视频访问量</div>
            </div>
          </div>

          <div class="stat-item audio-views">
            <div class="stat-icon">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 3V21M12 3L8 7M12 3L16 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M8 21H16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ currentTraffic.audio_views }}</div>
              <div class="stat-label">音频访问量</div>
            </div>
          </div>
        </div>

        <div class="stats-row">
          <div class="stat-item video-downloads">
            <div class="stat-icon">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M21 15V19C21 19.5304 20.7893 20.0391 20.4142 20.4142C20.0391 20.7893 19.5304 21 19 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M7 10L12 15L17 10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M12 15V3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ currentTraffic.video_downloads }}</div>
              <div class="stat-label">视频下载量</div>
            </div>
          </div>

          <div class="stat-item audio-downloads">
            <div class="stat-icon">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M21 15V19C21 19.5304 20.7893 20.0391 20.4142 20.4142C20.0391 20.7893 19.5304 21 19 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M7 10L12 15L17 10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M12 15V3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ currentTraffic.audio_downloads }}</div>
              <div class="stat-label">音频下载量</div>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="empty-state">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M13 2L3 14H12L11 22L21 10H12L13 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <span>暂无统计数据</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { TrafficPeriod, TrafficStats } from '@/api/dashboard'

interface Props {
  traffic: TrafficStats[]
}

const props = defineProps<Props>()

const selectedPeriod = ref<TrafficPeriod>('today')

const currentTraffic = computed(() => {
  return props.traffic.find(t => t.period === selectedPeriod.value)
})

const getPeriodLabel = (period: TrafficPeriod): string => {
  const labels: Record<TrafficPeriod, string> = {
    today: '今天',
    week: '本周',
    month: '本月'
  }
  return labels[period]
}
</script>

<style scoped>
.traffic-card {
  background: rgba(15, 20, 35, 0.6);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 20px;
  transition: all 0.3s ease;
}

.traffic-card:hover {
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
}

.header-title h3 {
  font-size: 16px;
  font-weight: 600;
  color: #fff;
  margin: 0;
}

/* Card Content */
.card-content {
  min-height: 120px;
}

/* Period Tabs */
.period-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
  background: rgba(255, 255, 255, 0.03);
  padding: 4px;
  border-radius: 10px;
}

.period-tab {
  flex: 1;
  padding: 8px 12px;
  border: none;
  background: transparent;
  color: rgba(255, 255, 255, 0.5);
  font-size: 13px;
  font-weight: 500;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.period-tab:hover {
  color: rgba(255, 255, 255, 0.7);
  background: rgba(255, 255, 255, 0.05);
}

.period-tab.active {
  background: linear-gradient(135deg, #E94560 0%, #8B5CF6 100%);
  color: #fff;
}

/* Traffic Stats */
.traffic-stats {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.stats-row {
  display: flex;
  gap: 12px;
}

.stat-item {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 10px;
  transition: all 0.2s ease;
}

.stat-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.stat-item .stat-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-item .stat-icon svg {
  width: 18px;
  height: 18px;
}

.stat-item.video-views .stat-icon {
  background: rgba(233, 69, 96, 0.15);
  color: #E94560;
}

.stat-item.audio-views .stat-icon {
  background: rgba(139, 92, 246, 0.15);
  color: #8B5CF6;
}

.stat-item.video-downloads .stat-icon {
  background: rgba(34, 197, 94, 0.15);
  color: #22C55E;
}

.stat-item.audio-downloads .stat-icon {
  background: rgba(59, 130, 246, 0.15);
  color: #3B82F6;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 22px;
  font-weight: 700;
  color: #fff;
  line-height: 1;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px 16px;
  gap: 8px;
  color: rgba(255, 255, 255, 0.3);
}

.empty-state svg {
  width: 32px;
  height: 32px;
}

.empty-state span {
  font-size: 13px;
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .traffic-card {
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

  .period-tabs {
    margin-bottom: 16px;
  }

  .period-tab {
    padding: 6px 10px;
    font-size: 12px;
  }

  .stats-row {
    flex-direction: column;
    gap: 10px;
  }

  .stat-item {
    padding: 10px;
  }

  .stat-item .stat-icon {
    width: 32px;
    height: 32px;
  }

  .stat-item .stat-icon svg {
    width: 16px;
    height: 16px;
  }

  .stat-value {
    font-size: 18px;
  }
}
</style>
