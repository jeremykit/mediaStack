<template>
  <div class="home-page">
    <!-- Hero Section -->
    <div class="hero-section">
      <div class="hero-content">
        <div class="brand-area">
          <div class="logo-circle">
            <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="24" cy="24" r="20" fill="url(#hero-gradient)" />
              <path d="M20 16L30 24L20 32V16Z" fill="white" />
              <defs>
                <linearGradient id="hero-gradient" x1="4" y1="4" x2="44" y2="44" gradientUnits="userSpaceOnUse">
                  <stop stop-color="#FF6B9D" />
                  <stop offset="1" stop-color="#FFA06B" />
                </linearGradient>
              </defs>
            </svg>
          </div>
          <div class="brand-text">
            <h1 class="brand-title">MediaStack</h1>
            <p class="brand-subtitle">发现精彩视频内容</p>
          </div>
        </div>

        <div class="search-area">
          <div class="search-box">
            <svg class="search-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="11" cy="11" r="7" stroke="currentColor" stroke-width="2" />
              <path d="M16 16L21 21" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
            </svg>
            <input
              v-model="search"
              type="text"
              placeholder="搜索你感兴趣的视频..."
              @keyup.enter="loadVideos"
              class="search-input"
            />
            <button v-if="search" @click="search = ''; loadVideos()" class="clear-btn">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      <div class="hero-decoration">
        <div class="float-circle circle-1"></div>
        <div class="float-circle circle-2"></div>
        <div class="float-circle circle-3"></div>
      </div>
    </div>

    <!-- Filters Section -->
    <div class="filters-section">
      <div class="filter-container">
        <div class="filter-group" v-if="categories.length > 0">
          <div class="filter-header">
            <svg class="filter-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect x="3" y="3" width="7" height="7" rx="2" stroke="currentColor" stroke-width="2" />
              <rect x="14" y="3" width="7" height="7" rx="2" stroke="currentColor" stroke-width="2" />
              <rect x="3" y="14" width="7" height="7" rx="2" stroke="currentColor" stroke-width="2" />
              <rect x="14" y="14" width="7" height="7" rx="2" stroke="currentColor" stroke-width="2" />
            </svg>
            <span class="filter-label">分类</span>
          </div>
          <div class="filter-options">
            <button
              class="filter-chip"
              :class="{ active: selectedCategory === null }"
              @click="selectedCategory = null; loadVideos()"
            >
              全部
            </button>
            <button
              v-for="cat in categories"
              :key="cat.id"
              class="filter-chip"
              :class="{ active: selectedCategory === cat.id }"
              @click="selectedCategory = cat.id; loadVideos()"
            >
              {{ cat.name }}
            </button>
          </div>
        </div>

        <div class="filter-group" v-if="tags.length > 0">
          <div class="filter-header">
            <svg class="filter-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M3 10.5V5C3 3.89543 3.89543 3 5 3H10.5L21 13.5L13.5 21L3 10.5Z" stroke="currentColor" stroke-width="2" />
              <circle cx="8" cy="8" r="1.5" fill="currentColor" />
            </svg>
            <span class="filter-label">标签</span>
          </div>
          <div class="filter-options">
            <button
              v-for="tag in tags"
              :key="tag.id"
              class="filter-chip tag-chip"
              :class="{ active: selectedTags.includes(tag.id) }"
              @click="toggleTag(tag.id)"
            >
              {{ tag.name }}
            </button>
          </div>
        </div>

        <div class="filter-group" v-if="authStore.isLoggedIn">
          <div class="filter-header">
            <svg class="filter-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span class="filter-label">审核状态</span>
          </div>
          <div class="filter-options">
            <button
              class="filter-chip"
              :class="{ active: selectedStatus === null }"
              @click="selectedStatus = null; loadVideos()"
            >
              全部
            </button>
            <button
              class="filter-chip"
              :class="{ active: selectedStatus === 'published' }"
              @click="selectedStatus = 'published'; loadVideos()"
            >
              已发布
            </button>
            <button
              class="filter-chip"
              :class="{ active: selectedStatus === 'pending' }"
              @click="selectedStatus = 'pending'; loadVideos()"
            >
              待审核
            </button>
            <button
              class="filter-chip"
              :class="{ active: selectedStatus === 'offline' }"
              @click="selectedStatus = 'offline'; loadVideos()"
            >
              已下架
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Videos Grid -->
    <div class="content-section">
      <div class="section-header" v-if="videos.length > 0">
        <h2 class="section-title">
          {{ selectedCategory || selectedTags.length > 0 ? '筛选结果' : '全部视频' }}
        </h2>
        <span class="video-count">{{ videos.length }} 个视频</span>
      </div>

      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>加载中...</p>
      </div>

      <div v-else-if="videos.length === 0" class="empty-state">
        <svg class="empty-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect x="2" y="6" width="14" height="12" rx="2" stroke="currentColor" stroke-width="2" />
          <path d="M16 10L22 7V17L16 14V10Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round" />
        </svg>
        <h3>暂无视频</h3>
        <p>{{ search ? '试试其他搜索词' : '还没有上传任何视频' }}</p>
      </div>

      <div v-else class="video-grid">
        <VideoCard
          v-for="video in videos"
          :key="video.id"
          :video="video"
          @click="goToVideo(video.id)"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { videosApi, type Video, type VideoStatus } from '../api/videos'
