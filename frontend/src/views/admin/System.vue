<template>
  <div class="system-page">
    <h2>系统状态</h2>
    <el-row :gutter="20" v-loading="loading">
      <el-col :span="8">
        <el-card>
          <template #header>CPU 使用率</template>
          <el-progress type="dashboard" :percentage="status?.cpu_percent || 0" :color="getColor(status?.cpu_percent)" />
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>内存使用率</template>
          <el-progress type="dashboard" :percentage="status?.memory_percent || 0" :color="getColor(status?.memory_percent)" />
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>磁盘使用率</template>
          <el-progress type="dashboard" :percentage="status?.disk_percent || 0" :color="getColor(status?.disk_percent)" />
          <div class="disk-info" v-if="status">{{ formatSize(status.disk_used) }} / {{ formatSize(status.disk_total) }}</div>
        </el-card>
      </el-col>
    </el-row>
    <el-button @click="loadStatus" style="margin-top: 20px">刷新</el-button>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { systemApi, type SystemStatus } from '../../api/system'

const status = ref<SystemStatus | null>(null)
const loading = ref(false)
let refreshTimer: ReturnType<typeof setInterval> | null = null

const loadStatus = async () => {
  loading.value = true
  try {
    const { data } = await systemApi.getStatus()
    status.value = data
  } catch (e) {
    console.error('Failed to load system status', e)
  } finally {
    loading.value = false
  }
}

const getColor = (percent?: number) => {
  if (!percent) return '#409eff'
  if (percent >= 90) return '#f56c6c'
  if (percent >= 70) return '#e6a23c'
  return '#67c23a'
}

const formatSize = (bytes: number) => {
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let i = 0, size = bytes
  while (size >= 1024 && i < units.length - 1) { size /= 1024; i++ }
  return `${size.toFixed(1)} ${units[i]}`
}

onMounted(() => {
  loadStatus()
  refreshTimer = setInterval(loadStatus, 30000)
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
})
</script>

<style scoped>
.system-page {
  padding: 0;
}

.system-page h2 {
  font-size: 20px;
  font-weight: 600;
  color: #fff;
  margin: 0 0 24px 0;
}

.disk-info {
  margin-top: 12px;
  color: rgba(255, 255, 255, 0.6);
  font-size: 14px;
}

/* Card styles */
:deep(.el-card) {
  background: rgba(15, 20, 35, 0.6);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  color: #e4e7eb;
  text-align: center;
}

:deep(.el-card__header) {
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  color: #fff;
  font-weight: 600;
  background: rgba(233, 69, 96, 0.05);
}

/* Progress styles */
:deep(.el-progress__text) {
  color: #e4e7eb;
  font-weight: 600;
}

:deep(.el-progress-circle__track) {
  stroke: rgba(255, 255, 255, 0.1);
}

/* Button styles */
:deep(.el-button) {
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.3s ease;
  margin-top: 20px;
  background: linear-gradient(135deg, #E94560 0%, #8B5CF6 100%);
  border: none;
  box-shadow: 0 4px 12px rgba(233, 69, 96, 0.3);
  color: #fff;
}

:deep(.el-button:hover) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(233, 69, 96, 0.4);
}

/* Loading overlay */
:deep(.el-loading-mask) {
  background: rgba(10, 14, 26, 0.8);
  backdrop-filter: blur(4px);
}

:deep(.el-loading-spinner .circular) {
  stroke: #E94560;
}
</style>
