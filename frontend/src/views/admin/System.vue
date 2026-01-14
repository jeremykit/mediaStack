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
import { ref, onMounted } from 'vue'
import { systemApi, type SystemStatus } from '../../api/system'

const status = ref<SystemStatus | null>(null)
const loading = ref(false)

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

onMounted(loadStatus)
</script>

<style scoped>
.system-page { padding: 20px; }
.el-card { text-align: center; }
.disk-info { margin-top: 12px; color: #909399; font-size: 14px; }
</style>
