<template>
  <div class="system-resource-card">
    <div class="card-header">
      <div class="header-icon">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect x="3" y="3" width="8" height="8" rx="1" stroke="currentColor" stroke-width="2"/>
          <rect x="13" y="3" width="8" height="8" rx="1" stroke="currentColor" stroke-width="2"/>
          <rect x="3" y="13" width="8" height="8" rx="1" stroke="currentColor" stroke-width="2"/>
          <rect x="13" y="13" width="8" height="8" rx="1" stroke="currentColor" stroke-width="2"/>
        </svg>
      </div>
      <div class="header-title">
        <h3>系统资源</h3>
      </div>
    </div>

    <div class="card-content">
      <div class="resource-list">
        <!-- CPU -->
        <div class="resource-item">
          <div class="resource-icon" :class="getStatusClass(system.cpu_percent)">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M4 6H8M10 6H14M16 6H20M4 12H8M10 12H14M16 12H20M4 18H8M10 18H14M16 18H20" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </div>
          <div class="resource-info">
            <div class="resource-label">CPU</div>
            <div class="resource-value" :class="getStatusClass(system.cpu_percent)">
              {{ system.cpu_percent }}%
            </div>
          </div>
          <div class="resource-progress">
            <div class="progress-bar">
              <div
                class="progress-fill"
                :class="getStatusClass(system.cpu_percent)"
                :style="{ width: `${system.cpu_percent}%` }"
              ></div>
            </div>
          </div>
        </div>

        <!-- Memory -->
        <div class="resource-item">
          <div class="resource-icon" :class="getStatusClass(system.memory_percent)">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M4 8V16C4 17.1046 4.89543 18 6 18H18C19.1046 18 20 17.1046 20 16V8M4 8L9 4H15L20 8M4 8L12 12L20 8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="resource-info">
            <div class="resource-label">内存</div>
            <div class="resource-value" :class="getStatusClass(system.memory_percent)">
              {{ system.memory_percent }}%
            </div>
          </div>
          <div class="resource-progress">
            <div class="progress-bar">
              <div
                class="progress-fill"
                :class="getStatusClass(system.memory_percent)"
                :style="{ width: `${system.memory_percent}%` }"
              ></div>
            </div>
          </div>
        </div>

        <!-- Disk -->
        <div class="resource-item">
          <div class="resource-icon" :class="getStatusClass(system.disk_percent)">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="12" cy="12" r="8" stroke="currentColor" stroke-width="2"/>
              <path d="M12 4V12L16 16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </div>
          <div class="resource-info">
            <div class="resource-label">磁盘</div>
            <div class="resource-value" :class="getStatusClass(system.disk_percent)">
              {{ system.disk_percent }}%
            </div>
          </div>
          <div class="resource-progress">
            <div class="progress-bar">
              <div
                class="progress-fill"
                :class="getStatusClass(system.disk_percent)"
                :style="{ width: `${system.disk_percent}%` }"
              ></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  system: {
    cpu_percent: number
    memory_percent: number
    disk_percent: number
  }
}

const props = defineProps<Props>()

const getStatusClass = (percent: number): string => {
  if (percent >= 90) return 'danger'
  if (percent >= 70) return 'warning'
  return 'success'
}
</script>

<style scoped>
.system-resource-card {
  background: rgba(15, 20, 35, 0.6);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 20px;
  transition: all 0.3s ease;
}

.system-resource-card:hover {
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

/* Resource List */
.resource-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.resource-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  transition: all 0.2s ease;
}

.resource-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.resource-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.resource-icon svg {
  width: 16px;
  height: 16px;
}

.resource-icon.success {
  background: rgba(34, 197, 94, 0.15);
  color: #22C55E;
}

.resource-icon.warning {
  background: rgba(251, 146, 60, 0.15);
  color: #FB923C;
}

.resource-icon.danger {
  background: rgba(239, 68, 68, 0.15);
  color: #EF4444;
}

.resource-info {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.resource-label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
  font-weight: 500;
}

.resource-value {
  font-size: 16px;
  font-weight: 600;
  color: #fff;
}

.resource-value.success {
  color: #22C55E;
}

.resource-value.warning {
  color: #FB923C;
}

.resource-value.danger {
  color: #EF4444;
}

.resource-progress {
  width: 80px;
  flex-shrink: 0;
}

.progress-bar {
  width: 100%;
  height: 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.5s ease, background-color 0.3s ease;
}

.progress-fill.success {
  background: linear-gradient(90deg, #22C55E 0%, #16A34A 100%);
}

.progress-fill.warning {
  background: linear-gradient(90deg, #FB923C 0%, #F97316 100%);
}

.progress-fill.danger {
  background: linear-gradient(90deg, #EF4444 0%, #DC2626 100%);
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .system-resource-card {
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

  .resource-item {
    padding: 8px 10px;
  }

  .resource-icon {
    width: 28px;
    height: 28px;
  }

  .resource-icon svg {
    width: 14px;
    height: 14px;
  }

  .resource-label {
    font-size: 12px;
  }

  .resource-value {
    font-size: 14px;
  }

  .resource-progress {
    width: 60px;
  }
}
</style>
