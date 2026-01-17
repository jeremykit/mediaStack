<template>
  <div class="admin-layout">
    <!-- Sidebar -->
    <aside class="sidebar">
      <!-- Logo & Brand -->
      <div class="brand-section">
        <div class="logo-container">
          <svg class="logo-icon" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="4" y="4" width="40" height="40" rx="8" fill="url(#logo-gradient)" />
            <path d="M16 18L24 14L32 18V30L24 34L16 30V18Z" stroke="white" stroke-width="2" stroke-linejoin="round" />
            <circle cx="24" cy="24" r="3" fill="white" />
            <defs>
              <linearGradient id="logo-gradient" x1="4" y1="4" x2="44" y2="44" gradientUnits="userSpaceOnUse">
                <stop stop-color="#E94560" />
                <stop offset="1" stop-color="#8B5CF6" />
              </linearGradient>
            </defs>
          </svg>
          <div class="brand-text">
            <h1 class="brand-name">MediaStack</h1>
            <span class="brand-tagline">Live Recording Studio</span>
          </div>
        </div>
        <div class="status-indicator">
          <span class="pulse-dot"></span>
          <span class="status-text">LIVE</span>
        </div>
      </div>

      <!-- Navigation Menu -->
      <nav class="nav-menu">
        <div class="nav-section">
          <div class="nav-section-title">录制控制</div>
          <router-link
            v-for="item in recordingMenuItems"
            :key="item.path"
            :to="item.path"
            class="nav-item"
            :class="{ active: route.path === item.path }"
          >
            <component :is="item.icon" class="nav-icon" />
            <span class="nav-label">{{ item.label }}</span>
            <span v-if="item.badge" class="nav-badge">{{ item.badge }}</span>
          </router-link>
        </div>

        <div class="nav-section">
          <div class="nav-section-title">内容管理</div>
          <router-link
            v-for="item in contentMenuItems"
            :key="item.path"
            :to="item.path"
            class="nav-item"
            :class="{ active: route.path === item.path }"
          >
            <component :is="item.icon" class="nav-icon" />
            <span class="nav-label">{{ item.label }}</span>
          </router-link>
        </div>

        <div class="nav-section">
          <div class="nav-section-title">系统设置</div>
          <router-link
            v-for="item in systemMenuItems"
            :key="item.path"
            :to="item.path"
            class="nav-item"
            :class="{ active: route.path === item.path }"
          >
            <component :is="item.icon" class="nav-icon" />
            <span class="nav-label">{{ item.label }}</span>
          </router-link>
        </div>
      </nav>

      <!-- Sidebar Footer -->
      <div class="sidebar-footer">
        <div class="user-profile">
          <div class="user-avatar">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="12" cy="8" r="4" stroke="currentColor" stroke-width="2" />
              <path d="M6 21C6 17.134 8.686 14 12 14C15.314 14 18 17.134 18 21" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
            </svg>
          </div>
          <div class="user-info">
            <div class="user-name">Admin</div>
            <div class="user-role">管理员</div>
          </div>
        </div>
      </div>
    </aside>

    <!-- Main Content Area -->
    <div class="main-container">
      <!-- Top Header -->
      <header class="top-header">
        <div class="header-left">
          <h2 class="page-title">{{ currentPageTitle }}</h2>
        </div>
        <div class="header-right">
          <SystemStatus />
        </div>
      </header>

      <!-- Page Content -->
      <main class="page-content">
        <router-view v-slot="{ Component }">
          <transition name="page-fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>

    <!-- Background Effects -->
    <div class="bg-effects">
      <div class="gradient-orb orb-1"></div>
      <div class="gradient-orb orb-2"></div>
      <div class="grid-pattern"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, h } from 'vue'
import { useRoute } from 'vue-router'
import SystemStatus from '../../components/SystemStatus.vue'

const route = useRoute()

