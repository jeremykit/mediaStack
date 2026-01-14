<template>
  <div class="videos-page">
    <div class="page-header"><h2>视频管理</h2></div>
    <el-table :data="videos" v-loading="loading" stripe>
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="title" label="标题" show-overflow-tooltip />
      <el-table-column prop="duration" label="时长" width="100">
        <template #default="{ row }">{{ formatDuration(row.duration) }}</template>
      </el-table-column>
      <el-table-column prop="file_size" label="大小" width="100">
        <template #default="{ row }">{{ formatSize(row.file_size) }}</template>
      </el-table-column>
      <el-table-column prop="view_count" label="观看" width="80" />
      <el-table-column prop="created_at" label="创建时间" width="180">
        <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button size="small" type="primary" @click="handleEdit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { videosApi, type Video } from '../../api/videos'

const videos = ref<Video[]>([])
const loading = ref(false)

const loadVideos = async () => {
  loading.value = true
  try {
    const { data } = await videosApi.list()
    videos.value = data
  } catch { ElMessage.error('加载失败') }
  finally { loading.value = false }
}

const handleEdit = async (row: Video) => {
  const { value } = await ElMessageBox.prompt('请输入新标题', '编辑视频', {
    inputValue: row.title, inputPattern: /.+/, inputErrorMessage: '标题不能为空'
  })
  try {
    await videosApi.update(row.id, { title: value })
    ElMessage.success('更新成功')
    loadVideos()
  } catch (e: any) { ElMessage.error(e.response?.data?.detail || '更新失败') }
}

const handleDelete = async (row: Video) => {
  try {
    await ElMessageBox.confirm('确定要删除该视频吗？此操作将同时删除文件！', '提示', { type: 'warning' })
    await videosApi.delete(row.id)
    ElMessage.success('删除成功')
    loadVideos()
  } catch (e: any) { if (e !== 'cancel') ElMessage.error(e.response?.data?.detail || '删除失败') }
}

const formatDuration = (s: number | null) => {
  if (!s) return '-'
  const m = Math.floor(s / 60), sec = s % 60
  return `${m}:${sec.toString().padStart(2, '0')}`
}
const formatSize = (b: number | null) => {
  if (!b) return '-'
  const u = ['B', 'KB', 'MB', 'GB']
  let i = 0, s = b
  while (s >= 1024 && i < 3) { s /= 1024; i++ }
  return `${s.toFixed(1)} ${u[i]}`
}
const formatTime = (t: string) => new Date(t).toLocaleString('zh-CN')

onMounted(loadVideos)
</script>

<style scoped>
.videos-page { padding: 20px; }
.page-header { margin-bottom: 20px; }
</style>
