<template>
  <div class="pending-video-card" :class="{ 'zero-count': count === 0 }" @click="navigateToVideos">
    <div class="card-header">
      <div class="header-icon" :class="count === 0 ? 'success' : 'pending'">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect x="2" y="6" width="14" height="12" rx="2" stroke="currentColor" stroke-width="2"/>
          <path d="M16 10L22 7V17L16 14V10Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
        </svg>
      </div>
      <div class="header-title">
        <h3>待处理视频</h3>
        <span class="count">{{ count }}</span>
      </div>
      <div class="header-arrow">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M9 18L15 12L9 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
    </div>

    <div class="card-content">
      <div v-if="count === 0" class="empty-state success">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M9 12L11 14L15 10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="2"/>
        </svg>
        <p>所有视频已处理完成</p>
      </div>

      <div v-else class="count-display">
        <div class="big-number">{{ count }}</div>
        <div class="label">个视频待处理</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

interface Props {
  count: number
}

const props = defineProps<Props>()
const router = useRouter()

const navigateToVideos = () => {
  router.push('/admin/videos')
}
</script>

<style scoped>
.pending-video-card {
  background: rgba(15, 20, 35, 0.6);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.pending-video-card:hover {
  border-color: rgba(251, 146, 60, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(251, 146, 60, 0.15);
}

.pending-video-card.zero-count:hover {
  border-color: rgba(34, 197, 94, 0.3);
  box-shadow: 0 8px 24px rgba(34, 197, 94, 0.15);
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

.header-icon.pending {
  background: rgba(251, 146, 60, 0.15);
  color: #FB923C;
}

.header-icon.success {
  background: rgba(34, 197, 94, 0.15);
  color: #22C55E;
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

.pending-video-card:hover .header-arrow {
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

.empty-state.success {
  color: rgba(34, 197, 94, 0.5);
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

/* Count Display */
.count-display {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 10px 0;
}

.big-number {
  font-size: 48px;
  font-weight: 700;
  background: linear-gradient(135deg, #FB923C 0%, #F97316 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1;
  margin-bottom: 8px;
}

.zero-count .big-number {
  background: linear-gradient(135deg, #22C55E 0%, #16A34A 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.count-display .label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.4);
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .pending-video-card {
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

  .big-number {
    font-size: 40px;
  }
}
</style>