// SVG Icon Components
const IconBroadcast = () => h('svg', { viewBox: '0 0 24 24', fill: 'none', xmlns: 'http://www.w3.org/2000/svg' }, [
  h('circle', { cx: '12', cy: '12', r: '2', fill: 'currentColor' }),
  h('path', { d: 'M8.5 8.5C9.88071 7.11929 12.1193 7.11929 13.5 8.5M6 6C8.76142 3.23858 13.2386 3.23858 16 6M18.5 8.5C17.1193 7.11929 14.8807 7.11929 13.5 8.5M20 6C17.2386 3.23858 12.7614 3.23858 10 6', stroke: 'currentColor', 'stroke-width': '2', 'stroke-linecap': 'round' })
])

const IconRecord = () => h('svg', { viewBox: '0 0 24 24', fill: 'none', xmlns: 'http://www.w3.org/2000/svg' }, [
  h('circle', { cx: '12', cy: '12', r: '8', stroke: 'currentColor', 'stroke-width': '2' }),
  h('circle', { cx: '12', cy: '12', r: '4', fill: 'currentColor' })
])

const IconClock = () => h('svg', { viewBox: '0 0 24 24', fill: 'none', xmlns: 'http://www.w3.org/2000/svg' }, [
  h('circle', { cx: '12', cy: '12', r: '9', stroke: 'currentColor', 'stroke-width': '2' }),
  h('path', { d: 'M12 7V12L15 15', stroke: 'currentColor', 'stroke-width': '2', 'stroke-linecap': 'round' })
])

const IconFolder = () => h('svg', { viewBox: '0 0 24 24', fill: 'none', xmlns: 'http://www.w3.org/2000/svg' }, [
  h('path', { d: 'M3 7C3 5.89543 3.89543 5 5 5H9L11 7H19C20.1046 7 21 7.89543 21 9V17C21 18.1046 20.1046 19 19 19H5C3.89543 19 3 18.1046 3 17V7Z', stroke: 'currentColor', 'stroke-width': '2' })
])

const IconVideo = () => h('svg', { viewBox: '0 0 24 24', fill: 'none', xmlns: 'http://www.w3.org/2000/svg' }, [
  h('rect', { x: '2', y: '6', width: '14', height: '12', rx: '2', stroke: 'currentColor', 'stroke-width': '2' }),
  h('path', { d: 'M16 10L22 7V17L16 14V10Z', stroke: 'currentColor', 'stroke-width': '2', 'stroke-linejoin': 'round' })
])

const IconUpload = () => h('svg', { viewBox: '0 0 24 24', fill: 'none', xmlns: 'http://www.w3.org/2000/svg' }, [
  h('path', { d: 'M12 4V16M12 4L8 8M12 4L16 8', stroke: 'currentColor', 'stroke-width': '2', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }),
  h('path', { d: 'M4 17V19C4 20.1046 4.89543 21 6 21H18C19.1046 21 20 20.1046 20 19V17', stroke: 'currentColor', 'stroke-width': '2', 'stroke-linecap': 'round' })
])

const IconTag = () => h('svg', { viewBox: '0 0 24 24', fill: 'none', xmlns: 'http://www.w3.org/2000/svg' }, [
  h('path', { d: 'M3 10.5V5C3 3.89543 3.89543 3 5 3H10.5L21 13.5L13.5 21L3 10.5Z', stroke: 'currentColor', 'stroke-width': '2' }),
  h('circle', { cx: '8', cy: '8', r: '1.5', fill: 'currentColor' })
])

const IconGrid = () => h('svg', { viewBox: '0 0 24 24', fill: 'none', xmlns: 'http://www.w3.org/2000/svg' }, [
  h('rect', { x: '3', y: '3', width: '7', height: '7', rx: '1', stroke: 'currentColor', 'stroke-width': '2' }),
  h('rect', { x: '14', y: '3', width: '7', height: '7', rx: '1', stroke: 'currentColor', 'stroke-width': '2' }),
  h('rect', { x: '3', y: '14', width: '7', height: '7', rx: '1', stroke: 'currentColor', 'stroke-width': '2' }),
  h('rect', { x: '14', y: '14', width: '7', height: '7', rx: '1', stroke: 'currentColor', 'stroke-width': '2' })
])

