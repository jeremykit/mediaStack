<template>
  <div class="tasks-page">
    <div class="page-header">
      <h2>录制任务</h2>
      <el-button @click="loadTasks" :loading="loading">刷新</el-button>
    </div>

    <el-table :data="tasks" v-loading="loading" stripe>
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="source_name" label="直播源" />
      <el-table-column prop="status" label="状态" width="120">
        <template #default="{ row }">
          <el-tag :type="statusType(row.status)">{{ statusText(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="started_at" label="开始时间" width="180">
        <template #default="{ row }">{{ formatTime(row.started_at) }}</template>
      </el-table-column>
      <el-table-column prop="ended_at" label="结束时间" width="180">
        <template #default="{ row }">{{ formatTime(row.ended_at) }}</template>
      </el-table-column>
      <el-table-column prop="duration" label="时长" width="100">
        <template #default="{ row }">{{ formatDuration(row.duration) }}</template>
      </el-table-column>
      <el-table-column prop="file_size" label="文件大小" width="120">
        <template #default="{ row }">{{ formatSize(row.file_size) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="100" fixed="right">
        <template #default="{ row }">
          <el-button
            v-if="row.status === 'recording'"
            size="small"
            type="danger"
            @click="handleStop(row)"
            :loading="row.stopping"
          >停止</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { tasksApi, type Task } from '../../api/tasks'

const tasks = ref<(Task & { stopping?: boolean })[]>([])
const loading = ref(false)
let refreshTimer: number | null = null

const loadTasks = async () => {
  loading.value = true
  try {
    const { data } = await tasksApi.list()
    tasks.value = data
  } catch {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const handleStop = async (row: Task & { stopping?: boolean }) => {
  row.stopping = true
  try {
    await tasksApi.stopRecording(row.source_id)
    ElMessage.success('已停止录制')
    loadTasks()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '停止失败')
  } finally {
    row.stopping = false
  }
}

const statusType = (status: string) => ({
  pending: 'info', recording: 'warning', completed: 'success', failed: 'danger', interrupted: 'info'
}[status] || 'info')

const statusText = (status: string) => ({
  pending: '等待中', recording: '录制中', completed: '已完成', failed: '失败', interrupted: '已中断'
}[status] || status)

const formatTime = (time: string | null) => time ? new Date(time).toLocaleString('zh-CN') : '-'

const formatDuration = (seconds: number | null) => {
  if (!seconds) return '-'
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = seconds % 60
  return h > 0 ? `${h}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}` : `${m}:${String(s).padStart(2, '0')}`
}

const formatSize = (bytes: number | null) => {
  if (!bytes) return '-'
  const units = ['B', 'KB', 'MB', 'GB']
  let i = 0, size = bytes
  while (size >= 1024 && i < units.length - 1) { size /= 1024; i++ }
  return `${size.toFixed(1)} ${units[i]}`
}

onMounted(() => {
  loadTasks()
  refreshTimer = window.setInterval(loadTasks, 5000)
})

onUnmounted(() => { if (refreshTimer) clearInterval(refreshTimer) })
</script>

<style scoped>
.tasks-page { padding: 20px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
</style>
