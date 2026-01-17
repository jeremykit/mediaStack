<template>
  <div class="login-page">
    <!-- Background Effects -->
    <div class="bg-effects">
      <div class="gradient-orb orb-1"></div>
      <div class="gradient-orb orb-2"></div>
      <div class="grid-pattern"></div>
    </div>

    <!-- Login Card -->
    <div class="login-card">
      <!-- Logo & Brand -->
      <div class="brand-section">
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
        <h1 class="brand-name">MediaStack</h1>
        <p class="brand-tagline">Live Recording Studio</p>
      </div>

      <!-- Login Form -->
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="0"
        @submit.prevent="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="form.username"
            placeholder="用户名"
            prefix-icon="User"
            size="large"
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
            prefix-icon="Lock"
            size="large"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            class="login-button"
            @click="handleLogin"
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>

      <!-- Status Indicator -->
      <div class="status-indicator">
        <span class="pulse-dot"></span>
        <span class="status-text">SYSTEM READY</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { useAuthStore } from '../stores/auth'
import api from '../api'

const router = useRouter()
const auth = useAuthStore()
const formRef = ref<FormInstance>()
const loading = ref(false)

const form = reactive({
  username: '',
  password: ''
})

const rules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const handleLogin = async () => {
  if (!formRef.value) return

  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    const formData = new FormData()
    formData.append('username', form.username)
    formData.append('password', form.password)

    const { data } = await api.post('/auth/login', formData)
    auth.setToken(data.access_token)
    ElMessage.success('登录成功')
    router.push('/admin/sources')
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #0a0e1a;
  color: #e4e7eb;
  font-family: var(--font-admin);
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

/* Login Card */
.login-card {
  width: 440px;
  padding: 48px;
  background: rgba(15, 20, 35, 0.8);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(233, 69, 96, 0.1);
  border-radius: 24px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  position: relative;
  z-index: 10;
  animation: slideUp 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Brand Section */
.brand-section {
  text-align: center;
  margin-bottom: 40px;
  padding-bottom: 32px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.logo-icon {
  width: 64px;
  height: 64px;
  margin: 0 auto 20px;
  filter: drop-shadow(0 4px 16px rgba(233, 69, 96, 0.5));
  animation: logoFloat 3s ease-in-out infinite;
}

@keyframes logoFloat {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}

.brand-name {
  font-size: 32px;
  font-weight: 700;
  font-family: var(--font-mono);
  background: linear-gradient(135deg, #E94560 0%, #8B5CF6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -1px;
  margin: 0 0 8px 0;
}

.brand-tagline {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
  font-family: var(--font-mono);
  text-transform: uppercase;
  letter-spacing: 2px;
  margin: 0;
}

/* Form Styles */
.el-form {
  margin-bottom: 24px;
}

.login-button {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  background: linear-gradient(135deg, #E94560 0%, #8B5CF6 100%);
  border: none;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(233, 69, 96, 0.3);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.login-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(233, 69, 96, 0.5);
}

.login-button:active {
  transform: translateY(0);
}

/* Status Indicator */
.status-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 12px;
  background: rgba(233, 69, 96, 0.1);
  border: 1px solid rgba(233, 69, 96, 0.2);
  border-radius: 8px;
  margin-top: 24px;
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
  font-family: var(--font-mono);
  color: #E94560;
  letter-spacing: 1.5px;
}

/* Form Item Spacing */
:deep(.el-form-item) {
  margin-bottom: 20px;
}

:deep(.el-form-item:last-child) {
  margin-bottom: 0;
}

/* Input Styles */
:deep(.el-input__wrapper) {
  height: 48px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  box-shadow: none;
  transition: all 0.3s ease;
}

:deep(.el-input__wrapper:hover) {
  border-color: rgba(233, 69, 96, 0.3);
}

:deep(.el-input__wrapper.is-focus) {
  border-color: #E94560;
  box-shadow: 0 0 0 3px rgba(233, 69, 96, 0.1);
}

:deep(.el-input__inner) {
  color: #e4e7eb;
  font-size: 15px;
}

:deep(.el-input__inner::placeholder) {
  color: rgba(255, 255, 255, 0.3);
}

:deep(.el-input__prefix) {
  color: rgba(255, 255, 255, 0.4);
}

:deep(.el-input__suffix) {
  color: rgba(255, 255, 255, 0.4);
}
</style>
