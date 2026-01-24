<template>
  <div class="sources-page">
    <div class="page-header">
      <h2>直播源管理</h2>
      <div>
        <el-button
          v-if="selectedSources.length > 0"
          type="primary"
          @click="showBulkCategoryDialog = true"
        >批量设置分类 ({{ selectedSources.length }})</el-button>
        <el-button type="primary" @click="handleAdd">添加直播源</el-button>
      </div>
    </div>

    <el-table :data="sources" v-loading="loading" stripe @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="55" />
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="protocol" label="协议" width="100">
        <template #default="{ row }">
          <el-tag>{{ row.protocol.toUpperCase() }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="分类" width="120">
        <template #default="{ row }">
          <el-tag v-if="row.category" size="small">{{ row.category.name }}</el-tag>
          <el-tag v-else size="small" type="info">未分类</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="url" label="拉流地址" show-overflow-tooltip />
      <el-table-column label="直播状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.is_online ? 'success' : 'danger'">
            {{ row.is_online ? '在线' : '离线' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="录制状态" width="100">
        <template #default="{ row }">
          <el-tag v-if="row.is_recording" type="warning">正在录制</el-tag>
          <el-tag v-else type="info">未录制</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="retention_days" label="保留天数" width="100" />
      <el-table-column prop="is_active" label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'">
            {{ row.is_active ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="380" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="handleCheckStatus(row)" :loading="row.checking">
            检测状态
          </el-button>
          <el-button
            v-if="!row.is_recording"
            size="small"
            type="success"
            @click="handleStartRecording(row)"
            :loading="row.starting"
            :disabled="!row.is_online"
          >开始录制</el-button>
          <el-button
            v-else
            size="small"
            type="danger"
            @click="handleStopRecording(row)"
            :loading="row.stopping"
          >停止录制</el-button>
          <el-button
            size="small"
            type="primary"
            @click="handleEdit(row)"
            :disabled="row.is_recording"
          >编辑</el-button>
          <el-button
            size="small"
            type="danger"
            @click="handleDelete(row)"
            :disabled="row.is_recording"
          >删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <SourceForm v-model="formVisible" :source="currentSource" @success="loadSources" />

    <el-dialog v-model="showBulkCategoryDialog" title="批量设置分类" width="400px">
      <el-form>
        <el-form-item label="选择分类">
          <el-select v-model="bulkCategoryId" placeholder="请选择分类">
            <el-option
              v-for="cat in categories"
              :key="cat.id"
              :label="cat.name"
              :value="cat.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showBulkCategoryDialog = false">取消</el-button>
        <el-button type="primary" @click="handleBulkUpdateCategory" :loading="bulkUpdating">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { sourcesApi, type Source } from '../../api/sources'
import { categoriesApi } from '../../api/categories'
import { tasksApi } from '../../api/tasks'
import SourceForm from '../../components/SourceForm.vue'

const sources = ref<(Source & { checking?: boolean; starting?: boolean; stopping?: boolean })[]>([])
const loading = ref(false)
const formVisible = ref(false)
const currentSource = ref<Source | null>(null)
const selectedSources = ref<Source[]>([])
const showBulkCategoryDialog = ref(false)
const bulkCategoryId = ref<number | null>(null)
const bulkUpdating = ref(false)
const categories = ref<any[]>([])
let pollTimer: number | null = null

const loadSources = async () => {
  loading.value = true
  try {
    const { data } = await sourcesApi.list()
    sources.value = data
  } catch (e: any) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const startPolling = () => {
  pollTimer = window.setInterval(() => {
    loadSources()
  }, 30000)
}

const stopPolling = () => {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

const handleAdd = () => {
  currentSource.value = null
  formVisible.value = true
}

const handleEdit = (row: Source) => {
  currentSource.value = row
  formVisible.value = true
}

const handleDelete = async (row: Source) => {
  try {
    await ElMessageBox.confirm('确定要删除该直播源吗？', '提示', { type: 'warning' })
    await sourcesApi.delete(row.id)
    ElMessage.success('删除成功')
    loadSources()
  } catch (e: any) {
    if (e !== 'cancel') {
      ElMessage.error(e.response?.data?.detail || '删除失败')
    }
  }
}

const handleCheckStatus = async (row: Source & { checking?: boolean }) => {
  row.checking = true
  try {
    const { data } = await sourcesApi.checkStatus(row.id)
    ElMessage({
      type: data.online ? 'success' : 'warning',
      message: data.message,
      duration: 5000
    })
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '检测失败，请检查网络连接')
  } finally {
    row.checking = false
  }
}

const handleStartRecording = async (row: Source & { starting?: boolean }) => {
  row.starting = true
  try {
    await tasksApi.startRecording(row.id)
    ElMessage.success('已开始录制')
    await loadSources()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '启动失败')
  } finally {
    row.starting = false
  }
}

const handleStopRecording = async (row: Source & { stopping?: boolean }) => {
  row.stopping = true
  try {
    await tasksApi.stopRecording(row.id)
    ElMessage.success('已停止录制')
    await loadSources()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '停止失败')
  } finally {
    row.stopping = false
  }
}

const loadCategories = async () => {
  try {
    const { data } = await categoriesApi.list()
    categories.value = data
  } catch (e) {
    console.error('Failed to load categories', e)
  }
}

const handleSelectionChange = (selection: Source[]) => {
  selectedSources.value = selection
}

const handleBulkUpdateCategory = async () => {
  if (!bulkCategoryId.value) {
    ElMessage.warning('请选择分类')
    return
  }

  bulkUpdating.value = true
  try {
    const sourceIds = selectedSources.value.map(s => s.id)
    await sourcesApi.bulkUpdateCategory(sourceIds, bulkCategoryId.value)
    ElMessage.success('批量设置成功')
    showBulkCategoryDialog.value = false
    bulkCategoryId.value = null
    loadSources()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '批量设置失败')
  } finally {
    bulkUpdating.value = false
  }
}

onMounted(() => {
  loadSources()
  loadCategories()
  startPolling()
})

onUnmounted(() => {
  stopPolling()
})
</script>

<style scoped>
.sources-page {
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

:deep(.el-button--success) {
  background: rgba(16, 185, 129, 0.2);
  border: 1px solid rgba(16, 185, 129, 0.4);
  color: #10b981;
}

:deep(.el-button--success:hover) {
  background: rgba(16, 185, 129, 0.3);
  border-color: rgba(16, 185, 129, 0.6);
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

:deep(.el-tag--success) {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
}

:deep(.el-tag--info) {
  background: rgba(107, 114, 128, 0.2);
  color: #9ca3af;
}

:deep(.el-tag:not(.el-tag--success):not(.el-tag--info)) {
  background: rgba(139, 92, 246, 0.2);
  color: #8B5CF6;
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
