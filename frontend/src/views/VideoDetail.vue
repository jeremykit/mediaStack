<template>
  <div class="video-detail" v-loading="loading">
    <div class="player-section" v-if="video">
      <VideoPlayer :src="playUrl" />
    </div>
    <div class="info-section" v-if="video">
      <h1>{{ video.title }}</h1>
      <div class="meta">
        <span>{{ video.view_count }} 次观看</span>
        <span>{{ formatDate(video.created_at) }}</span>
        <span>{{ formatDuration(video.duration) }}</span>
        <span>{{ formatSize(video.file_size) }}</span>
      </div>
    </div>
    <el-button @click="$router.back()" style="margin-top: 20px">返回</el-button>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { videosApi, type Video } from '../api/videos'
import VideoPlayer from '../components/VideoPlayer.vue'

const route = useRoute()
const video = ref<Video | null>(null)
const playUrl = ref('')
const loading = ref(false)

const loadVideo = async () => {
  const id = Number(route.params.id)
  loading.value = true
  try {
    const [videoRes, playRes] = await Promise.all([videosApi.get(id), videosApi.getPlayUrl(id)])
    video.value = videoRes.data
    playUrl.value = playRes.data.hls_url
    videosApi.incrementView(id)
  } catch (e) {
    console.error('Failed to load video', e)
  } finally {
    loading.value = false
  }
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

onMounted(loadVideo)
</script>

<style scoped>
.video-detail { max-width: 1000px; margin: 0 auto; padding: 20px; }
.player-section { margin-bottom: 20px; }
.info-section h1 { margin: 0 0 12px; font-size: 24px; }
.meta { display: flex; gap: 20px; color: #909399; }
</style>
