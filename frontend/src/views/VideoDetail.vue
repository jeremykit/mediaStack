<template>
  <div class="video-detail" v-loading="loading">
    <!-- Player Section -->
    <div class="player-section" v-if="video">
      <!-- Video/Audio Mode Toggle -->
      <div class="player-mode-toggle" v-if="audioInfo?.has_audio">
        <el-radio-group v-model="playMode" size="small">
          <el-radio-button value="video">视频模式</el-radio-button>
          <el-radio-button value="audio">音频模式</el-radio-button>
        </el-radio-group>
      </div>

      <!-- Video Player -->
      <div v-show="playMode === 'video'">
        <VideoPlayer :src="playUrl" />
      </div>

      <!-- Audio Player -->
      <div v-show="playMode === 'audio'" class="audio-player-container">
        <!-- Use WaveformPlayer for pure audio files -->
        <WaveformPlayer
          v-if="video.file_type === 'audio'"
          :audio-url="audioDownloadUrl"
          :cover="video.thumbnail"
        />
        <!-- Use simple HTML5 audio player for video files in audio mode -->
        <template v-else>
          <div class="audio-cover" v-if="video.thumbnail">
            <img :src="video.thumbnail" alt="封面" />
          </div>
          <div class="audio-cover audio-cover-placeholder" v-else>
            <el-icon :size="64"><Headset /></el-icon>
          </div>
          <audio
            ref="audioRef"
            :src="audioDownloadUrl"
            controls
            class="audio-player"
          ></audio>
        </template>
      </div>
    </div>

    <!-- Info Section -->
    <div class="info-section" v-if="video">
      <h1>{{ video.title }}</h1>
      <div class="meta">
        <span>{{ video.view_count }} 次观看</span>
        <span>{{ formatDate(video.created_at) }}</span>
        <span>{{ formatDuration(video.duration) }}</span>
        <span>{{ formatSize(video.file_size) }}</span>
      </div>

      <!-- Description -->
      <div class="description" v-if="video.description">
        <p>{{ video.description }}</p>
      </div>

      <!-- Audio Download -->
      <div class="audio-actions" v-if="audioInfo">
        <template v-if="audioInfo.has_audio">
          <el-button
            type="primary"
            :icon="Download"
            @click="handleDownloadAudio"
          >
            下载音频 {{ audioInfo.file_size ? `(${formatSize(audioInfo.file_size)})` : '' }}
          </el-button>
        </template>
        <template v-else-if="audioInfo.task">
          <el-tag v-if="audioInfo.task.status === 'pending'" type="info">
            音频提取等待中...
          </el-tag>
          <el-tag v-else-if="audioInfo.task.status === 'processing'" type="warning">
            音频提取中...
          </el-tag>
          <el-tag v-else-if="audioInfo.task.status === 'failed'" type="danger">
            音频提取失败
          </el-tag>
        </template>
      </div>

      <!-- Category and Tags -->
      <div class="tags-section" v-if="video.category || video.tags?.length">
        <el-tag v-if="video.category" type="primary" class="category-tag">
          {{ video.category.name }}
        </el-tag>
        <el-tag
          v-for="tag in video.tags"
          :key="tag.id"
          type="info"
          class="video-tag"
        >
          {{ tag.name }}
        </el-tag>
      </div>
    </div>

    <!-- Extensions Section -->
    <div class="extensions-section" v-if="video">
      <!-- Images Carousel -->
      <div class="extension-block" v-if="images.length > 0">
        <h3>相关图片</h3>
        <el-carousel
          :interval="5000"
          type="card"
          height="200px"
          v-if="images.length > 1"
        >
          <el-carousel-item v-for="image in images" :key="image.id">
            <el-image
              :src="image.image_url"
              fit="cover"
              :preview-src-list="images.map(i => i.image_url)"
              :initial-index="images.findIndex(i => i.id === image.id)"
              class="carousel-image"
            />
          </el-carousel-item>
        </el-carousel>
        <div v-else class="single-image">
          <el-image
            :src="images[0].image_url"
            fit="contain"
            :preview-src-list="[images[0].image_url]"
            class="single-image-display"
          />
        </div>
      </div>

      <!-- Texts -->
      <div class="extension-block" v-if="texts.length > 0">
        <h3>相关内容</h3>
        <el-collapse>
          <el-collapse-item
            v-for="text in texts"
            :key="text.id"
            :title="text.title"
            :name="text.id"
          >
            <div class="text-content">{{ text.content }}</div>
          </el-collapse-item>
        </el-collapse>
      </div>

      <!-- Links -->
      <div class="extension-block" v-if="links.length > 0">
        <h3>相关链接</h3>
        <div class="links-list">
          <div v-for="link in links" :key="link.id" class="link-item">
            <el-link :href="link.url" target="_blank" type="primary">
              {{ link.title }}
            </el-link>
          </div>
        </div>
      </div>
    </div>

    <el-button @click="$router.back()" style="margin-top: 20px">返回</el-button>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { Download, Headset } from '@element-plus/icons-vue'
