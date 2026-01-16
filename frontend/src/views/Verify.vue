<template>
  <div class="verify-page">
    <div class="verify-card">
      <h1>请输入观看码</h1>
      <p class="hint">输入观看码以访问视频内容</p>

      <el-form @submit.prevent="handleVerify">
        <el-form-item>
          <el-input
            v-model="code"
            placeholder="请输入观看码"
            size="large"
            :maxlength="12"
            @keyup.enter="handleVerify"
          />
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            style="width: 100%"
            @click="handleVerify"
            :loading="loading"
          >
            验证
          </el-button>
        </el-form-item>
      </el-form>

      <p v-if="error" class="error">{{ error }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { viewCodesApi } from '../api/viewCodes'
import { useViewCodeStore } from '../stores/viewCode'

const router = useRouter()
const viewCodeStore = useViewCodeStore()

const code = ref('')
const loading = ref(false)
const error = ref('')

const handleVerify = async () => {
  if (!code.value.trim()) {
    error.value = '请输入观看码'
    return
  }

  loading.value = true
  error.value = ''

  try {
    const { data } = await viewCodesApi.verify(code.value.trim())

    if (data.valid) {
      viewCodeStore.setViewCode(code.value.trim(), data.category_ids, data.expires_at)
      ElMessage.success('验证成功')
      router.push('/')
    } else {
      error.value = '观看码无效或已过期'
    }
  } catch (e: any) {
    error.value = e.response?.data?.detail || '验证失败，请重试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.verify-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.verify-card {
  background: white;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  width: 100%;
  max-width: 400px;
}

.verify-card h1 {
  margin: 0 0 8px;
  text-align: center;
  font-size: 24px;
  color: #303133;
}

.hint {
  text-align: center;
  color: #909399;
  margin-bottom: 24px;
}

.error {
  color: #f56c6c;
  text-align: center;
  margin-top: 16px;
}
</style>
