<template>
  <div class="upload-page">
    <div class="page-header">
      <h2>文件上传</h2>
    </div>

    <!-- Upload Area -->
    <div
      class="upload-area"
      :class="{ 'is-dragover': isDragover }"
      @dragover.prevent="isDragover = true"
      @dragleave.prevent="isDragover = false"
      @drop.prevent="handleDrop"
      @click="triggerFileInput"
    >
      <input
        ref="fileInput"
        type="file"
        accept=".mp4,.mp3,.wav,.aac,.flac"
        @change="handleFileSelect"
        style="display: none"
      />
      <el-icon class="upload-icon" :size="48"><UploadFilled /></el-icon>
      <p class="upload-text">拖拽文件到此处，或点击选择文件</p>
      <p class="upload-hint">支持 MP4 视频（最大 10GB）和 MP3/WAV/AAC/FLAC 音频（最大 1GB）</p>
    </div>

    <!-- Upload Progress -->
    <div v-if="currentUpload" class="upload-progress">
      <div class="upload-info">
        <span class="filename">{{ currentUpload.filename }}</span>
        <span class="status">{{ uploadStatusText }}</span>
      </div>
      <el-progress
        :percentage="uploadProgress"
        :status="uploadProgressStatus"
      />
      <div class="upload-actions">
        <el-button
          v-if="currentUpload.status === 'uploading'"
          size="small"
          @click="togglePause"
        >
          {{ isPaused ? '继续' : '暂停' }}
        </el-button>
        <el-button
          v-if="currentUpload.status === 'uploading'"
          size="small"
          type="danger"
          @click="cancelUpload"
        >
          取消
        </el-button>
      </div>
    </div>

    <!-- Upload Complete Form -->
    <el-card v-if="showCompleteForm" class="complete-form">
      <template #header>
        <span>设置视频信息</span>
      </template>
      <el-form :model="completeForm" label-width="80px">
        <el-form-item label="标题">
          <el-input v-model="completeForm.title" placeholder="视频标题" />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="completeForm.category_id" placeholder="选择分类" clearable style="width: 100%">
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
            v-model="completeForm.tag_ids"
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
        <el-form-item>
          <el-button type="primary" @click="completeUpload" :loading="completing">
            完成上传
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- Upload History -->
    <div v-if="uploadHistory.length > 0" class="upload-history">
      <h3>上传历史</h3>
      <el-table :data="uploadHistory" stripe>
        <el-table-column prop="filename" label="文件名" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'completed' ? 'success' : 'danger'">
              {{ row.status === 'completed' ? '成功' : '失败' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="video_id" label="视频ID" width="100" />
      </el-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import { uploadApi } from '../../api/upload'
import { categoriesApi, type Category } from '../../api/categories'
import { tagsApi, type Tag } from '../../api/tags'

const fileInput = ref<HTMLInputElement>()
const isDragover = ref(false)
const categories = ref<Category[]>([])
const tags = ref<Tag[]>([])

interface UploadState {
  taskId: string
  filename: string
  fileSize: number
  chunkSize: number
  totalChunks: number
  uploadedChunks: number
  status: 'uploading' | 'completed' | 'failed'
  file: File
}

const currentUpload = ref<UploadState | null>(null)
const isPaused = ref(false)
const showCompleteForm = ref(false)
const completing = ref(false)

const completeForm = reactive({
  title: '',
  category_id: null as number | null,
  tag_ids: [] as number[]
})

interface UploadHistoryItem {
  filename: string
  status: 'completed' | 'failed'
  video_id?: number
}

const uploadHistory = ref<UploadHistoryItem[]>([])

const uploadProgress = computed(() => {
  if (!currentUpload.value) return 0
  return Math.round((currentUpload.value.uploadedChunks / currentUpload.value.totalChunks) * 100)
})

const uploadStatusText = computed(() => {
  if (!currentUpload.value) return ''
  if (isPaused.value) return '已暂停'
  if (currentUpload.value.status === 'completed') return '上传完成'
  if (currentUpload.value.status === 'failed') return '上传失败'
  return `${currentUpload.value.uploadedChunks}/${currentUpload.value.totalChunks} 分片`
})

const uploadProgressStatus = computed(() => {
  if (!currentUpload.value) return ''
  if (currentUpload.value.status === 'completed') return 'success'
  if (currentUpload.value.status === 'failed') return 'exception'
  return ''
})

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleDrop = (e: DragEvent) => {
  isDragover.value = false
  const files = e.dataTransfer?.files
  if (files && files.length > 0) {
    startUpload(files[0])
  }
}

const handleFileSelect = (e: Event) => {
  const input = e.target as HTMLInputElement
  if (input.files && input.files.length > 0) {
    startUpload(input.files[0])
    input.value = ''
  }
}

const startUpload = async (file: File) => {
  // Validate file type
  const ext = file.name.toLowerCase().split('.').pop()
  const allowedExts = ['mp4', 'mp3', 'wav', 'aac', 'flac']
  if (!ext || !allowedExts.includes(ext)) {
    ElMessage.error('不支持的文件格式')
    return
  }

  // Validate file size
  const maxSize = ext === 'mp4' ? 10 * 1024 * 1024 * 1024 : 1024 * 1024 * 1024
  if (file.size > maxSize) {
    ElMessage.error(`文件过大，最大支持 ${ext === 'mp4' ? '10GB' : '1GB'}`)
    return
  }

  try {
    // Initialize upload
    const chunkSize = 5 * 1024 * 1024 // 5MB
    const { data } = await uploadApi.init({
      filename: file.name,
      file_size: file.size,
      chunk_size: chunkSize
    })

    currentUpload.value = {
      taskId: data.task_id,
      filename: file.name,
      fileSize: file.size,
      chunkSize: data.chunk_size,
      totalChunks: data.total_chunks,
      uploadedChunks: 0,
      status: 'uploading',
      file
    }

    completeForm.title = file.name.replace(/\.[^/.]+$/, '')
    isPaused.value = false
    showCompleteForm.value = false

    // Start uploading chunks
    await uploadChunks()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '初始化上传失败')
  }
}

const uploadChunks = async () => {
  if (!currentUpload.value) return

  const { taskId, file, chunkSize, totalChunks } = currentUpload.value

  for (let i = currentUpload.value.uploadedChunks; i < totalChunks; i++) {
    if (isPaused.value || !currentUpload.value) return

    const start = i * chunkSize
    const end = Math.min(start + chunkSize, file.size)
    const chunk = file.slice(start, end)

    try {
      const { data } = await uploadApi.uploadChunk(taskId, i, chunk)
      if (currentUpload.value) {
        currentUpload.value.uploadedChunks = data.uploaded_chunks
      }
    } catch (e: any) {
      ElMessage.error(`分片 ${i + 1} 上传失败`)
      if (currentUpload.value) {
        currentUpload.value.status = 'failed'
      }
      return
    }
  }

  // All chunks uploaded
  if (currentUpload.value && currentUpload.value.uploadedChunks === totalChunks) {
    showCompleteForm.value = true
  }
}

const togglePause = () => {
  isPaused.value = !isPaused.value
  if (!isPaused.value) {
    uploadChunks()
  }
}

const cancelUpload = async () => {
  if (!currentUpload.value) return

  try {
    await uploadApi.cancel(currentUpload.value.taskId)
    ElMessage.info('上传已取消')
  } catch (e) {
    // Ignore error
  }

  currentUpload.value = null
  showCompleteForm.value = false
}

const completeUpload = async () => {
  if (!currentUpload.value) return

  completing.value = true
  try {
    const result = await uploadApi.complete(currentUpload.value.taskId, {
      title: completeForm.title || undefined,
      category_id: completeForm.category_id || undefined,
      tag_ids: completeForm.tag_ids.length > 0 ? completeForm.tag_ids : undefined
    })

    uploadHistory.value.unshift({
      filename: currentUpload.value.filename,
      status: 'completed',
      video_id: result.data.video_id
    })

    ElMessage.success('上传完成')
    currentUpload.value = null
    showCompleteForm.value = false

    // Reset form
    completeForm.title = ''
    completeForm.category_id = null
    completeForm.tag_ids = []
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '完成上传失败')
    if (currentUpload.value) {
      uploadHistory.value.unshift({
        filename: currentUpload.value.filename,
        status: 'failed'
      })
    }
  } finally {
    completing.value = false
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

const loadTags = async () => {
  try {
    const { data } = await tagsApi.list()
    tags.value = data
  } catch (e) {
    console.error('Failed to load tags', e)
  }
}

onMounted(() => {
  loadCategories()
  loadTags()
})
</script>

<style scoped>
.upload-page {
  padding: 0;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h2 {
  font-size: 20px;
  font-weight: 600;
  color: #fff;
  margin: 0;
}

.upload-area {
  border: 2px dashed rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 60px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  background: rgba(15, 20, 35, 0.4);
}

.upload-area:hover,
.upload-area.is-dragover {
  border-color: #E94560;
  background: rgba(233, 69, 96, 0.05);
}

.upload-icon {
  color: rgba(255, 255, 255, 0.4);
}

.upload-text {
  margin: 16px 0 8px;
  font-size: 16px;
  color: #e4e7eb;
  font-weight: 500;
}

.upload-hint {
  margin: 0;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
}

.upload-progress {
  margin-top: 20px;
  padding: 16px;
  background: rgba(15, 20, 35, 0.6);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 12px;
}

.upload-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  color: #e4e7eb;
}

.filename {
  font-weight: 500;
  color: #fff;
}

.status {
  color: rgba(255, 255, 255, 0.6);
}

.upload-actions {
  margin-top: 12px;
  display: flex;
  gap: 8px;
}

.complete-form {
  margin-top: 20px;
}

.upload-history {
  margin-top: 40px;
}

.upload-history h3 {
  margin-bottom: 16px;
  font-size: 18px;
  font-weight: 600;
  color: #fff;
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

:deep(.el-button--success) {
  background: rgba(16, 185, 129, 0.2);
  border: 1px solid rgba(16, 185, 129, 0.4);
  color: #10b981;
}

:deep(.el-button--success:hover) {
  background: rgba(16, 185, 129, 0.3);
  border-color: rgba(16, 185, 129, 0.6);
}

/* Progress styles */
:deep(.el-progress__text) {
  color: #e4e7eb;
}

:deep(.el-progress-bar__outer) {
  background: rgba(255, 255, 255, 0.1);
}

:deep(.el-progress-bar__inner) {
  background: linear-gradient(135deg, #E94560 0%, #8B5CF6 100%);
}

/* ==================== Mobile Responsive ==================== */
@media (max-width: 768px) {
  .page-header h2 {
    font-size: 18px;
  }

  .upload-area {
    padding: 40px 16px;
  }

  .upload-text {
    font-size: 14px;
  }

  .upload-hint {
    font-size: 11px;
  }

  .upload-info {
    flex-direction: column;
    gap: 4px;
  }

  .filename {
    font-size: 13px;
    word-break: break-all;
  }

  .upload-actions {
    flex-wrap: wrap;
  }

  .upload-actions .el-button {
    flex: 1;
  }

  .complete-form :deep(.el-form-item__label) {
    width: 80px !important;
  }

  /* Table on mobile */
  :deep(.el-table) {
    font-size: 12px;
  }

  :deep(.el-table th),
  :deep(.el-table td) {
    padding: 8px 4px;
  }

  /* Card styles for mobile */
  :deep(.el-card) {
    background: rgba(15, 20, 35, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.05);
  }

  :deep(.el-card__header) {
    background: rgba(15, 20, 35, 0.8);
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  }

  :deep(.el-card__body) {
    padding: 16px;
  }
}
</style>
