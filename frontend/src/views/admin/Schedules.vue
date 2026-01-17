<template>
  <div class="schedules-page">
    <div class="page-header">
      <h2>定时计划</h2>
      <el-button type="primary" @click="handleAdd">添加定时计划</el-button>
    </div>
    <el-table :data="schedules" v-loading="loading" stripe>
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="source_name" label="直播源" />
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
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
          <el-button size="small" type="primary" @click="handleEdit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <ScheduleForm v-model="formVisible" :schedule="currentSchedule" @success="loadSchedules" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { schedulesApi, type Schedule } from '../../api/schedules'
import ScheduleForm from '../../components/ScheduleForm.vue'

const schedules = ref<Schedule[]>([])
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
</style>
