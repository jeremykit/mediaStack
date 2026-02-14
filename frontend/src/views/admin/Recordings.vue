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
      <el-table-column prop="title" label="标题" min-width="100" class-name="title-column" show-overflow-tooltip />
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
      <el-table-column label="操作" fixed="right">
        <template #default="{ row }">
          <el-button size="small" type="primary" @click="handleEdit(row)">编辑</el-button>
          <el-button
            v-if="row.source_type === 'recorded' && row.file_type === 'video'"
            size="small"
            type="warning"
            @click="handleTrim(row)"
          >
            裁剪
          </el-button>
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

    <!-- Mobile Card Layout -->
    <div class="mobile-recording-cards" v-loading="loading">
      <!-- Mobile tabs -->
      <div class="mobile-tabs">
        <div
          v-for="tab in mobileTabs"
          :key="tab.value"
          class="mobile-tab"
          :class="{ active: activeTab === tab.value }"
          @click="activeTab = tab.value; handleTabChange()"
        >
          {{ tab.label }}
          <span v-if="tab.badge && tab.badge > 0" class="mobile-tab-badge">{{ tab.badge }}</span>
        </div>
      </div>

      <div
        v-for="video in videos"
        :key="video.id"
        class="recording-card"
      >
        <div class="recording-card-header">
          <div class="recording-card-title">
            <div class="recording-card-name">{{ video.title }}</div>
            <div class="recording-card-id">ID: {{ video.id }}</div>
          </div>
          <el-checkbox
            :model-value="selectedIds.includes(video.id)"
            @change="toggleSelection(video.id)"
          ></el-checkbox>
        </div>

        <div class="recording-card-thumbnail" v-if="video.thumbnail">
          <img :src="video.thumbnail" alt="封面" />
        </div>

        <div class="recording-card-meta">
          <el-tag :type="getStatusType(video.status)" size="small">
            {{ getStatusLabel(video.status) }}
          </el-tag>
          <el-tag :type="video.file_type === 'video' ? 'primary' : 'success'" size="small">
            {{ video.file_type === 'video' ? '视频' : '音频' }}
          </el-tag>
          <span class="recording-card-duration">{{ formatDuration(video.duration) }}</span>
          <span class="recording-card-size">{{ formatSize(video.file_size) }}</span>
        </div>

        <div class="recording-card-row" v-if="video.category">
          <span class="recording-card-label">分类</span>
          <el-tag size="small">{{ video.category.name }}</el-tag>
        </div>

        <div class="recording-card-time">{{ formatTime(video.created_at) }}</div>

        <div class="recording-card-actions">
          <el-button size="small" type="primary" @click="handleEdit(video)">编辑</el-button>
          <el-button
            v-if="video.source_type === 'recorded' && video.file_type === 'video'"
            size="small"
            type="warning"
            @click="handleTrim(video)"
          >裁剪</el-button>
          <el-button
            v-if="video.status !== 'published'"
            size="small"
            type="success"
            @click="handlePublish(video)"
          >发布</el-button>
          <el-button
            v-else
            size="small"
            type="warning"
            @click="handleOffline(video)"
          >下架</el-button>
          <el-button size="small" type="danger" @click="handleDelete(video)">删除</el-button>
        </div>
      </div>

      <div v-if="videos.length === 0 && !loading" class="empty-state">
        <p>暂无录制视频</p>
      </div>
    </div>

    <!-- Edit Dialog -->
    <el-dialog v-model="showEditDialog" title="编辑视频" width="800px" top="5vh" :class="{ 'mobile-dialog': isMobile }">
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
              <el-select
                v-model="editForm.category_id"
                placeholder="选择分类"
                clearable
                style="width: 100%"
                :teleported="!isMobile"
                :popper-class="{ 'mobile-select-dropdown': isMobile }"
              >
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
                :teleported="!isMobile"
                :popper-class="{ 'mobile-select-dropdown': isMobile }"
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
                      <el-select
                        v-model="extractFormat"
                        style="width: 100px"
                        :teleported="!isMobile"
                        :popper-class="{ 'mobile-select-dropdown': isMobile }"
                      >
                        <el-option label="MP3" value="mp3" />
                      </el-select>
                    </el-form-item>
                    <el-form-item label="比特率">
                      <el-select
                        v-model="extractBitrate"
                        style="width: 120px"
                        :teleported="!isMobile"
                        :popper-class="{ 'mobile-select-dropdown': isMobile }"
                      >
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

    <!-- Video Trim Dialog -->
    <VideoTrimDialog
      v-model="showTrimDialog"
      :video-id="trimmingVideo?.id || 0"
      :video-url="getTrimVideoUrl()"
      :duration="trimmingVideo?.duration || 0"
      @success="handleTrimSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { UploadRawFile } from 'element-plus'
