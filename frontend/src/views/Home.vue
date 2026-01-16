<template>
  <div class="home-page">
    <div class="header">
      <h1>MediaStack</h1>
      <el-input v-model="search" placeholder="搜索视频..." style="width: 300px" @keyup.enter="loadVideos" clearable />
    </div>

    <!-- Filters -->
    <div class="filters">
      <div class="filter-group">
        <span class="filter-label">分类：</span>
        <el-radio-group v-model="selectedCategory" @change="loadVideos">
          <el-radio-button :value="null">全部</el-radio-button>
          <el-radio-button
            v-for="cat in categories"
            :key="cat.id"
            :value="cat.id"
          >
            {{ cat.name }}
          </el-radio-button>
        </el-radio-group>
      </div>
      <div class="filter-group" v-if="tags.length > 0">
        <span class="filter-label">标签：</span>
        <el-checkbox-group v-model="selectedTags" @change="loadVideos">
          <el-checkbox-button
            v-for="tag in tags"
            :key="tag.id"
            :value="tag.id"
          >
            {{ tag.name }}
          </el-checkbox-button>
        </el-checkbox-group>
      </div>
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
import { categoriesApi, type Category } from '../api/categories'
import { tagsApi, type Tag } from '../api/tags'
import VideoCard from '../components/VideoCard.vue'

const router = useRouter()
const videos = ref<Video[]>([])
const categories = ref<Category[]>([])
const tags = ref<Tag[]>([])
const loading = ref(false)
const search = ref('')
const selectedCategory = ref<number | null>(null)
const selectedTags = ref<number[]>([])

const loadVideos = async () => {
  loading.value = true
  try {
    const params: any = {}
    if (search.value) params.search = search.value
    if (selectedCategory.value) params.category_id = selectedCategory.value
    if (selectedTags.value.length > 0) params.tag_ids = selectedTags.value.join(',')

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
.home-page { max-width: 1200px; margin: 0 auto; padding: 20px; }
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.header h1 { margin: 0; }
.filters { margin-bottom: 24px; }
.filter-group { margin-bottom: 12px; display: flex; align-items: center; flex-wrap: wrap; gap: 8px; }
.filter-label { color: #606266; font-size: 14px; min-width: 50px; }
.video-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; }
.empty { text-align: center; padding: 60px; color: #909399; }
</style>
