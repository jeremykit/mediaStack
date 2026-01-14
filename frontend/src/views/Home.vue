<template>
  <div class="home-page">
    <div class="header">
      <h1>MediaStack</h1>
      <el-input v-model="search" placeholder="搜索视频..." style="width: 300px" @keyup.enter="loadVideos" clearable />
    </div>
    <div class="video-grid" v-loading="loading">
      <VideoCard v-for="video in videos" :key="video.id" :video="video" @click="goToVideo(video.id)" />
    </div>
    <div v-if="!loading && videos.length === 0" class="empty">暂无视频</div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { videosApi, type Video } from '../api/videos'
import VideoCard from '../components/VideoCard.vue'

const router = useRouter()
const videos = ref<Video[]>([])
const loading = ref(false)
const search = ref('')

const loadVideos = async () => {
  loading.value = true
  try {
    const { data } = await videosApi.list({ search: search.value || undefined })
    videos.value = data
  } catch (e) {
    console.error('Failed to load videos', e)
  } finally {
    loading.value = false
  }
}

const goToVideo = (id: number) => router.push(`/video/${id}`)

onMounted(loadVideos)
</script>

<style scoped>
.home-page { max-width: 1200px; margin: 0 auto; padding: 20px; }
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.header h1 { margin: 0; }
.video-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; }
.empty { text-align: center; padding: 60px; color: #909399; }
</style>