import { videosApi, type Video, type VideoStatus } from '../../api/videos'
import { categoriesApi, type Category } from '../../api/categories'
import { tagsApi, type Tag } from '../../api/tags'
import { audioApi, type AudioInfo } from '../../api/audio'
import { thumbnailApi } from '../../api/thumbnail'
import VideoExtensions from '../../components/VideoExtensions.vue'
import VideoTrimDialog from '../../components/VideoTrimDialog.vue'

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

// Mobile detection
const isMobile = ref(false)
const checkMobile = () => {
  isMobile.value = window.innerWidth < 768
}

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

// Trim state
const showTrimDialog = ref(false)
const trimmingVideo = ref<Video | null>(null)

const editForm = reactive({
  title: '',
  description: '',
  category_id: null as number | null,
  tag_ids: [] as number[]
})

const pendingCount = computed(() => {
  return allVideos.value.filter(v => v.status === 'pending').length
})

const mobileTabs = computed(() => [
  { value: 'all', label: '全部' },
  { value: 'pending', label: '待审核', badge: pendingCount.value },
  { value: 'published', label: '已发布' },
  { value: 'offline', label: '已下架' }
])

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

const toggleSelection = (id: number) => {
  const index = selectedIds.value.indexOf(id)
  if (index > -1) {
    selectedIds.value.splice(index, 1)
  } else {
    selectedIds.value.push(id)
  }
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

const handleTrim = (row: Video) => {
  trimmingVideo.value = row
  showTrimDialog.value = true
}

const handleTrimSuccess = () => {
  ElMessage.success('视频裁剪完成，状态已重置为待审核')
  loadVideos()
}

const getTrimVideoUrl = (): string => {
  if (!trimmingVideo.value) return ''
  return `/api/videos/${trimmingVideo.value.id}/stream`
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
  checkMobile()
  window.addEventListener('resize', checkMobile)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})
</script>