import { categoriesApi, type Category } from '../api/categories'
import { tagsApi, type Tag } from '../api/tags'
import { useAuthStore } from '../stores/auth'
import VideoCard from '../components/VideoCard.vue'

const router = useRouter()
const authStore = useAuthStore()
const videos = ref<Video[]>([])
const categories = ref<Category[]>([])
const tags = ref<Tag[]>([])
const loading = ref(false)
const search = ref('')
const selectedCategory = ref<number | null>(null)
const selectedTags = ref<number[]>([])
const selectedStatus = ref<VideoStatus | null>(null)

const toggleTag = (tagId: number) => {
  const index = selectedTags.value.indexOf(tagId)
  if (index > -1) {
    selectedTags.value.splice(index, 1)
  } else {
    selectedTags.value.push(tagId)
  }
  loadVideos()
}

const loadVideos = async () => {
  loading.value = true
  try {
    const params: any = {}
    if (search.value) params.search = search.value
    if (selectedCategory.value) params.category_id = selectedCategory.value
    if (selectedTags.value.length > 0) params.tag_ids = selectedTags.value.join(',')
    // Only send status parameter if user is logged in
    if (authStore.isLoggedIn && selectedStatus.value) {
      params.status = selectedStatus.value
    }

    const { data } = await videosApi.list(params)
    videos.value = data
  } catch (e) {
    console.error('Failed to load videos', e)
  } finally {
    loading.value = false
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

const goToVideo = (id: number) => router.push(`/video/${id}`)

onMounted(() => {
  loadCategories()
  loadTags()
  loadVideos()
})
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.home-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #FFF5F7 0%, #FFF9E6 50%, #F0F9FF 100%);
  /* 使用系统字体，无需加载外部资源 */
  font-family: var(--font-home);
}

/* Hero Section */
.hero-section {
  position: relative;
  padding: 60px 20px 80px;
  overflow: hidden;
}

.hero-content {
  max-width: 1200px;
  margin: 0 auto;
  position: relative;
  z-index: 2;
}

.brand-area {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 40px;
  justify-content: center;
}

.logo-circle {
  width: 80px;
  height: 80px;
  animation: float 3s ease-in-out infinite;
}

.logo-circle svg {
  width: 100%;
  height: 100%;
  filter: drop-shadow(0 8px 24px rgba(255, 107, 157, 0.3));
}

@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
}

.brand-text {
  text-align: left;
}

.brand-title {
  font-size: 48px;
  font-weight: 700;
  font-family: var(--font-sans);
  background: linear-gradient(135deg, #FF6B9D 0%, #FFA06B 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0;
  line-height: 1.2;
}

.brand-subtitle {
  font-size: 18px;
  color: #FF8BA7;
  margin: 8px 0 0;
  font-weight: 500;
}

.search-area {
  max-width: 700px;
  margin: 0 auto;
}

.search-box {
  position: relative;
  display: flex;
  align-items: center;
  background: white;
  border-radius: 50px;
  padding: 16px 24px;
  box-shadow: 0 8px 32px rgba(255, 107, 157, 0.15);
  transition: all 0.3s ease;
}

.search-box:focus-within {
  box-shadow: 0 12px 48px rgba(255, 107, 157, 0.25);
  transform: translateY(-2px);
}

.search-icon {
  width: 24px;
  height: 24px;
  color: #FF8BA7;
  flex-shrink: 0;
}

.search-input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 16px;
  margin-left: 16px;
  color: #333;
  font-family: var(--font-sans);
}

