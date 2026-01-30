<template>
  <div class="videos-page">
    <div class="page-header"><h2>视频管理</h2></div>
    <el-table :data="videos" v-loading="loading" stripe>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="title" label="标题" show-overflow-tooltip min-width="150" />
      <el-table-column label="分类" width="120">
        <template #default="{ row }">
          <el-tag v-if="row.category" size="small">{{ row.category.name }}</el-tag>
          <span v-else class="text-muted">-</span>
        </template>
      </el-table-column>
      <el-table-column label="标签" min-width="150">
        <template #default="{ row }">
          <el-tag
            v-for="tag in row.tags"
            :key="tag.id"
            size="small"
            type="info"
            style="margin-right: 4px"
          >
            {{ tag.name }}
          </el-tag>
          <span v-if="!row.tags || row.tags.length === 0" class="text-muted">-</span>
        </template>
      </el-table-column>
      <el-table-column prop="file_type" label="类型" width="80">
        <template #default="{ row }">
          <el-tag :type="row.file_type === 'video' ? 'primary' : 'success'" size="small">
            {{ row.file_type === 'video' ? '视频' : '音频' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="duration" label="时长" width="80">
        <template #default="{ row }">{{ formatDuration(row.duration) }}</template>
      </el-table-column>
      <el-table-column prop="file_size" label="大小" width="80">
        <template #default="{ row }">{{ formatSize(row.file_size) }}</template>
      </el-table-column>
      <el-table-column prop="view_count" label="观看" width="60" />
      <el-table-column prop="created_at" label="创建时间" width="160">
        <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
          <el-button size="small" type="primary" @click="handleEdit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- Mobile Card Layout -->
    <div class="mobile-video-cards" v-loading="loading">
      <div
        v-for="video in videos"
        :key="video.id"
        class="video-card"
      >
        <div class="video-card-header">
          <div class="video-card-title">
            <div class="video-card-name">{{ video.title }}</div>
            <div class="video-card-id">ID: {{ video.id }}</div>
          </div>
          <el-tag :type="video.file_type === 'video' ? 'primary' : 'success'" size="small">
            {{ video.file_type === 'video' ? '视频' : '音频' }}
          </el-tag>
        </div>

        <div class="video-card-row" v-if="video.category">
          <span class="video-card-label">分类</span>
          <el-tag size="small">{{ video.category.name }}</el-tag>
        </div>

        <div class="video-card-row" v-if="video.tags && video.tags.length > 0">
          <span class="video-card-label">标签</span>
          <div class="video-card-tags">
            <el-tag
              v-for="tag in video.tags"
              :key="tag.id"
              size="small"
              type="info"
            >
              {{ tag.name }}
            </el-tag>
          </div>
        </div>

        <div class="video-card-meta">
          <span class="video-card-meta-item">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" width="14" height="14">
              <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
              <path d="M12 6V12L16 14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
            {{ formatDuration(video.duration) }}
          </span>
          <span class="video-card-meta-item">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" width="14" height="14">
              <path d="M21 15V19C21 19.5304 20.7893 20.0391 20.4142 20.4142C20.0391 20.7893 19.5304 21 19 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <path d="M7 10L12 15L17 10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            {{ formatSize(video.file_size) }}
          </span>
          <span class="video-card-meta-item">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" width="14" height="14">
              <path d="M1 12S5 4 12 4s11 8 11 8-5 8-11 8-11-8-11-8z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2"/>
            </svg>
            {{ video.view_count }}
          </span>
        </div>

        <div class="video-card-time">{{ formatTime(video.created_at) }}</div>

        <div class="video-card-actions">
          <el-button size="small" type="primary" @click="handleEdit(video)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(video)">删除</el-button>
        </div>
      </div>

      <div v-if="videos.length === 0 && !loading" class="empty-state">
        <p>暂无视频</p>
      </div>
    </div>

    <!-- Edit Dialog -->
    <el-dialog v-model="showEditDialog" title="编辑视频" width="500px">
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="标题">
          <el-input v-model="editForm.title" />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="editForm.category_id" placeholder="选择分类" clearable style="width: 100%">
            <el-option
              v-for="cat in categories"
              :key="cat.id"
              :label="cat.name"
              :value="cat.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="标签">
          <el-select
            v-model="editForm.tag_ids"
            multiple
            placeholder="选择标签"
            style="width: 100%"
          >
            <el-option
              v-for="tag in tags"
              :key="tag.id"
              :label="tag.name"
              :value="tag.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="saveEdit" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { videosApi, type Video } from '../../api/videos'
import { categoriesApi, type Category } from '../../api/categories'
import { tagsApi, type Tag } from '../../api/tags'

const videos = ref<Video[]>([])
const categories = ref<Category[]>([])
const tags = ref<Tag[]>([])
const loading = ref(false)
const showEditDialog = ref(false)
const saving = ref(false)
const editingVideo = ref<Video | null>(null)

const editForm = reactive({
  title: '',
  category_id: null as number | null,
  tag_ids: [] as number[]
})

const loadVideos = async () => {
  loading.value = true
  try {
    const { data } = await videosApi.list()
    videos.value = data
  } catch { ElMessage.error('加载失败') }
  finally { loading.value = false }
}

const loadCategories = async () => {
  try {
    const { data } = await categoriesApi.list()
    categories.value = data
  } catch (e) {
    console.error('Failed to load categories', e)
  }
}

const loadTags = async () => {
  try {
    const { data } = await tagsApi.list()
    tags.value = data
  } catch (e) {
    console.error('Failed to load tags', e)
  }
}

const handleEdit = (row: Video) => {
  editingVideo.value = row
  editForm.title = row.title
  editForm.category_id = row.category_id
  editForm.tag_ids = row.tags?.map(t => t.id) || []
  showEditDialog.value = true
}

const saveEdit = async () => {
  if (!editingVideo.value) return

  saving.value = true
  try {
    // Update title
    if (editForm.title !== editingVideo.value.title) {
      await videosApi.update(editingVideo.value.id, { title: editForm.title })
    }

    // Update category
    if (editForm.category_id !== editingVideo.value.category_id) {
      await videosApi.setCategory(editingVideo.value.id, editForm.category_id)
    }

    // Update tags
    const currentTagIds = editingVideo.value.tags?.map(t => t.id) || []
    const newTagIds = editForm.tag_ids
    if (JSON.stringify(currentTagIds.sort()) !== JSON.stringify(newTagIds.sort())) {
      await videosApi.setTags(editingVideo.value.id, newTagIds)
    }

    ElMessage.success('更新成功')
    showEditDialog.value = false
    loadVideos()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '更新失败')
  } finally {
    saving.value = false
  }
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

onMounted(() => {
  loadVideos()
  loadCategories()
  loadTags()
})
</script>

<style scoped>
.videos-page {
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

.text-muted {
  color: rgba(255, 255, 255, 0.4);
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

:deep(.el-tag--primary) {
  background: rgba(139, 92, 246, 0.2);
  color: #8B5CF6;
}

:deep(.el-tag--success) {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
}

:deep(.el-tag--info) {
  background: rgba(107, 114, 128, 0.2);
  color: #9ca3af;
}

:deep(.el-tag:not(.el-tag--primary):not(.el-tag--success):not(.el-tag--info)) {
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
  .mobile-video-cards {
    display: none !important;
  }
}

/* Mobile Card Layout */
@media (max-width: 768px) {
  .mobile-video-cards {
    display: block !important;
  }

  .video-card {
    background: rgba(15, 20, 35, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 12px;
    backdrop-filter: blur(10px);
  }

  .video-card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 12px;
    padding-bottom: 12px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  }

  .video-card-title {
    flex: 1;
    min-width: 0;
    padding-right: 12px;
  }

  .video-card-name {
    font-size: 15px;
    font-weight: 600;
    color: #fff;
    margin-bottom: 4px;
    line-height: 1.4;
  }

  .video-card-id {
    font-size: 11px;
    color: rgba(255, 255, 255, 0.4);
    font-family: var(--font-mono);
  }

  .video-card-row {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    margin-bottom: 10px;
  }

  .video-card-label {
    color: rgba(255, 255, 255, 0.5);
    font-size: 12px;
    min-width: 50px;
    padding-top: 2px;
  }

  .video-card-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
  }

  .video-card-meta {
    display: flex;
    gap: 16px;
    margin-bottom: 10px;
    padding: 8px 0;
    border-top: 1px solid rgba(255, 255, 255, 0.05);
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  }

  .video-card-meta-item {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 12px;
    color: rgba(255, 255, 255, 0.6);
  }

  .video-card-meta-item svg {
    flex-shrink: 0;
    color: rgba(255, 255, 255, 0.4);
  }

  .video-card-time {
    font-size: 11px;
    color: rgba(255, 255, 255, 0.4);
    margin-bottom: 10px;
  }

  .video-card-actions {
    display: flex;
    gap: 8px;
  }

  .video-card-actions .el-button {
    flex: 1;
  }
}
</style>
