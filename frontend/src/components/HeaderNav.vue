<template>
  <div class="header-nav">
    <router-link
      v-if="!authStore.isLoggedIn"
      to="/login"
      class="nav-btn login-btn"
    >
      登录
    </router-link>
    <template v-else>
      <router-link
        to="/admin/sources"
        class="nav-btn admin-btn"
      >
        进入管理后台
      </router-link>
      <button
        @click="handleLogout"
        class="nav-btn logout-btn"
      >
        登出
      </button>
    </template>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { ElMessageBox, ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const handleLogout = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要登出吗？',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    authStore.logout()
    ElMessage.success('已登出')
    // 刷新当前页面以更新UI状态
    router.go(0)
  } catch {
    // 用户点击取消，什么都不做
  }
}
</script>

<style scoped>
.header-nav {
  position: absolute;
  top: 20px;
  right: 20px;
  display: flex;
  gap: 12px;
  align-items: center;
  z-index: 10;
}

.nav-btn {
  padding: 10px 20px;
  border-radius: 24px;
  font-size: 14px;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.3s ease;
  cursor: pointer;
  border: none;
  font-family: var(--font-sans);
}

.login-btn {
  background: linear-gradient(135deg, #FF6B9D 0%, #FFA06B 100%);
  color: white;
  box-shadow: 0 4px 16px rgba(255, 107, 157, 0.3);
}

.login-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(255, 107, 157, 0.4);
}

.admin-btn {
  background: rgba(255, 255, 255, 0.9);
  color: #FF6B9D;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.admin-btn:hover {
  background: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.logout-btn {
  background: transparent;
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.5);
}

.logout-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.8);
}

/* 移动端适配 */
@media (max-width: 768px) {
  .header-nav {
    top: 16px;
    right: 16px;
    gap: 8px;
  }

  .nav-btn {
    padding: 8px 16px;
    font-size: 13px;
    border-radius: 20px;
  }

  .admin-btn {
    display: none;
  }
}
</style>
