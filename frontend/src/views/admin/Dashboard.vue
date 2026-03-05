<template>
  <div class="dashboard-page">
    <div class="dashboard-header">
      <h2>仪表盘</h2>
      <el-button @click="refreshAll" :loading="refreshing" class="refresh-btn">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M4 4V9H4.58152M4.58152 9C6.09566 5.8294 9.37744 3.62921 13.1393 4.09593C17.5488 4.64436 20.8538 8.43238 20.9955 12.8788C21.1518 17.7662 17.1643 21.9235 12.2769 21.9654C7.68865 22.0048 3.77858 18.5878 3.11675 14.1056" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        全局刷新
      </el-button>
    </div>

    <!-- Dashboard Grid -->
    <div class="dashboard-grid">
      <!-- Stats Cards Row -->
      <el-row :gutter="20">
        <el-col :span="6">
          <div class="stat-card">
            <div class="stat-icon sources">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="12" r="2" fill="currentColor"/>
                <path d="M8.5 8.5C9.88071 7.11929 12.1193 7.11929 13.5 8.5M6 6C8.76142 3.23858 13.2386 3.23858 16 6M18.5 8.5C17.1193 7.11929 14.8807 7.11929 13.5 8.5M20 6C17.2386 3.23858 12.7614 3.23858 10 6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stats.sources }}</div>
              <div class="stat-label">直播源</div>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card">
            <div class="stat-icon tasks">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="12" r="8" stroke="currentColor" stroke-width="2"/>
                <circle cx="12" cy="12" r="4" fill="currentColor"/>
              </svg>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stats.activeTasks }}</div>
              <div class="stat-label">录制中</div>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card">
            <div class="stat-icon videos">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect x="2" y="6" width="14" height="12" rx="2" stroke="currentColor" stroke-width="2"/>
                <path d="M16 10L22 7V17L16 14V10Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
              </svg>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stats.videos }}</div>
              <div class="stat-label">视频总数</div>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card">
            <div class="stat-icon storage">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M4 10V16C4 17.1046 4.89543 18 6 18H18C19.1046 18 20 17.1046 20 16V10M4 10L9 6H15L20 10M4 10L12 14L20 10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stats.storageUsed }}</div>
              <div class="stat-label">存储使用</div>
            </div>
          </div>
        </el-col>
      </el-row>

      <!-- Placeholder for additional dashboard widgets -->
      <div class="dashboard-widgets">
        <div class="widget-placeholder">
          <p>仪表盘组件占位符</p>
          <p class="hint">后续将添加图表、最近活动、快捷操作等组件</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'

const refreshing = ref(false)

// Stats data (placeholder - will be fetched from API)
const stats = ref({
  sources: 0,
  activeTasks: 0,
  videos: 0,
  storageUsed: '0 GB'
})

const refreshAll = async () => {
  refreshing.value = true
  // Simulate refresh - will be replaced with actual API calls
  setTimeout(() => {
    refreshing.value = false
    ElMessage.success('刷新成功')
  }, 1000)
}

let refreshTimer: ReturnType<typeof setInterval> | null = null

onMounted(() => {
  // Auto refresh every 30 seconds
  refreshTimer = setInterval(() => {
    // Will be replaced with actual data fetching
  }, 30000)
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
})
</script>

<style scoped>
.dashboard-page {
  padding: 0;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.dashboard-header h2 {
  font-size: 20px;
  font-weight: 600;
  color: #fff;
  margin: 0;
}

.refresh-btn {
  background: linear-gradient(135deg, #E94560 0%, #8B5CF6 100%);
  border: none;
  color: #fff;
  border-radius: 8px;
  padding: 8px 16px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(233, 69, 96, 0.3);
}

.refresh-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(233, 69, 96, 0.4);
}

.refresh-btn svg {
  width: 16px;
  height: 16px;
}

.refresh-btn.is-loading svg {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* Stat Cards */
.dashboard-grid {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: rgba(15, 20, 35, 0.6);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  transition: all 0.3s ease;
}

.stat-card:hover {
  border-color: rgba(233, 69, 96, 0.2);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(233, 69, 96, 0.15);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-icon svg {
  width: 24px;
  height: 24px;
}

.stat-icon.sources {
  background: rgba(233, 69, 96, 0.15);
  color: #E94560;
}

.stat-icon.tasks {
  background: rgba(139, 92, 246, 0.15);
  color: #8B5CF6;
}

.stat-icon.videos {
  background: rgba(34, 197, 94, 0.15);
  color: #22C55E;
}

.stat-icon.storage {
  background: rgba(59, 130, 246, 0.15);
  color: #3B82F6;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #fff;
  line-height: 1;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.5);
}

/* Widget Placeholder */
.dashboard-widgets {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.widget-placeholder {
  grid-column: 1 / -1;
  padding: 60px 20px;
  background: rgba(15, 20, 35, 0.4);
  border: 2px dashed rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  text-align: center;
  color: rgba(255, 255, 255, 0.4);
}

.widget-placeholder p {
  margin: 0;
  font-size: 16px;
}

.widget-placeholder .hint {
  font-size: 14px;
  margin-top: 8px;
  color: rgba(255, 255, 255, 0.2);
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .dashboard-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .refresh-btn {
    width: 100%;
    justify-content: center;
  }

  :deep(.el-col-6) {
    width: 100% !important;
    max-width: 100%;
    flex: 0 0 100%;
    margin-bottom: 12px;
  }

  .stat-card {
    padding: 16px;
  }

  .stat-icon {
    width: 40px;
    height: 40px;
  }

  .stat-icon svg {
    width: 20px;
    height: 20px;
  }

  .stat-value {
    font-size: 24px;
  }

  .dashboard-widgets {
    grid-template-columns: 1fr;
  }

  .widget-placeholder {
    padding: 40px 20px;
  }
}
</style>
