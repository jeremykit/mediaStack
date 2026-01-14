<template>
  <el-card class="video-card" shadow="hover" @click="$emit('click')">
    <div class="thumbnail">
      <img v-if="video.thumbnail" :src="video.thumbnail" :alt="video.title" />
      <div v-else class="placeholder">
        <el-icon :size="48"><VideoPlay /></el-icon>
      </div>
      <span class="duration">{{ formatDuration(video.duration) }}</span>
    </div>
    <div class="info">
      <h4 class="title" :title="video.title">{{ video.title }}</h4>
      <div class="meta">
        <span>{{ video.view_count }} 次观看</span>
        <span>{{ formatDate(video.created_at) }}</span>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { VideoPlay } from '@element-plus/icons-vue'
import type { Video } from '../api/videos'

defineProps<{ video: Video }>()
defineEmits<{ click: [] }>()

const formatDuration = (seconds: number | null) => {
  if (!seconds) return '--:--'
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = seconds % 60
  if (h > 0) return `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
  return `${m}:${s.toString().padStart(2, '0')}`
}

const formatDate = (date: string) => new Date(date).toLocaleDateString('zh-CN')
</script>

<style scoped>
.video-card { cursor: pointer; transition: transform 0.2s; }
.video-card:hover { transform: translateY(-4px); }
.thumbnail { position: relative; aspect-ratio: 16/9; background: #000; border-radius: 4px; overflow: hidden; }
.thumbnail img { width: 100%; height: 100%; object-fit: cover; }
.placeholder { display: flex; align-items: center; justify-content: center; height: 100%; color: #666; }
.duration { position: absolute; bottom: 8px; right: 8px; background: rgba(0,0,0,0.8); color: #fff; padding: 2px 6px; border-radius: 4px; font-size: 12px; }
.info { padding: 12px 0 0; }
.title { margin: 0 0 8px; font-size: 14px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.meta { display: flex; justify-content: space-between; font-size: 12px; color: #909399; }
</style>
