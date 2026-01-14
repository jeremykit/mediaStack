<template>
  <div class="sources-page">
    <div class="page-header">
      <h2>直播源管理</h2>
      <el-button type="primary" @click="handleAdd">添加直播源</el-button>
    </div>

    <el-table :data="sources" v-loading="loading" stripe>
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="protocol" label="协议" width="100">
        <template #default="{ row }">
          <el-tag>{{ row.protocol.toUpperCase() }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="url" label="拉流地址" show-overflow-tooltip />
      <el-table-column prop="retention_days" label="保留天数" width="100" />
      <el-table-column prop="is_active" label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'">
            {{ row.is_active ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="280" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="handleCheckStatus(row)" :loading="row.checking">
            检测状态
          </el-button>
          <el-button size="small" type="primary" @click="handleEdit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <SourceForm v-model="formVisible" :source="currentSource" @success="loadSources" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { sourcesApi, type Source } from '../../api/sources'
import SourceForm from '../../components/SourceForm.vue'

const sources = ref<(Source & { checking?: boolean })[]>([])
const loading = ref(false)
const formVisible = ref(false)
const currentSource = ref<Source | null>(null)

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
      message: data.online ? '直播源在线' : `直播源离线: ${data.message}`
    })
  } catch (e: any) {
    ElMessage.error('检测失败')
  } finally {
    row.checking = false
  }
}

onMounted(loadSources)
</script>

<style scoped>
.sources-page {
  padding: 20px;
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
</style>
