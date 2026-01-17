<template>
  <div class="recordings-page">
    <div class="page-header">
      <h2>录制管理</h2>
      <div class="header-actions">
        <el-button
          type="primary"
          :disabled="selectedIds.length === 0"
          @click="handleBatchPublish"
        >
          批量发布 ({{ selectedIds.length }})
        </el-button>
        <el-button
          type="warning"
          :disabled="selectedIds.length === 0"
          @click="handleBatchOffline"
        >
          批量下架 ({{ selectedIds.length }})
        </el-button>
      </div>
    </div>

    <el-tabs v-model="activeTab" @tab-change="handleTabChange">
      <el-tab-pane label="全部" name="all" />
      <el-tab-pane name="pending">
        <template #label>
          待审核
          <el-badge v-if="pendingCount > 0" :value="pendingCount" class="tab-badge" />
        </template>
      </el-tab-pane>
      <el-tab-pane label="已发布" name="published" />
      <el-tab-pane label="已下架" name="offline" />
    </el-tabs>

    <el-table
      :data="videos"
      v-loading="loading"
      stripe
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="50" />
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column label="封面" width="80">
        <template #default="{ row }">
          <el-image
            v-if="row.thumbnail"
            :src="row.thumbnail"
            fit="cover"
            style="width: 60px; height: 40px; border-radius: 4px;"
            :preview-src-list="[row.thumbnail]"
          />
          <span v-else class="text-muted">-</span>
        </template>
      </el-table-column>
      <el-table-column prop="title" label="标题" show-overflow-tooltip min-width="150" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)" size="small">
            {{ getStatusLabel(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="分类" width="120">
        <template #default="{ row }">
          <el-tag v-if="row.category" size="small">{{ row.category.name }}</el-tag>
          <span v-else class="text-muted">-</span>
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
      <el-table-column prop="created_at" label="创建时间" width="160">
        <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="280" fixed="right">
        <template #default="{ row }">
          <el-button size="small" type="primary" @click="handleEdit(row)">编辑</el-button>
          <el-button
            v-if="row.file_type === 'video'"
            size="small"
            type="info"
            @click="handleExtractAudio(row)"
            :loading="extractingAudioId === row.id"
          >
            提取音频
          </el-button>
          <el-button
            v-if="row.status !== 'published'"
            size="small"
            type="success"
            @click="handlePublish(row)"
          >
            发布
          </el-button>
          <el-button
            v-if="row.status === 'published'"
            size="small"
            type="warning"
            @click="handleOffline(row)"
          >
            下架
          </el-button>
          <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- Edit Dialog -->
    <el-dialog v-model="showEditDialog" title="编辑视频" width="800px" top="5vh">
      <el-tabs v-model="editActiveTab">
        <!-- Basic Info Tab -->
        <el-tab-pane label="基本信息" name="basic">
          <el-form :model="editForm" label-width="80px">
            <el-form-item label="标题">
              <el-input v-model="editForm.title" />
            </el-form-item>
            <el-form-item label="描述">
              <el-input
                v-model="editForm.description"
                type="textarea"
                :rows="3"
                placeholder="请输入视频描述"
              />
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
        </el-tab-pane>

        <!-- Thumbnail Tab -->
        <el-tab-pane label="封面管理" name="thumbnail">
          <div class="thumbnail-section">
            <div class="current-thumbnail">
              <h4>当前封面</h4>
              <div class="thumbnail-preview">
                <el-image
                  v-if="editingVideo?.thumbnail"
                  :src="editingVideo.thumbnail"
                  fit="contain"
                  style="max-width: 300px; max-height: 200px;"
                />
                <div v-else class="no-thumbnail">暂无封面</div>
              </div>
            </div>
            <div class="thumbnail-actions">
              <el-button
                type="primary"
                @click="handleAutoCapture"
                :loading="capturingThumbnail"
              >
                自动截取封面
              </el-button>
              <el-upload
                :show-file-list="false"
                :before-upload="handleThumbnailUpload"
                accept="image/*"
              >
                <el-button type="success" :loading="uploadingThumbnail">
                  上传封面
                </el-button>
              </el-upload>
            </div>
            <div class="capture-at-section">
              <h4>指定时间截取</h4>
              <div class="capture-at-form">
                <el-input-number
                  v-model="captureTimestamp"
                  :min="0"
                  :max="editingVideo?.duration || 0"
                  placeholder="秒"
                />
                <span class="capture-hint">秒 (最大: {{ editingVideo?.duration || 0 }}秒)</span>
                <el-button
                  type="primary"
                  @click="handleCaptureAt"
                  :loading="capturingThumbnail"
                  :disabled="!captureTimestamp"
                >
                  截取
                </el-button>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <!-- Extensions Tab -->
        <el-tab-pane label="扩展信息" name="extensions">
          <VideoExtensions
            v-if="editingVideo"
            :video-id="editingVideo.id"
          />
        </el-tab-pane>

        <!-- Audio Tab -->
        <el-tab-pane label="音频管理" name="audio" v-if="editingVideo?.file_type === 'video'">
          <div class="audio-section" v-loading="loadingAudioInfo">
            <div v-if="audioInfo">
              <div v-if="audioInfo.has_audio" class="audio-available">
                <el-alert type="success" :closable="false">
                  <template #title>
                    音频已提取完成
                    <span v-if="audioInfo.file_size">
                      ({{ formatSize(audioInfo.file_size) }})
                    </span>
                  </template>
                </el-alert>
                <div class="audio-actions">
                  <el-button type="primary" @click="handleDownloadAudio">
                    下载音频
                  </el-button>
                </div>
              </div>
              <div v-else-if="audioInfo.task" class="audio-task">
                <el-alert
                  v-if="audioInfo.task.status === 'pending'"
                  type="info"
                  :closable="false"
                  title="音频提取任务等待中..."
                />
                <el-alert
                  v-else-if="audioInfo.task.status === 'processing'"
                  type="warning"
                  :closable="false"
                  title="音频正在提取中..."
                />
                <el-alert
                  v-else-if="audioInfo.task.status === 'failed'"
                  type="error"
                  :closable="false"
                  title="音频提取失败"
                />
              </div>
              <div v-else class="no-audio">
                <el-alert type="info" :closable="false" title="暂无提取的音频" />
                <div class="extract-form">
                  <el-form inline>
                    <el-form-item label="格式">
                      <el-select v-model="extractFormat" style="width: 100px">
                        <el-option label="MP3" value="mp3" />
                      </el-select>
                    </el-form-item>
                    <el-form-item label="比特率">
                      <el-select v-model="extractBitrate" style="width: 120px">
                        <el-option label="128kbps" value="128k" />
                        <el-option label="192kbps" value="192k" />
                        <el-option label="256kbps" value="256k" />
                        <el-option label="320kbps" value="320k" />
                      </el-select>
                    </el-form-item>
                    <el-form-item>
                      <el-button
                        type="primary"
                        @click="handleExtractAudioInDialog"
                        :loading="extractingAudio"
                      >
                        提取音频
                      </el-button>
                    </el-form-item>
                  </el-form>
                </div>
              </div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="saveEdit" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { UploadRawFile } from 'element-plus'
import { videosApi, type Video, type VideoStatus } from '../../api/videos'
import { categoriesApi, type Category } from '../../api/categories'
import { tagsApi, type Tag } from '../../api/tags'
import { audioApi, type AudioInfo } from '../../api/audio'
import { thumbnailApi } from '../../api/thumbnail'
import VideoExtensions from '../../components/VideoExtensions.vue'

const videos = ref<Video[]>([])
const allVideos = ref<Video[]>([])
const categories = ref<Category[]>([])
const tags = ref<Tag[]>([])
const loading = ref(false)
const showEditDialog = ref(false)
const saving = ref(false)
const editingVideo = ref<Video | null>(null)
const activeTab = ref('all')
const selectedIds = ref<number[]>([])
const editActiveTab = ref('basic')

// Thumbnail state
const capturingThumbnail = ref(false)
const uploadingThumbnail = ref(false)
const captureTimestamp = ref(0)

// Audio state
const audioInfo = ref<AudioInfo | null>(null)
const loadingAudioInfo = ref(false)
const extractingAudio = ref(false)
const extractingAudioId = ref<number | null>(null)
const extractFormat = ref('mp3')
const extractBitrate = ref('192k')

const editForm = reactive({
  title: '',
  description: '',
  category_id: null as number | null,
  tag_ids: [] as number[]
})

const pendingCount = computed(() => {
  return allVideos.value.filter(v => v.status === 'pending').length
})

const loadVideos = async () => {
  loading.value = true
  try {
    const { data } = await videosApi.list()
    allVideos.value = data
    filterVideos()
  } catch {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const filterVideos = () => {
  if (activeTab.value === 'all') {
    videos.value = allVideos.value
  } else {
    videos.value = allVideos.value.filter(v => v.status === activeTab.value)
  }
}

const handleTabChange = () => {
  filterVideos()
  selectedIds.value = []
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

const loadAudioInfo = async (videoId: number) => {
  loadingAudioInfo.value = true
  try {
    const { data } = await audioApi.getAudioInfo(videoId)
    audioInfo.value = data

    // Poll if task is in progress
    if (data.task?.status === 'pending' || data.task?.status === 'processing') {
      setTimeout(() => {
        if (editingVideo.value?.id === videoId) {
          loadAudioInfo(videoId)
        }
      }, 3000)
    }
  } catch (e) {
    console.error('Failed to load audio info', e)
  } finally {
    loadingAudioInfo.value = false
  }
}

const handleSelectionChange = (selection: Video[]) => {
  selectedIds.value = selection.map(v => v.id)
}

const handleEdit = (row: Video) => {
  editingVideo.value = row
  editForm.title = row.title
  editForm.description = row.description || ''
  editForm.category_id = row.category_id
  editForm.tag_ids = row.tags?.map(t => t.id) || []
  editActiveTab.value = 'basic'
  captureTimestamp.value = 0
  audioInfo.value = null
  showEditDialog.value = true

  // Load audio info if video type
  if (row.file_type === 'video') {
    loadAudioInfo(row.id)
  }
}

const saveEdit = async () => {
  if (!editingVideo.value) return

  saving.value = true
  try {
    // Update title and description
    if (editForm.title !== editingVideo.value.title || editForm.description !== (editingVideo.value.description || '')) {
      await videosApi.update(editingVideo.value.id, {
        title: editForm.title,
        description: editForm.description || undefined
      })
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

// Thumbnail handlers
const handleAutoCapture = async () => {
  if (!editingVideo.value) return
  capturingThumbnail.value = true
  try {
    const { data } = await thumbnailApi.autoCapture(editingVideo.value.id)
    editingVideo.value.thumbnail = data.thumbnail_url
    ElMessage.success('封面截取成功')
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '封面截取失败')
  } finally {
    capturingThumbnail.value = false
  }
}

const handleThumbnailUpload = async (file: UploadRawFile) => {
  if (!editingVideo.value) return false
  uploadingThumbnail.value = true
  try {
    const { data } = await thumbnailApi.upload(editingVideo.value.id, file)
    editingVideo.value.thumbnail = data.thumbnail_url
    ElMessage.success('封面上传成功')
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '封面上传失败')
  } finally {
    uploadingThumbnail.value = false
  }
  return false
}

const handleCaptureAt = async () => {
  if (!editingVideo.value || !captureTimestamp.value) return
  capturingThumbnail.value = true
  try {
    const { data } = await thumbnailApi.captureAt(editingVideo.value.id, captureTimestamp.value)
    editingVideo.value.thumbnail = data.thumbnail_url
    ElMessage.success('封面截取成功')
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '封面截取失败')
  } finally {
    capturingThumbnail.value = false
  }
}

// Audio handlers
const handleExtractAudio = async (row: Video) => {
  extractingAudioId.value = row.id
  try {
    await audioApi.extractAudio(row.id)
    ElMessage.success('音频提取任务已创建')
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '音频提取失败')
  } finally {
    extractingAudioId.value = null
  }
}

const handleExtractAudioInDialog = async () => {
  if (!editingVideo.value) return
  extractingAudio.value = true
  try {
    await audioApi.extractAudio(editingVideo.value.id, extractFormat.value, extractBitrate.value)
    ElMessage.success('音频提取任务已创建')
    loadAudioInfo(editingVideo.value.id)
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '音频提取失败')
  } finally {
    extractingAudio.value = false
  }
}

const handleDownloadAudio = () => {
  if (!editingVideo.value) return
  window.open(audioApi.getDownloadUrl(editingVideo.value.id), '_blank')
}

const handlePublish = async (row: Video) => {
  try {
    await ElMessageBox.confirm('确定要发布该视频吗？', '提示', { type: 'info' })
    await videosApi.publish(row.id)
    ElMessage.success('发布成功')
    loadVideos()
  } catch (e: any) {
    if (e !== 'cancel') ElMessage.error(e.response?.data?.detail || '发布失败')
  }
}

const handleOffline = async (row: Video) => {
  try {
    await ElMessageBox.confirm('确定要下架该视频吗？', '提示', { type: 'warning' })
    await videosApi.offline(row.id)
    ElMessage.success('下架成功')
    loadVideos()
  } catch (e: any) {
    if (e !== 'cancel') ElMessage.error(e.response?.data?.detail || '下架失败')
  }
}

const handleBatchPublish = async () => {
  if (selectedIds.value.length === 0) return
  try {
    await ElMessageBox.confirm(`确定要批量发布 ${selectedIds.value.length} 个视频吗？`, '提示', { type: 'info' })
    const { data } = await videosApi.batchPublish(selectedIds.value)
    ElMessage.success(`成功发布 ${data.success} 个视频${data.failed > 0 ? `，${data.failed} 个失败` : ''}`)
    selectedIds.value = []
    loadVideos()
  } catch (e: any) {
    if (e !== 'cancel') ElMessage.error(e.response?.data?.detail || '批量发布失败')
  }
}

const handleBatchOffline = async () => {
  if (selectedIds.value.length === 0) return
  try {
    await ElMessageBox.confirm(`确定要批量下架 ${selectedIds.value.length} 个视频吗？`, '提示', { type: 'warning' })
    const { data } = await videosApi.batchOffline(selectedIds.value)
    ElMessage.success(`成功下架 ${data.success} 个视频${data.failed > 0 ? `，${data.failed} 个失败` : ''}`)
    selectedIds.value = []
    loadVideos()
  } catch (e: any) {
    if (e !== 'cancel') ElMessage.error(e.response?.data?.detail || '批量下架失败')
  }
}

const handleDelete = async (row: Video) => {
  try {
    await ElMessageBox.confirm('确定要删除该视频吗？此操作将同时删除文件！', '提示', { type: 'warning' })
    await videosApi.delete(row.id)
    ElMessage.success('删除成功')
    loadVideos()
  } catch (e: any) {
    if (e !== 'cancel') ElMessage.error(e.response?.data?.detail || '删除失败')
  }
}

const getStatusType = (status: VideoStatus) => {
  switch (status) {
    case 'pending': return 'warning'
    case 'published': return 'success'
    case 'offline': return 'info'
    default: return 'info'
  }
}

const getStatusLabel = (status: VideoStatus) => {
  switch (status) {
    case 'pending': return '待审核'
    case 'published': return '已发布'
    case 'offline': return '已下架'
    default: return status
  }
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
.recordings-page {
  padding: 20px;
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.header-actions {
  display: flex;
  gap: 10px;
}
.text-muted {
  color: #909399;
}
.tab-badge {
  margin-left: 5px;
}
.tab-badge :deep(.el-badge__content) {
  top: -2px;
}

/* Thumbnail section */
.thumbnail-section {
  padding: 16px 0;
}
.current-thumbnail {
  margin-bottom: 20px;
}
.current-thumbnail h4 {
  margin: 0 0 12px;
  color: #303133;
}
.thumbnail-preview {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  min-height: 150px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.no-thumbnail {
  color: #909399;
}
.thumbnail-actions {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}
.capture-at-section h4 {
  margin: 0 0 12px;
  color: #303133;
}
.capture-at-form {
  display: flex;
  align-items: center;
  gap: 12px;
}
.capture-hint {
  color: #909399;
  font-size: 13px;
}

/* Audio section */
.audio-section {
  padding: 16px 0;
}
.audio-available,
.audio-task,
.no-audio {
  margin-bottom: 16px;
}
.audio-actions {
  margin-top: 16px;
  display: flex;
  gap: 12px;
}
.extract-form {
  margin-top: 16px;
}
</style>
