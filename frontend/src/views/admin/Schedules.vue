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
.schedules-page { padding: 20px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
</style>
