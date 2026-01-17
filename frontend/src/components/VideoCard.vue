<template>
  <div class="video-card" @click="$emit('click')">
    <div class="thumbnail-wrapper">
      <div class="thumbnail">
        <img v-if="video.thumbnail" :src="video.thumbnail" :alt="video.title" />
        <div v-else class="placeholder">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="10" fill="url(#play-gradient)" />
            <path d="M10 8L16 12L10 16V8Z" fill="white" />
            <defs>
              <linearGradient id="play-gradient" x1="2" y1="2" x2="22" y2="22" gradientUnits="userSpaceOnUse">
                <stop stop-color="#FF6B9D" />
                <stop offset="1" stop-color="#FFA06B" />
              </linearGradient>
            </defs>
          </svg>
        </div>
        <div class="duration-badge">{{ formatDuration(video.duration) }}</div>
      </div>
    </div>
    <div class="card-content">
      <h4 class="video-title" :title="video.title">{{ video.title }}</h4>
      <div class="video-meta">
        <span class="meta-item">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M15 12C15 13.6569 13.6569 15 12 15C10.3431 15 9 13.6569 9 12C9 10.3431 10.3431 9 12 9C13.6569 9 15 10.3431 15 12Z" stroke="currentColor" stroke-width="2" />
            <path d="M2 12C2 12 5 5 12 5C19 5 22 12 22 12C22 12 19 19 12 19C5 19 2 12 2 12Z" stroke="currentColor" stroke-width="2" />
          </svg>
          {{ video.view_count }} 次观看
        </span>
        <span class="meta-item">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="3" y="6" width="18" height="15" rx="2" stroke="currentColor" stroke-width="2" />
            <path d="M3 10H21M8 3V6M16 3V6" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
          </svg>
          {{ formatDate(video.created_at) }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
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
.video-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
}

.video-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 32px rgba(255, 107, 157, 0.2);
}

.thumbnail-wrapper {
  position: relative;
  overflow: hidden;
}

.thumbnail {
  position: relative;
  aspect-ratio: 16/9;
  background: linear-gradient(135deg, #FFF5F7 0%, #FFE0E8 100%);
  overflow: hidden;
}

.thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.video-card:hover .thumbnail img {
  transform: scale(1.05);
}

.placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.placeholder svg {
  width: 64px;
  height: 64px;
  opacity: 0.8;
}

.duration-badge {
  position: absolute;
  bottom: 12px;
  right: 12px;
  background: rgba(0, 0, 0, 0.75);
  backdrop-filter: blur(8px);
  color: white;
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  font-family: var(--font-mono);
}

.card-content {
  padding: 16px;
}

.video-title {
  margin: 0 0 12px;
  font-size: 16px;
  font-weight: 600;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  line-height: 1.5;
  min-height: 48px;
}

.video-meta {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #999;
}

.meta-item svg {
  width: 16px;
  height: 16px;
  color: #FFB8C6;
  flex-shrink: 0;
}
</style>
