<template>
  <el-container class="admin-layout">
    <el-aside width="200px">
      <el-menu :default-active="route.path" router>
        <el-menu-item index="/admin/sources">
          <span>直播源管理</span>
        </el-menu-item>
        <el-menu-item index="/admin/tasks">
          <span>录制任务</span>
        </el-menu-item>
        <el-menu-item index="/admin/schedules">
          <span>定时计划</span>
        </el-menu-item>
        <el-menu-item index="/admin/videos">
          <span>视频管理</span>
        </el-menu-item>
        <el-menu-item index="/admin/system">
          <span>系统状态</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="admin-header">
        <SystemStatus />
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
import SystemStatus from '../../components/SystemStatus.vue'
const route = useRoute()
</script>

<style scoped>
.admin-layout {
  height: 100vh;
}
.el-aside {
  background: #304156;
}
.el-menu {
  border-right: none;
  background: #304156;
}
.el-menu-item {
  color: #bfcbd9;
}
.el-menu-item:hover,
.el-menu-item.is-active {
  background: #263445 !important;
  color: #409eff;
}
.admin-header {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  background: #304156;
  border-bottom: 1px solid #263445;
}
</style>
