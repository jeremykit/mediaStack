<template>
  <div class="schedules-page">
    <div class="page-header">
      <h2>定时计划</h2>
      <el-button type="primary" @click="handleAdd">添加定时计划</el-button>
    </div>
    <el-table :data="schedules" v-loading="loading" stripe>
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="source_name" label="直播源" width="100" show-overflow-tooltip />
      <el-table-column prop="cron_expr" label="Cron 表达式" width="150" />
      <el-table-column prop="is_active" label="状态" width="100">
        <template #default="{ row }">
          <el-switch
            v-model="row.is_active"
            :loading="row._switching"
            @change="handleToggleActive(row)"
          />
        </template>
      </el-table-column>
      <el-table-column prop="last_run_at" label="上次执行" width="180">
        <template #default="{ row }">{{ formatTime(row.last_run_at) }}</template>
      </el-table-column>
      <el-table-column prop="next_run_at" label="下次执行" width="180">
        <template #default="{ row }">{{ formatTime(row.next_run_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" fixed="right">
        <template #default="{ row }">
          <el-button size="small" type="primary" @click="handleEdit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- Mobile Card Layout -->
    <div class="mobile-schedule-cards" v-loading="loading">
      <div
        v-for="schedule in schedules"
        :key="schedule.id"
        class="schedule-card"
      >
        <div class="schedule-card-header">
          <div class="schedule-card-title">
            <div class="schedule-card-name">{{ schedule.source_name || '未知来源' }}</div>
            <div class="schedule-card-id">ID: {{ schedule.id }}</div>
          </div>
          <el-switch
            v-model="schedule.is_active"
            :loading="schedule._switching"
            @change="handleToggleActive(schedule)"
          />
        </div>

        <div class="schedule-card-row">
          <span class="schedule-card-label">Cron</span>
          <span class="schedule-card-value schedule-card-cron">{{ schedule.cron_expr }}</span>
        </div>

        <div class="schedule-card-row">
          <span class="schedule-card-label">上次</span>
          <span class="schedule-card-value">{{ formatTime(schedule.last_run_at) }}</span>
        </div>

        <div class="schedule-card-row">
          <span class="schedule-card-label">下次</span>
          <span class="schedule-card-value">{{ formatTime(schedule.next_run_at) }}</span>
        </div>

        <div class="schedule-card-actions">
          <el-button size="small" type="primary" @click="handleEdit(schedule)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(schedule)">删除</el-button>
        </div>
      </div>

      <div v-if="schedules.length === 0 && !loading" class="empty-state">
        <p>暂无定时计划</p>
      </div>
    </div>

    <ScheduleForm v-model="formVisible" :schedule="currentSchedule" @success="loadSchedules" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { schedulesApi, type Schedule } from '../../api/schedules'
import ScheduleForm from '../../components/ScheduleForm.vue'

const schedules = ref<(Schedule & { _switching?: boolean })[]>([])
const loading = ref(false)
const formVisible = ref(false)
const currentSchedule = ref<Schedule | null>(null)

const loadSchedules = async () => {
  loading.value = true
  try { schedules.value = (await schedulesApi.list()).data }
  catch { ElMessage.error('加载失败') }
  finally { loading.value = false }
}

const handleAdd = () => { currentSchedule.value = null; formVisible.value = true }
const handleEdit = (row: Schedule) => { currentSchedule.value = row; formVisible.value = true }

const handleToggleActive = async (row: Schedule & { _switching?: boolean }) => {
  row._switching = true
  try {
    await schedulesApi.update(row.id, { is_active: row.is_active })
    ElMessage.success(row.is_active ? '已启用' : '已禁用')
  } catch (e: any) {
    row.is_active = !row.is_active
    ElMessage.error(e.response?.data?.detail || '操作失败')
  } finally {
    row._switching = false
  }
}

const handleDelete = async (row: Schedule) => {
  try {
    await ElMessageBox.confirm('确定要删除该定时计划吗？', '提示', { type: 'warning' })
    await schedulesApi.delete(row.id)
    ElMessage.success('删除成功')
    loadSchedules()
  } catch (e: any) {
    if (e !== 'cancel') ElMessage.error(e.response?.data?.detail || '删除失败')
  }
}

const formatTime = (time: string | null) => time ? new Date(time).toLocaleString('zh-CN') : '-'

onMounted(loadSchedules)
</script>

<style scoped>
.schedules-page {
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
  .mobile-schedule-cards {
    display: none !important;
  }
}

/* Mobile Card Layout */
@media (max-width: 768px) {
  .mobile-schedule-cards {
    display: block !important;
  }

  .schedule-card {
    background: rgba(15, 20, 35, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 12px;
    backdrop-filter: blur(10px);
  }

  .schedule-card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 12px;
    padding-bottom: 12px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  }

  .schedule-card-title {
    flex: 1;
    min-width: 0;
    padding-right: 12px;
  }

  .schedule-card-name {
    font-size: 16px;
    font-weight: 600;
    color: #fff;
    margin-bottom: 4px;
  }

  .schedule-card-id {
    font-size: 12px;
    color: rgba(255, 255, 255, 0.4);
    font-family: var(--font-mono);
  }

  .schedule-card-row {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 10px;
    font-size: 14px;
  }

  .schedule-card-row:last-child {
    margin-bottom: 0;
  }

  .schedule-card-label {
    color: rgba(255, 255, 255, 0.5);
    font-size: 12px;
    min-width: 50px;
  }

  .schedule-card-value {
    flex: 1;
    color: #e4e7eb;
  }

  .schedule-card-cron {
    font-family: var(--font-mono);
    font-size: 13px;
    color: #E94560;
  }

  .schedule-card-actions {
    display: flex;
    gap: 8px;
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid rgba(255, 255, 255, 0.08);
  }

  .schedule-card-actions .el-button {
    flex: 1;
  }
}
</style>
