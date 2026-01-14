<template>
  <div class="system-status" v-if="status">
    <el-tooltip content="CPU 使用率">
      <span class="status-item">
        <el-icon><Cpu /></el-icon>
        {{ status.cpu_percent.toFixed(1) }}%
      </span>
    </el-tooltip>
    <el-tooltip content="内存使用率">
      <span class="status-item">
        <el-icon><Coin /></el-icon>
        {{ status.memory_percent.toFixed(1) }}%
      </span>
    </el-tooltip>
    <el-tooltip :content="`磁盘: ${formatSize(status.disk_used)} / ${formatSize(status.disk_total)}`">
      <span class="status-item">
        <el-icon><FolderOpened /></el-icon>
        {{ status.disk_percent.toFixed(1) }}%
      </span>
    </el-tooltip>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { Cpu, Coin, FolderOpened } from '@element-plus/icons-vue'
import { systemApi, type SystemStatus } from '../api/system'

const status = ref<SystemStatus | null>(null)
let timer: number | null = null

const loadStatus = async () => {
  try {
    const { data } = await systemApi.getStatus()
    status.value = data
  } catch (e) {
    // Silently fail
  }
}

const formatSize = (bytes: number) => {
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let i = 0, size = bytes
  while (size >= 1024 && i < units.length - 1) { size /= 1024; i++ }
  return `${size.toFixed(1)} ${units[i]}`
}

onMounted(() => {
  loadStatus()
  timer = window.setInterval(loadStatus, 30000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<style scoped>
.system-status {
  display: flex;
  gap: 16px;
  color: #bfcbd9;
  font-size: 13px;
}
.status-item {
  display: flex;
  align-items: center;
  gap: 4px;
}
</style>