<style scoped>
.recordings-page {
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

.header-actions {
  display: flex;
  gap: 10px;
}

.text-muted {
  color: rgba(255, 255, 255, 0.4);
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
  color: #fff;
  font-weight: 600;
}

.thumbnail-preview {
  background: rgba(15, 20, 35, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  min-height: 150px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.no-thumbnail {
  color: rgba(255, 255, 255, 0.4);
}

.thumbnail-actions {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.capture-at-section h4 {
  margin: 0 0 12px;
  color: #fff;
  font-weight: 600;
}

.capture-at-form {
  display: flex;
  align-items: center;
  gap: 12px;
}

.capture-hint {
  color: rgba(255, 255, 255, 0.4);
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
  color: #e4e7eb;
}

.audio-actions {
  margin-top: 16px;
  display: flex;
  gap: 12px;
}

.extract-form {
  margin-top: 16px;
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

/* Title column: adaptive width with max-width and tooltip */
:deep(.title-column .cell) {
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

:deep(.title-column) {
  position: relative;
}

:deep(.title-column:hover .cell) {
  cursor: help;
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

:deep(.el-button--warning) {
  background: rgba(245, 158, 11, 0.2);
  border: 1px solid rgba(245, 158, 11, 0.4);
  color: #f59e0b;
}

:deep(.el-button--warning:hover) {
  background: rgba(245, 158, 11, 0.3);
  border-color: rgba(245, 158, 11, 0.6);
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

:deep(.el-button--success) {
  background: rgba(16, 185, 129, 0.2);
  border: 1px solid rgba(16, 185, 129, 0.4);
  color: #10b981;
}

:deep(.el-button--success:hover) {
  background: rgba(16, 185, 129, 0.3);
  border-color: rgba(16, 185, 129, 0.6);
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

:deep(.el-tag--warning) {
  background: rgba(245, 158, 11, 0.2);
  color: #f59e0b;
}

:deep(.el-tag--danger) {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

:deep(.el-tag--info) {
  background: rgba(107, 114, 128, 0.2);
  color: #9ca3af;
}

/* Tabs styles */
:deep(.el-tabs__header) {
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  margin-bottom: 24px;
}

:deep(.el-tabs__item) {
  color: rgba(255, 255, 255, 0.6);
  font-weight: 500;
}

:deep(.el-tabs__item:hover) {
  color: #E94560;
}

:deep(.el-tabs__item.is-active) {
  color: #E94560;
}

:deep(.el-tabs__active-bar) {
  background: linear-gradient(135deg, #E94560 0%, #8B5CF6 100%);
}

/* Badge styles */
:deep(.el-badge__content) {
  background: linear-gradient(135deg, #E94560 0%, #8B5CF6 100%);
  border: none;
}

/* Image styles */
:deep(.el-image) {
  border-radius: 8px;
  overflow: hidden;
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

  .header-actions {
    width: 100%;
    flex-wrap: wrap;
  }

  .header-actions .el-button {
    flex: 1;
    min-width: 120px;
  }

  /* Hide default tabs and table on mobile */
  :deep(.el-tabs) {
    display: none;
  }

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
  .mobile-recording-cards {
    display: none !important;
  }
}

/* Mobile Card Layout */
@media (max-width: 768px) {
  .mobile-recording-cards {
    display: block !important;
  }

  .mobile-tabs {
    display: flex;
    overflow-x: auto;
    gap: 8px;
    margin-bottom: 16px;
    padding-bottom: 8px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  }

  .mobile-tab {
    flex-shrink: 0;
    padding: 8px 16px;
    border-radius: 8px;
    color: rgba(255, 255, 255, 0.6);
    font-size: 14px;
    white-space: nowrap;
    position: relative;
  }

  .mobile-tab.active {
    background: rgba(233, 69, 96, 0.2);
    color: #E94560;
  }

  .mobile-tab-badge {
    position: absolute;
    top: -4px;
    right: -4px;
    background: #E94560;
    color: white;
    font-size: 10px;
    padding: 2px 6px;
    border-radius: 10px;
    min-width: 16px;
    text-align: center;
  }

  .recording-card {
    background: rgba(15, 20, 35, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 12px;
    backdrop-filter: blur(10px);
  }

  .recording-card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 12px;
  }

  .recording-card-title {
    flex: 1;
    min-width: 0;
    padding-right: 12px;
  }

  .recording-card-name {
    font-size: 15px;
    font-weight: 600;
    color: #fff;
    margin-bottom: 4px;
    line-height: 1.4;
  }

  .recording-card-id {
    font-size: 11px;
    color: rgba(255, 255, 255, 0.4);
    font-family: var(--font-mono);
  }

  .recording-card-thumbnail {
    width: 100%;
    height: 160px;
    border-radius: 8px;
    overflow: hidden;
    margin-bottom: 12px;
    background: rgba(0, 0, 0, 0.3);
  }

  .recording-card-thumbnail img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .recording-card-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 10px;
  }

  .recording-card-duration,
  .recording-card-size {
    display: flex;
    align-items: center;
    font-size: 12px;
    color: rgba(255, 255, 255, 0.5);
  }

  .recording-card-row {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 10px;
  }

  .recording-card-label {
    color: rgba(255, 255, 255, 0.5);
    font-size: 12px;
    min-width: 50px;
  }

  .recording-card-time {
    font-size: 11px;
    color: rgba(255, 255, 255, 0.4);
    margin-bottom: 10px;
  }

  .recording-card-actions {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    padding-top: 10px;
    border-top: 1px solid rgba(255, 255, 255, 0.08);
  }

  .recording-card-actions .el-button {
    flex: 0 1 auto;
    min-width: 60px;
  }
}

/* ==================== Dialog Mobile Responsive ==================== */
@media (max-width: 768px) {
  /* Remove dialog styles that conflict with global theme - use global instead */

  /* Dialog tab content specific fixes */
  :deep(.el-dialog .el-tabs__content) {
    padding: 12px 0 !important;
  }

  :deep(.el-dialog .el-tab-pane) {
    padding: 0 4px !important;
  }

  /* Thumbnail section */
  .thumbnail-section {
    padding: 12px 0 !important;
  }

  .current-thumbnail h4 {
    font-size: 14px !important;
    margin-bottom: 8px !important;
  }

  .thumbnail-preview {
    padding: 12px !important;
    min-height: 120px !important;
  }

  .no-thumbnail {
    font-size: 12px !important;
  }

  .thumbnail-actions {
    flex-wrap: wrap !important;
    gap: 8px !important;
  }

  .capture-at-section h4 {
    font-size: 14px !important;
    margin-bottom: 8px !important;
  }

  .capture-at-form {
    flex-wrap: wrap !important;
  }

  .capture-hint {
    font-size: 11px !important;
  }

  /* Audio section */
  .audio-section {
    padding: 12px 0 !important;
  }

  .audio-available,
  .audio-task,
  .no-audio {
    margin-bottom: 12px !important;
  }

  .audio-actions {
    margin-top: 12px !important;
  }

  .extract-form {
    margin-top: 12px !important;
  }

  .extract-form :deep(.el-form) {
    display: block !important;
  }

  .extract-form :deep(.el-form-item) {
    display: block !important;
    margin-bottom: 12px !important;
  }

  .extract-form :deep(.el-form-item__content) {
    width: 100% !important;
  }
}
</style>
