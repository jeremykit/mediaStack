<template>
  <div class="storage-card">
    <div class="card-header">
      <div class="header-icon">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M4 10V16C4 17.1046 4.89543 18 6 18H18C19.1046 18 20 17.1046 20 16V10M4 10L9 6H15L20 10M4 10L12 14L20 10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
      <div class="header-title">
        <h3>存储统计</h3>
      </div>
    </div>

    <div class="card-content">
      <!-- Total Stats -->
      <div class="total-stats">
        <div class="total-files">
          <div class="total-label">总文件数</div>
          <div class="total-value">{{ storage.total_files }}</div>
        </div>
        <div class="total-size">
          <div class="total-label">总存储</div>
          <div class="total-value">{{ formatSize(storage.total_size) }}</div>
        </div>
      </div>

      <!-- Category Breakdown -->
      <div class="category-section">
        <div class="section-title">分类统计</div>
        <div v-if="storage.by_category.length > 0" class="category-list">
          <div
            v-for="category in storage.by_category"
            :key="category.name"
            class="category-item"
          >
            <div class="category-info">
              <div class="category-name">{{ category.name }}</div>
              <div class="category-meta">
                <span>{{ category.count }} 个文件</span>
                <span>{{ formatSize(category.size) }}</span>
              </div>
            </div>
            <div class="category-progress">
              <div class="progress-bar">
                <div
                  class="progress-fill"
                  :style="{
                    width: `${getPercentage(category.size)}%`,
                    backgroundColor: getCategoryColor(category.name)
                  }"
                ></div>
              </div>
              <div class="percentage">{{ getPercentage(category.size) }}%</div>
            </div>
          </div>
        </div>
        <div v-else class="empty-state">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M4 10V16C4 17.1046 4.89543 18 6 18H18C19.1046 18 20 17.1046 20 16V10M4 10L9 6H15L20 10M4 10L12 14L20 10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <span>暂无存储数据</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface CategoryStorageInfo {
  name: string
  count: number
  size: number
}

interface Props {
  storage: {
    total_files: number
    total_size: number
    by_category: CategoryStorageInfo[]
  }
}

const props = defineProps<Props>()

// Format bytes to human readable size
const formatSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  const k = 1024
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  const value = bytes / Math.pow(k, i)
  return `${value.toFixed(i > 0 ? 1 : 0)} ${units[i]}`
}

// Get percentage of total storage
const getPercentage = (size: number): number => {
  if (props.storage.total_size === 0) return 0
  return Math.round((size / props.storage.total_size) * 100)
}

// Get color for category
const getCategoryColor = (name: string): string => {
  const colors: Record<string, string> = {
    '直播录制': '#E94560',
    '上传视频': '#8B5CF6',
    '其他': '#3B82F6',
    'default': '#22C55E'
  }
  return colors[name] || colors.default
}
</script>

<style scoped>
.storage-card {
  background: rgba(15, 20, 35, 0.6);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 20px;
  transition: all 0.3s ease;
}

.storage-card:hover {
  border-color: rgba(59, 130, 246, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(59, 130, 246, 0.15);
}

/* Card Header */
.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.header-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: rgba(59, 130, 246, 0.15);
  color: #3B82F6;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.header-icon svg {
  width: 20px;
  height: 20px;
}

.header-title {
  flex: 1;
}

.header-title h3 {
  font-size: 16px;
  font-weight: 600;
  color: #fff;
  margin: 0;
}

/* Card Content */
.card-content {
  min-height: 120px;
}

/* Total Stats */
.total-stats {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 10px;
}

.total-files,
.total-size {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.total-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

.total-value {
  font-size: 20px;
  font-weight: 700;
  color: #fff;
}

/* Category Section */
.category-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.section-title {
  font-size: 13px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.6);
}

.category-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.category-item {
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  transition: all 0.2s ease;
}

.category-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.category-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.category-name {
  font-size: 14px;
  font-weight: 500;
  color: #fff;
}

.category-meta {
  display: flex;
  gap: 8px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

.category-progress {
  display: flex;
  align-items: center;
  gap: 8px;
}

.progress-bar {
  flex: 1;
  height: 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.5s ease;
}

.percentage {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  min-width: 35px;
  text-align: right;
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 24px;
  gap: 8px;
  color: rgba(255, 255, 255, 0.3);
}

.empty-state svg {
  width: 32px;
  height: 32px;
}

.empty-state span {
  font-size: 13px;
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .storage-card {
    padding: 16px;
  }

  .header-icon {
    width: 36px;
    height: 36px;
  }

  .header-icon svg {
    width: 18px;
    height: 18px;
  }

  .header-title h3 {
    font-size: 14px;
  }

  .total-stats {
    flex-direction: column;
    gap: 12px;
    padding: 12px;
  }

  .total-value {
    font-size: 18px;
  }

  .category-item {
    padding: 8px 10px;
  }
}
</style>