const IconKey = () => h('svg', { viewBox: '0 0 24 24', fill: 'none', xmlns: 'http://www.w3.org/2000/svg' }, [
  h('circle', { cx: '8', cy: '15', r: '5', stroke: 'currentColor', 'stroke-width': '2' }),
  h('path', { d: 'M12 11L21 2M21 2H17M21 2V6', stroke: 'currentColor', 'stroke-width': '2', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' })
])

const IconChart = () => h('svg', { viewBox: '0 0 24 24', fill: 'none', xmlns: 'http://www.w3.org/2000/svg' }, [
  h('path', { d: 'M3 3V21H21', stroke: 'currentColor', 'stroke-width': '2', 'stroke-linecap': 'round' }),
  h('path', { d: 'M7 14L11 10L15 14L21 8', stroke: 'currentColor', 'stroke-width': '2', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' })
])

// Menu Items
const recordingMenuItems = [
  { path: '/admin/sources', label: '直播源管理', icon: IconBroadcast },
  { path: '/admin/tasks', label: '录制任务', icon: IconRecord },
  { path: '/admin/schedules', label: '定时计划', icon: IconClock },
  { path: '/admin/recordings', label: '录制管理', icon: IconFolder }
]

const contentMenuItems = [
  { path: '/admin/videos', label: '视频管理', icon: IconVideo },
  { path: '/admin/upload', label: '文件上传', icon: IconUpload },
  { path: '/admin/categories', label: '分类管理', icon: IconGrid },
  { path: '/admin/tags', label: '标签管理', icon: IconTag },
  { path: '/admin/view-codes', label: '观看码管理', icon: IconKey }
]

const systemMenuItems = [
  { path: '/admin/system', label: '系统状态', icon: IconChart }
]

const currentPageTitle = computed(() => {
  const allItems = [...recordingMenuItems, ...contentMenuItems, ...systemMenuItems]
  const current = allItems.find(item => item.path === route.path)
  return current?.label || 'MediaStack'
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Noto+Sans+SC:wght@400;500;600;700&display=swap');

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.admin-layout {
  display: flex;
  height: 100vh;
  background: #0a0e1a;
  color: #e4e7eb;
  font-family: 'Noto Sans SC', 'JetBrains Mono', sans-serif;
  position: relative;
  overflow: hidden;
}

/* Background Effects */
.bg-effects {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
}

.gradient-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(120px);
  opacity: 0.15;
  animation: float 20s ease-in-out infinite;
}

.orb-1 {
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, #E94560 0%, transparent 70%);
  top: -200px;
  left: -200px;
  animation-delay: 0s;
}

.orb-2 {
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, #8B5CF6 0%, transparent 70%);
  bottom: -150px;
  right: -150px;
  animation-delay: -10s;
}

@keyframes float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(50px, -50px) scale(1.1); }
  66% { transform: translate(-30px, 30px) scale(0.9); }
}

.grid-pattern {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(233, 69, 96, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(139, 92, 246, 0.03) 1px, transparent 1px);
  background-size: 50px 50px;
  mask-image: radial-gradient(ellipse 80% 50% at 50% 50%, black 40%, transparent 100%);
}

/* Sidebar */
.sidebar {
  width: 280px;
  background: rgba(15, 20, 35, 0.8);
  backdrop-filter: blur(20px);
  border-right: 1px solid rgba(233, 69, 96, 0.1);
  display: flex;
  flex-direction: column;
  position: relative;
  z-index: 10;
  box-shadow: 4px 0 24px rgba(0, 0, 0, 0.3);
}

/* Brand Section */
.brand-section {
  padding: 24px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.logo-icon {
  width: 48px;
  height: 48px;
  filter: drop-shadow(0 4px 12px rgba(233, 69, 96, 0.4));
}

.brand-text {
  flex: 1;
}

.brand-name {
  font-size: 20px;
  font-weight: 700;
  font-family: 'JetBrains Mono', monospace;
  background: linear-gradient(135deg, #E94560 0%, #8B5CF6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -0.5px;
  margin: 0;
}

.brand-tagline {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
  font-family: 'JetBrains Mono', monospace;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: rgba(233, 69, 96, 0.1);
  border: 1px solid rgba(233, 69, 96, 0.2);
  border-radius: 6px;
}

.pulse-dot {
  width: 8px;
  height: 8px;
  background: #E94560;
  border-radius: 50%;
  animation: pulse 2s ease-in-out infinite;
  box-shadow: 0 0 12px rgba(233, 69, 96, 0.8);
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.6; transform: scale(0.9); }
}

.status-text {
  font-size: 11px;
  font-weight: 600;
  font-family: 'JetBrains Mono', monospace;
  color: #E94560;
  letter-spacing: 1px;
}

/* Navigation Menu */
.nav-menu {
  flex: 1;
  overflow-y: auto;
  padding: 16px 0;
}

.nav-menu::-webkit-scrollbar {
  width: 4px;
}

.nav-menu::-webkit-scrollbar-track {
  background: transparent;
}

.nav-menu::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
}

.nav-section {
  margin-bottom: 24px;
}

.nav-section-title {
  font-size: 11px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.3);
  text-transform: uppercase;
  letter-spacing: 1.5px;
  padding: 0 20px 8px;
  font-family: 'JetBrains Mono', monospace;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  color: rgba(255, 255, 255, 0.6);
  text-decoration: none;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  margin: 2px 12px;
  border-radius: 8px;
}

.nav-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 0;
  background: linear-gradient(180deg, #E94560 0%, #8B5CF6 100%);
  border-radius: 0 2px 2px 0;
  transition: height 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.nav-item:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.05);
}

.nav-item:hover::before {
  height: 60%;
}

.nav-item.active {
  color: #fff;
  background: rgba(233, 69, 96, 0.15);
  border: 1px solid rgba(233, 69, 96, 0.2);
}

.nav-item.active::before {
  height: 80%;
}

.nav-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.nav-label {
  flex: 1;
  font-size: 14px;
  font-weight: 500;
}

.nav-badge {
  padding: 2px 8px;
  background: rgba(233, 69, 96, 0.2);
  color: #E94560;
  font-size: 11px;
  font-weight: 600;
  border-radius: 10px;
  font-family: 'JetBrains Mono', monospace;
}

/* Sidebar Footer */
.sidebar-footer {
  padding: 16px 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  transition: all 0.3s ease;
  cursor: pointer;
}

.user-profile:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(233, 69, 96, 0.3);
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: linear-gradient(135deg, #E94560 0%, #8B5CF6 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.user-avatar svg {
  width: 20px;
  height: 20px;
}

.user-info {
  flex: 1;
}

.user-name {
  font-size: 14px;
  font-weight: 600;
  color: #fff;
}

.user-role {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
}

/* Main Container */
.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  position: relative;
  z-index: 1;
  overflow: hidden;
}

/* Top Header */
.top-header {
  height: 72px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
  background: rgba(15, 20, 35, 0.6);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  position: relative;
  z-index: 10;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #fff;
  margin: 0;
  font-family: 'Noto Sans SC', sans-serif;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

/* Page Content */
.page-content {
  flex: 1;
  overflow-y: auto;
  padding: 32px;
  position: relative;
}

.page-content::-webkit-scrollbar {
  width: 8px;
}

.page-content::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.02);
}

.page-content::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
}

.page-content::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.15);
}

/* Page Transition */
.page-fade-enter-active,
.page-fade-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.page-fade-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.page-fade-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}
</style>
