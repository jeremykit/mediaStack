<template>
  <el-dialog
    v-model="visible"
    title="视频裁剪"
    width="900px"
    top="5vh"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <div class="trim-dialog-content" v-loading="loading">
      <!-- Video Preview -->
      <div class="video-preview-section">
        <h4>视频预览</h4>
        <video
          ref="videoRef"
          :src="videoUrl"
          controls
          class="video-player"
          @loadedmetadata="handleVideoLoaded"
        />
      </div>

      <!-- Timeline Slider -->
      <div class="timeline-section">
        <h4>选择裁剪范围</h4>
        <div class="timeline-slider">
          <el-slider
            v-model="timeRange"
            range
            :min="0"
            :max="videoDuration"
            :step="1"
            :format-tooltip="formatTooltip"
            @change="handleTimeRangeChange"
          />
        </div>
        <div class="timeline-labels">
          <span>{{ formatTime(0) }}</span>
          <span>{{ formatTime(videoDuration) }}</span>
        </div>
      </div>

      <!-- Time Inputs -->
      <div class="time-inputs-section">
        <el-form :model="trimForm" label-width="80px">
          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item label="开始时间">
                <el-input
                  v-model="startTimeStr"
                  placeholder="HH:MM:SS"
                  @blur="handleStartTimeInput"
                />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="结束时间">
                <el-input
                  v-model="endTimeStr"
                  placeholder="HH:MM:SS"
                  @blur="handleEndTimeInput"
                />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="裁剪时长">
                <el-input
                  :value="formatTime(trimDuration)"
                  readonly
                  disabled
                />
              </el-form-item>
            </el-col>
          </el-row>

          <!-- Options -->
          <el-form-item label="选项">
            <el-checkbox v-model="trimForm.extract_audio">
              提取音频 (192kbps MP3)
            </el-checkbox>
            <el-checkbox v-model="trimForm.keep_original" style="margin-left: 20px">
              保留原文件
            </el-checkbox>
          </el-form-item>
        </el-form>
      </div>

      <!-- Task Status -->
      <div v-if="taskStatus" class="task-status-section">
        <el-alert
          :type="getTaskAlertType(taskStatus)"
          :closable="false"
          show-icon
        >
          <template #title>
            {{ getTaskStatusText(taskStatus) }}
          </template>
        </el-alert>
        <div v-if="taskError" class="task-error">
          <el-text type="danger">{{ taskError }}</el-text>
        </div>
      </div>
    </div>

    <template #footer>
      <el-button @click="handleClose" :disabled="processing">取消</el-button>
      <el-button
        type="primary"
        @click="handleSubmit"
        :loading="processing"
        :disabled="!isValidRange || processing"
      >
        {{ processing ? '处理中...' : '开始裁剪' }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { videoTrimApi, type TrimTaskStatus } from '../api/videoTrim'

interface Props {
  modelValue: boolean
  videoId: number
  videoUrl: string
  duration: number
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'success'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const videoRef = ref<HTMLVideoElement>()
const loading = ref(false)
const processing = ref(false)
const videoDuration = ref(props.duration || 0)
const timeRange = ref<[number, number]>([0, props.duration || 0])
const startTimeStr = ref('00:00:00')
const endTimeStr = ref('00:00:00')
const taskStatus = ref<TrimTaskStatus | null>(null)
const taskError = ref<string | null>(null)
const currentTaskId = ref<number | null>(null)
const pollingInterval = ref<number | null>(null)

const trimForm = ref({
  extract_audio: false,
  keep_original: false
})

const trimDuration = computed(() => {
  return timeRange.value[1] - timeRange.value[0]
})

const isValidRange = computed(() => {
  return timeRange.value[0] < timeRange.value[1] && trimDuration.value > 0
})

// Format seconds to HH:MM:SS
const formatTime = (seconds: number): string => {
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = Math.floor(seconds % 60)
  return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
}

// Format tooltip for slider
const formatTooltip = (value: number): string => {
  return formatTime(value)
}

// Parse HH:MM:SS to seconds
const parseTimeString = (timeStr: string): number | null => {
  const parts = timeStr.split(':')
  if (parts.length !== 3) return null

  const h = parseInt(parts[0])
  const m = parseInt(parts[1])
  const s = parseInt(parts[2])

  if (isNaN(h) || isNaN(m) || isNaN(s)) return null
  if (m >= 60 || s >= 60) return null

  return h * 3600 + m * 60 + s
}

// Handle video loaded
const handleVideoLoaded = () => {
  if (videoRef.value) {
    videoDuration.value = Math.floor(videoRef.value.duration)
    timeRange.value = [0, videoDuration.value]
    updateTimeStrings()
  }
}

// Update time strings from range
const updateTimeStrings = () => {
  startTimeStr.value = formatTime(timeRange.value[0])
  endTimeStr.value = formatTime(timeRange.value[1])
}

// Handle time range change from slider
const handleTimeRangeChange = () => {
  updateTimeStrings()
}

// Handle start time input
const handleStartTimeInput = () => {
  const seconds = parseTimeString(startTimeStr.value)
  if (seconds !== null && seconds >= 0 && seconds < timeRange.value[1]) {
    timeRange.value = [seconds, timeRange.value[1]]
  } else {
    // Reset to current value
    startTimeStr.value = formatTime(timeRange.value[0])
    ElMessage.warning('开始时间格式不正确或超出范围')
  }
}

// Handle end time input
const handleEndTimeInput = () => {
  const seconds = parseTimeString(endTimeStr.value)
  if (seconds !== null && seconds > timeRange.value[0] && seconds <= videoDuration.value) {
    timeRange.value = [timeRange.value[0], seconds]
  } else {
    // Reset to current value
    endTimeStr.value = formatTime(timeRange.value[1])
    ElMessage.warning('结束时间格式不正确或超出范围')
  }
}

// Get task alert type
const getTaskAlertType = (status: TrimTaskStatus): 'info' | 'warning' | 'success' | 'error' => {
  switch (status) {
    case 'pending':
      return 'info'
    case 'processing':
      return 'warning'
    case 'completed':
      return 'success'
    case 'failed':
      return 'error'
    default:
      return 'info'
  }
}

// Get task status text
const getTaskStatusText = (status: TrimTaskStatus): string => {
  switch (status) {
    case 'pending':
      return '任务等待中...'
    case 'processing':
      return '正在裁剪视频，请稍候...'
    case 'completed':
      return '裁剪完成！视频状态已重置为待审核，请重新审核后发布。'
    case 'failed':
      return '裁剪失败'
    default:
      return ''
  }
}

// Start polling task status
const startPolling = (taskId: number) => {
  if (pollingInterval.value) {
    clearInterval(pollingInterval.value)
  }

  pollingInterval.value = window.setInterval(async () => {
    try {
      const response = await videoTrimApi.getTrimTask(taskId)
      const task = response.data
      taskStatus.value = task.status
      taskError.value = task.error_message

      if (task.status === 'completed' || task.status === 'failed') {
        stopPolling()
        processing.value = false

        if (task.status === 'completed') {
          ElMessage.success('视频裁剪完成！')
          setTimeout(() => {
            emit('success')
            handleClose()
          }, 2000)
        } else {
          ElMessage.error('视频裁剪失败：' + (task.error_message || '未知错误'))
        }
      }
    } catch (error) {
      console.error('Failed to poll task status:', error)
    }
  }, 2000)
}

// Stop polling
const stopPolling = () => {
  if (pollingInterval.value) {
    clearInterval(pollingInterval.value)
    pollingInterval.value = null
  }
}

// Handle submit
const handleSubmit = async () => {
  if (!isValidRange.value) {
    ElMessage.warning('请选择有效的裁剪范围')
    return
  }

  try {
    processing.value = true
    taskStatus.value = null
    taskError.value = null

    const response = await videoTrimApi.trimVideo(props.videoId, {
      start_time: timeRange.value[0],
      end_time: timeRange.value[1],
      extract_audio: trimForm.value.extract_audio,
      keep_original: trimForm.value.keep_original
    })

    const task = response.data
    currentTaskId.value = task.id
    taskStatus.value = task.status

    ElMessage.success('裁剪任务已创建，正在处理...')
    startPolling(task.id)
  } catch (error: any) {
    processing.value = false
    const errorMsg = error.response?.data?.detail || '创建裁剪任务失败'
    ElMessage.error(errorMsg)
  }
}

// Handle close
const handleClose = () => {
  stopPolling()
  visible.value = false

  // Reset state
  nextTick(() => {
    taskStatus.value = null
    taskError.value = null
    currentTaskId.value = null
    processing.value = false
    trimForm.value = {
      extract_audio: false,
      keep_original: false
    }
  })
}

// Watch for dialog open
watch(visible, (newVal) => {
  if (newVal) {
    // Reset time range when dialog opens
    videoDuration.value = props.duration || 0
    timeRange.value = [0, videoDuration.value]
    updateTimeStrings()
  } else {
    stopPolling()
  }
})
</script>

<style scoped>
.trim-dialog-content {
  padding: 10px 0;
}

.video-preview-section {
  margin-bottom: 30px;
}

.video-preview-section h4 {
  margin-bottom: 10px;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.video-player {
  width: 100%;
  max-height: 400px;
  background: #000;
  border-radius: 4px;
}

.timeline-section {
  margin-bottom: 30px;
}

.timeline-section h4 {
  margin-bottom: 15px;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.timeline-slider {
  padding: 0 10px;
}

.timeline-labels {
  display: flex;
  justify-content: space-between;
  padding: 5px 10px 0;
  font-size: 12px;
  color: #909399;
}

.time-inputs-section {
  margin-bottom: 20px;
}

.task-status-section {
  margin-top: 20px;
}

.task-error {
  margin-top: 10px;
  padding: 10px;
  background: #fef0f0;
  border-radius: 4px;
}

:deep(.el-slider__runway) {
  height: 8px;
}

:deep(.el-slider__bar) {
  height: 8px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

:deep(.el-slider__button) {
  width: 16px;
  height: 16px;
  border: 2px solid #667eea;
}
</style>