import { videosApi, type Video } from '../api/videos'
import { audioApi, type AudioInfo } from '../api/audio'
import {
  videoExtensionsApi,
  type VideoImage,
  type VideoText,
  type VideoLink
} from '../api/videoExtensions'
import VideoPlayer from '../components/VideoPlayer.vue'
import WaveformPlayer from '../components/WaveformPlayer.vue'

const route = useRoute()
const video = ref<Video | null>(null)
const playUrl = ref('')
const loading = ref(false)

// Audio state
const audioInfo = ref<AudioInfo | null>(null)
const playMode = ref<'video' | 'audio'>('video')
const audioRef = ref<HTMLAudioElement>()

// Extensions state
const images = ref<VideoImage[]>([])
const texts = ref<VideoText[]>([])
const links = ref<VideoLink[]>([])

const audioDownloadUrl = computed(() => {
  if (!video.value) return ''
  return audioApi.getDownloadUrl(video.value.id)
})

const loadVideo = async () => {
  const id = Number(route.params.id)
  if (isNaN(id)) {
    console.error('Invalid video ID')
    return
  }

  loading.value = true
  try {
    const videoRes = await videosApi.get(id)
    video.value = videoRes.data

    const playRes = await videosApi.getPlayUrl(id)
    playUrl.value = playRes.data.hls_url

    videosApi.incrementView(id).catch(() => {})

    // Load audio info
    loadAudioInfo(id)

    // Load extensions
    loadExtensions(id)
  } catch (e) {
    console.error('Failed to load video', e)
  } finally {
    loading.value = false
  }
}

const loadAudioInfo = async (videoId: number) => {
  try {
    const res = await audioApi.getAudioInfo(videoId)
    audioInfo.value = res.data

    // If audio is being processed, poll for updates
    if (audioInfo.value?.task?.status === 'pending' || audioInfo.value?.task?.status === 'processing') {
      setTimeout(() => loadAudioInfo(videoId), 3000)
    }
  } catch (e) {
    console.error('Failed to load audio info', e)
  }
}

const loadExtensions = async (videoId: number) => {
  try {
    const [imagesRes, textsRes, linksRes] = await Promise.all([
      videoExtensionsApi.listImages(videoId),
      videoExtensionsApi.listTexts(videoId),
      videoExtensionsApi.listLinks(videoId)
    ])
    images.value = imagesRes.data
    texts.value = textsRes.data
    links.value = linksRes.data
  } catch (e) {
    console.error('Failed to load extensions', e)
  }
}

const handleDownloadAudio = () => {
  if (!video.value) return
  window.open(audioDownloadUrl.value, '_blank')
}

const formatDate = (date: string) => new Date(date).toLocaleString('zh-CN')
const formatDuration = (seconds: number | null) => {
  if (!seconds) return ''
  const h = Math.floor(seconds / 3600), m = Math.floor((seconds % 3600) / 60), s = seconds % 60
  return h > 0 ? `${h}小时${m}分${s}秒` : `${m}分${s}秒`
}
const formatSize = (bytes: number | null) => {
  if (!bytes) return ''
  const units = ['B', 'KB', 'MB', 'GB']
  let i = 0, size = bytes
  while (size >= 1024 && i < 3) { size /= 1024; i++ }
  return `${size.toFixed(1)} ${units[i]}`
}

// Watch for play mode changes
watch(playMode, (mode) => {
  if (mode === 'audio' && audioRef.value) {
    // Optionally auto-play audio when switching to audio mode
  }
})

onMounted(loadVideo)
</script>

<style scoped>
.video-detail {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

.player-section {
  margin-bottom: 20px;
}

.player-mode-toggle {
  margin-bottom: 12px;
  text-align: center;
}

.audio-player-container {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  padding: 40px 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.audio-cover {
  width: 200px;
  height: 200px;
  border-radius: 50%;
  overflow: hidden;
  margin-bottom: 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.audio-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.audio-cover-placeholder {
  background: rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(255, 255, 255, 0.8);
}

.audio-player {
  width: 100%;
  max-width: 400px;
}

.info-section h1 {
  margin: 0 0 12px;
  font-size: 24px;
}

.meta {
  display: flex;
  gap: 20px;
  color: #909399;
  margin-bottom: 16px;
}

.description {
  margin-bottom: 16px;
  color: #606266;
  line-height: 1.6;
}

.description p {
  margin: 0;
  white-space: pre-wrap;
}

.audio-actions {
  margin-bottom: 16px;
}

.tags-section {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}

.category-tag {
  font-weight: 500;
}

/* Extensions Section */
.extensions-section {
  margin-top: 32px;
  border-top: 1px solid #ebeef5;
  padding-top: 24px;
}

.extension-block {
  margin-bottom: 24px;
}

.extension-block h3 {
  margin: 0 0 16px;
  font-size: 18px;
  color: #303133;
}

.carousel-image {
  width: 100%;
  height: 100%;
  cursor: pointer;
}

.single-image {
  text-align: center;
}

.single-image-display {
  max-width: 100%;
  max-height: 400px;
}

.text-content {
  white-space: pre-wrap;
  color: #606266;
  line-height: 1.6;
}

.links-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.link-item {
  padding: 8px 0;
}

.link-item:not(:last-child) {
  border-bottom: 1px solid #ebeef5;
}
</style>