.search-input::placeholder {
  color: #FFB8C6;
}

.clear-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: #FFF0F3;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.clear-btn svg {
  width: 16px;
  height: 16px;
  color: #FF6B9D;
}

.clear-btn:hover {
  background: #FFE0E8;
  transform: rotate(90deg);
}

/* Hero Decoration */
.hero-decoration {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 1;
}

.float-circle {
  position: absolute;
  border-radius: 50%;
  opacity: 0.6;
  animation: floatCircle 20s ease-in-out infinite;
}

.circle-1 {
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, rgba(255, 107, 157, 0.2) 0%, transparent 70%);
  top: -100px;
  right: 10%;
  animation-delay: 0s;
}

.circle-2 {
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(255, 160, 107, 0.2) 0%, transparent 70%);
  bottom: 20%;
  left: 5%;
  animation-delay: -7s;
}

.circle-3 {
  width: 150px;
  height: 150px;
  background: radial-gradient(circle, rgba(99, 179, 237, 0.2) 0%, transparent 70%);
  top: 40%;
  right: 5%;
  animation-delay: -14s;
}

@keyframes floatCircle {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(30px, -30px) scale(1.1); }
  66% { transform: translate(-20px, 20px) scale(0.9); }
}

/* Filters Section */
.filters-section {
  background: white;
  border-radius: 32px 32px 0 0;
  padding: 32px 20px 24px;
  margin-top: -40px;
  position: relative;
  z-index: 3;
  box-shadow: 0 -4px 24px rgba(0, 0, 0, 0.05);
}

.filter-container {
  max-width: 1200px;
  margin: 0 auto;
}

.filter-group {
  margin-bottom: 24px;
}

.filter-group:last-child {
  margin-bottom: 0;
}

.filter-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.filter-icon {
  width: 20px;
  height: 20px;
  color: #FF8BA7;
}

.filter-label {
  font-size: 15px;
  font-weight: 600;
  color: #333;
}

.filter-options {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.filter-chip {
  padding: 10px 20px;
  border: 2px solid #FFE0E8;
  background: white;
  border-radius: 50px;
  font-size: 14px;
  font-weight: 500;
  color: #666;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: var(--font-sans);
}

.filter-chip:hover {
  border-color: #FFB8C6;
  background: #FFF5F7;
  transform: translateY(-2px);
}

.filter-chip.active {
  background: linear-gradient(135deg, #FF6B9D 0%, #FFA06B 100%);
  border-color: transparent;
  color: white;
  box-shadow: 0 4px 16px rgba(255, 107, 157, 0.3);
}

.tag-chip {
  border-color: #E0F2FE;
}

.tag-chip:hover {
  border-color: #BAE6FD;
  background: #F0F9FF;
}

.tag-chip.active {
  background: linear-gradient(135deg, #63B3ED 0%, #4299E1 100%);
  border-color: transparent;
  color: white;
  box-shadow: 0 4px 16px rgba(99, 179, 237, 0.3);
}

/* Content Section */
.content-section {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px 60px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.section-title {
  font-size: 28px;
  font-weight: 700;
  color: #333;
  margin: 0;
}

.video-count {
  font-size: 14px;
  color: #999;
  background: #F5F5F5;
  padding: 6px 16px;
  border-radius: 20px;
}

/* Loading State */
.loading-state {
  text-align: center;
  padding: 80px 20px;
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid #FFE0E8;
  border-top-color: #FF6B9D;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-state p {
  color: #999;
  font-size: 16px;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 80px 20px;
}

.empty-icon {
  width: 80px;
  height: 80px;
  color: #FFB8C6;
  margin: 0 auto 24px;
}

.empty-state h3 {
  font-size: 24px;
  color: #333;
  margin: 0 0 12px;
}

.empty-state p {
  font-size: 16px;
  color: #999;
}

/* Video Grid */
.video-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 24px;
}

/* Responsive */
@media (max-width: 768px) {
  .brand-title {
    font-size: 36px;
  }

  .brand-subtitle {
    font-size: 16px;
  }

  .search-box {
    padding: 12px 20px;
  }

  .section-title {
    font-size: 24px;
  }

  .video-grid {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 16px;
  }
}
</style>
