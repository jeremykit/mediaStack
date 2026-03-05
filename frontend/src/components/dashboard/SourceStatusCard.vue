<template>
  <div class="source-status-card" @click="navigateToSources">
    <div class="card-header">
      <div class="header-icon">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="12" cy="12" r="2" fill="currentColor"/>
          <path d="M8.5 8.5C9.88071 7.11929 12.1193 7.11929 13.5 8.5M6 6C8.76142 3.23858 13.2386 3.23858 16 6M18.5 8.5C17.1193 7.11929 14.8807 7.11929 13.5 8.5M20 6C17.2386 3.23858 12.7614 3.23858 10 6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
      </div>
      <div class="header-title">
        <h3>直播源状态</h3>
      </div>
      <div class="header-arrow">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M9 18L15 12L9 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
    </div>

    <div class="card-content">
      <div class="stats-grid">
        <!-- Total -->
        <div class="stat-item">
          <div class="stat-icon total">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="12" cy="12" r="8" stroke="currentColor" stroke-width="2"/>
              <path d="M12 8V12L15 15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ sources.total }}</div>
            <div class="stat-label">总数</div>
          </div>
        </div>

        <!-- Online -->
        <div class="stat-item">
          <div class="stat-icon online">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="12" cy="12" r="6" fill="currentColor"/>
            </svg>
          </div>
          <div class="stat-content">
            <div class="stat-value online">{{ sources.online }}</div>
            <div class="stat-label">在线</div>
          </div>
        </div>

        <!-- Offline -->
        <div class="stat-item">
          <div class="stat-icon offline">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="12" cy="12" r="6" stroke="currentColor" stroke-width="2"/>
              <path d="M12 8V16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </div>
          <div class="stat-content">
            <div class="stat-value offline">{{ sources.offline }}</div>
            <div class="stat-label">离线</div>
          </div>
        </div>

        <!-- Recording -->
        <div class="stat-item">
          <div class="stat-icon recording">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="12" cy="12" r="4" fill="currentColor"/>
              <circle cx="12" cy="12" r="8" stroke="currentColor" stroke-width="2"/>
            </svg>
          </div>
          <div class="stat-content">
            <div class="stat-value recording">{{ sources.recording }}</div>
            <div class="stat-label">录制中</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

interface Props {
  sources: {
    total: number
    online: number
    offline: number
    recording: number
  }
}

const props = defineProps<Props>()
const router = useRouter()

const navigateToSources = () => {
  router.push('/admin/sources')
}
</script>

<style scoped>
.source-status-card {
  background: rgba(15, 20, 35, 0.6);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.source-status-card:hover {
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

.header-arrow {
  color: rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
}

.source-status-card:hover .header-arrow {
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

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  transition: all 0.2s ease;
}

.stat-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.stat-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-icon svg {
  width: 16px;
  height: 16px;
}

.stat-icon.total {
  background: rgba(139, 92, 246, 0.15);
  color: #8B5CF6;
}

.stat-icon.online {
  background: rgba(34, 197, 94, 0.15);
  color: #22C55E;
}

.stat-icon.offline {
  background: rgba(156, 163, 175, 0.15);
  color: #9CA3AF;
}

.stat-icon.recording {
  background: rgba(251, 146, 60, 0.15);
  color: #FB923C;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 20px;
  font-weight: 700;
  color: #fff;
  line-height: 1;
  margin-bottom: 2px;
}

.stat-value.online {
  color: #22C55E;
}

.stat-value.offline {
  color: #9CA3AF;
}

.stat-value.recording {
  color: #FB923C;
}

.stat-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .source-status-card {
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

  .stats-grid {
    gap: 12px;
  }

  .stat-item {
    padding: 10px;
  }

  .stat-icon {
    width: 28px;
    height: 28px;
  }

  .stat-icon svg {
    width: 14px;
    height: 14px;
  }

  .stat-value {
    font-size: 18px;
  }

  .stat-label {
    font-size: 11px;
  }
}
</style>
