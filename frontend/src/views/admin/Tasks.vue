<template>
  <div class="tasks-page">
    <div class="page-header">
      <h2>录制任务</h2>
      <el-button @click="loadTasks" :loading="loading">刷新</el-button>
    </div>

    <el-table :data="tasks" v-loading="loading" stripe>
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="source_name" label="直播源" width="100" show-overflow-tooltip />
      <el-table-column label="分类" width="120">
        <template #default="{ row }">
          <el-tag v-if="row.source?.category" size="small">{{ row.source.category.name }}</el-tag>
          <el-tag v-else size="small" type="info">未分类</el-tag>
        </template>
      </el-table-column>
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
      <el-table-column label="操作" fixed="right">
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

    <!-- Mobile Card Layout -->
    <div class="mobile-task-cards" v-loading="loading">
      <div
        v-for="task in tasks"
        :key="task.id"
        class="task-card"
      >
        <div class="task-card-header">
          <div class="task-card-title">
            <div class="task-card-name">{{ task.source_name || '未知来源' }}</div>
            <div class="task-card-id">ID: {{ task.id }}</div>
          </div>
          <el-tag :type="statusType(task.status)">{{ statusText(task.status) }}</el-tag>
        </div>

        <div class="task-card-row" v-if="task.source?.category">
          <span class="task-card-label">分类</span>
          <el-tag size="small">{{ task.source.category.name }}</el-tag>
        </div>

        <div class="task-card-row">
          <span class="task-card-label">开始</span>
          <span class="task-card-value">{{ formatTime(task.started_at) }}</span>
        </div>

        <div class="task-card-row">
          <span class="task-card-label">结束</span>
          <span class="task-card-value">{{ formatTime(task.ended_at) }}</span>
        </div>

        <div class="task-card-row">
          <span class="task-card-label">时长</span>
          <span class="task-card-value">{{ formatDuration(task.duration) }}</span>
        </div>

        <div class="task-card-row" v-if="task.file_size">
          <span class="task-card-label">大小</span>
          <span class="task-card-value">{{ formatSize(task.file_size) }}</span>
        </div>

        <div class="task-card-actions" v-if="task.status === 'recording'">
          <el-button
            type="danger"
            size="small"
            @click="handleStop(task)"
            :loading="task.stopping"
            style="width: 100%"
          >停止录制</el-button>
        </div>
      </div>

      <div v-if="tasks.length === 0 && !loading" class="empty-state">
        <p>暂无录制任务</p>
      </div>
    </div>
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
.tasks-page {
  padding: 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h2 {
  font-size: 20px;
  font-weight: 600;
  color: #fff;
  margin: 0;
}

/* Override Element Plus table styles for dark theme */
:deep(.el-table) {
  background: rgba(15, 20, 35, 0.6);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  overflow: hidden;
  color: #e4e7eb;
}

:deep(.el-table__header-wrapper) {
  background: rgba(233, 69, 96, 0.05);
}

:deep(.el-table th.el-table__cell) {
  background: transparent;
  color: rgba(255, 255, 255, 0.7);
  font-weight: 600;
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

:deep(.el-table tr) {
  background: transparent;
}

:deep(.el-table__row) {
  transition: all 0.3s ease;
}

:deep(.el-table__row:hover > td) {
  background: rgba(233, 69, 96, 0.08) !important;
}

:deep(.el-table td.el-table__cell) {
  border-bottom: 1px solid rgba(255, 255, 255, 0.03);
  color: #e4e7eb;
}

:deep(.el-table--striped .el-table__body tr.el-table__row--striped td) {
  background: rgba(255, 255, 255, 0.02);
}

:deep(.el-table__empty-block) {
  background: transparent;
}

:deep(.el-table__empty-text) {
  color: rgba(255, 255, 255, 0.4);
}

/* Button styles */
:deep(.el-button) {
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.3s ease;
}

:deep(.el-button--primary) {
  background: linear-gradient(135deg, #E94560 0%, #8B5CF6 100%);
  border: none;
  box-shadow: 0 4px 12px rgba(233, 69, 96, 0.3);
}

:deep(.el-button--primary:hover) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(233, 69, 96, 0.4);
}

:deep(.el-button--danger) {
  background: rgba(239, 68, 68, 0.2);
  border: 1px solid rgba(239, 68, 68, 0.4);
  color: #ef4444;
}

:deep(.el-button--danger:hover) {
  background: rgba(239, 68, 68, 0.3);
  border-color: rgba(239, 68, 68, 0.6);
}

:deep(.el-button--small) {
  padding: 6px 12px;
  font-size: 13px;
}

/* Tag styles */
:deep(.el-tag) {
  border-radius: 6px;
  border: none;
  font-weight: 500;
  font-size: 12px;
  padding: 4px 12px;
}

:deep(.el-tag--info) {
  background: rgba(107, 114, 128, 0.2);
  color: #9ca3af;
}

:deep(.el-tag--warning) {
  background: rgba(245, 158, 11, 0.2);
  color: #f59e0b;
}

:deep(.el-tag--success) {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
}

:deep(.el-tag--danger) {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

/* Loading overlay */
:deep(.el-loading-mask) {
  background: rgba(10, 14, 26, 0.8);
  backdrop-filter: blur(4px);
}

:deep(.el-loading-spinner .circular) {
  stroke: #E94560;
}

/* ==================== Mobile Responsive ==================== */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .page-header h2 {
    font-size: 18px;
  }

  .page-header .el-button {
    width: 100%;
  }

  /* Hide default table on mobile */
  :deep(.el-table) {
    display: none;
  }

  .empty-state {
    text-align: center;
    padding: 40px 20px;
    color: rgba(255, 255, 255, 0.4);
  }
}

@media (min-width: 769px) {
  .mobile-task-cards {
    display: none !important;
  }
}

/* Mobile Card Layout */
@media (max-width: 768px) {
  .mobile-task-cards {
    display: block !important;
  }

  .task-card {
    background: rgba(15, 20, 35, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 12px;
    backdrop-filter: blur(10px);
  }

  .task-card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 12px;
    padding-bottom: 12px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  }

  .task-card-title {
    flex: 1;
    min-width: 0;
  }

  .task-card-name {
    font-size: 16px;
    font-weight: 600;
    color: #fff;
    margin-bottom: 4px;
  }

  .task-card-id {
    font-size: 12px;
    color: rgba(255, 255, 255, 0.4);
    font-family: var(--font-mono);
  }

  .task-card-row {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 10px;
    font-size: 14px;
  }

  .task-card-row:last-child {
    margin-bottom: 0;
  }

  .task-card-label {
    color: rgba(255, 255, 255, 0.5);
    font-size: 12px;
    min-width: 50px;
  }

  .task-card-value {
    flex: 1;
    color: #e4e7eb;
  }

  .task-card-actions {
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid rgba(255, 255, 255, 0.08);
  }
}
</style>
