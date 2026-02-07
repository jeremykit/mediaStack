<template>
  <div class="view-codes-page">
    <div class="page-header">
      <h2>观看码管理</h2>
      <div class="header-actions">
        <el-button
          v-if="selectedViewCodes.length > 0"
          type="danger"
          @click="handleBulkDelete"
          :loading="bulkDeleting"
        >批量删除 ({{ selectedViewCodes.length }})</el-button>
        <el-button type="primary" @click="showAddDialog = true">
          <el-icon><Plus /></el-icon>
          新增观看码
        </el-button>
      </div>
    </div>

    <el-table :data="viewCodes" v-loading="loading" stripe @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="55" />
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="code" label="观看码" width="150">
        <template #default="{ row }">
          <div class="code-cell">
            <code>{{ row.code }}</code>
            <el-button size="small" text @click="copyCode(row.code)">
              <el-icon><CopyDocument /></el-icon>
            </el-button>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="is_active" label="状态" width="100">
        <template #default="{ row }">
          <el-switch
            v-model="row.is_active"
            @change="toggleActive(row)"
          />
        </template>
      </el-table-column>
      <el-table-column label="关联分类" min-width="200">
        <template #default="{ row }">
          <el-tag
            v-for="name in row.category_names"
            :key="name"
            size="small"
            style="margin-right: 4px"
          >
            {{ name }}
          </el-tag>
          <span v-if="row.category_names.length === 0" class="text-muted">无</span>
        </template>
      </el-table-column>
      <el-table-column prop="expires_at" label="过期时间" width="180">
        <template #default="{ row }">
          <span v-if="row.expires_at">{{ formatDate(row.expires_at) }}</span>
          <span v-else class="text-muted">永不过期</span>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="180">
        <template #default="{ row }">
          {{ formatDate(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="100" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="editViewCode(row)">编辑</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- Mobile Card Layout -->
    <div class="mobile-viewcode-cards" v-loading="loading">
      <div
        v-for="code in viewCodes"
        :key="code.id"
        class="viewcode-card"
      >
        <div class="viewcode-card-header">
          <div class="viewcode-card-code">
            <code>{{ code.code }}</code>
            <el-button size="small" text @click="copyCode(code.code)">
              <el-icon><CopyDocument /></el-icon>
            </el-button>
          </div>
          <el-switch
            v-model="code.is_active"
            @change="toggleActive(code)"
          />
        </div>

        <div class="viewcode-card-row" v-if="code.category_names.length > 0">
          <span class="viewcode-card-label">分类</span>
          <div class="viewcode-card-tags">
            <el-tag
              v-for="name in code.category_names"
              :key="name"
              size="small"
            >
              {{ name }}
            </el-tag>
          </div>
        </div>

        <div class="viewcode-card-row">
          <span class="viewcode-card-label">过期</span>
          <span class="viewcode-card-value">
            {{ code.expires_at ? formatDate(code.expires_at) : '永不过期' }}
          </span>
        </div>

        <div class="viewcode-card-time">{{ formatDate(code.created_at) }}</div>

        <div class="viewcode-card-actions">
          <el-button size="small" @click="editViewCode(code)">编辑</el-button>
        </div>
      </div>

      <div v-if="viewCodes.length === 0 && !loading" class="empty-state">
        <p>暂无观看码</p>
      </div>
    </div>

    <!-- Add/Edit Dialog -->
    <el-dialog
      v-model="showDialog"
      :title="editingViewCode ? '编辑观看码' : '新增观看码'"
      width="500px"
      :class="{ 'mobile-dialog': isMobile }"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="观看码" prop="code" v-if="!editingViewCode">
          <el-input
            v-model="form.code"
            placeholder="6-12位字母数字"
            maxlength="12"
          />
          <el-button type="primary" text @click="generateCode">随机生成</el-button>
        </el-form-item>
        <el-form-item label="关联分类">
          <el-select
            v-model="form.category_ids"
            multiple
            placeholder="选择可访问的分类"
            style="width: 100%"
            :teleported="!isMobile"
            :popper-class="{ 'mobile-select-dropdown': isMobile }"
          >
            <el-option
              v-for="cat in categories"
              :key="cat.id"
              :label="cat.name"
              :value="cat.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="过期时间">
          <el-date-picker
            v-model="form.expires_at"
            type="datetime"
            placeholder="留空表示永不过期"
            style="width: 100%"
            :teleported="!isMobile"
          />
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="form.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Plus, CopyDocument } from '@element-plus/icons-vue'
import { viewCodesApi, type ViewCode } from '../../api/viewCodes'
import { categoriesApi, type Category } from '../../api/categories'

const viewCodes = ref<ViewCode[]>([])
const categories = ref<Category[]>([])
const loading = ref(false)
const showAddDialog = ref(false)
const editingViewCode = ref<ViewCode | null>(null)
const submitting = ref(false)
const formRef = ref<FormInstance>()
const selectedViewCodes = ref<ViewCode[]>([])
const bulkDeleting = ref(false)

// Mobile detection
const isMobile = ref(false)
const checkMobile = () => {
  isMobile.value = window.innerWidth < 768
}

const showDialog = computed({
  get: () => showAddDialog.value || editingViewCode.value !== null,
  set: (val) => {
    if (!val) {
      showAddDialog.value = false
      editingViewCode.value = null
      resetForm()
    }
  }
})

const form = reactive({
  code: '',
  is_active: true,
  expires_at: null as Date | null,
  category_ids: [] as number[]
})

const rules: FormRules = {
  code: [
    { required: true, message: '请输入观看码', trigger: 'blur' },
    { min: 6, max: 12, message: '观看码长度为6-12位', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9]+$/, message: '只能包含字母和数字', trigger: 'blur' }
  ]
}

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleString('zh-CN')
}

const resetForm = () => {
  form.code = ''
  form.is_active = true
  form.expires_at = null
  form.category_ids = []
}

const generateCode = () => {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghjkmnpqrstuvwxyz23456789'
  let code = ''
  for (let i = 0; i < 8; i++) {
    code += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  form.code = code
}

const copyCode = async (code: string) => {
  try {
    await navigator.clipboard.writeText(code)
    ElMessage.success('已复制到剪贴板')
  } catch (e) {
    ElMessage.error('复制失败')
  }
}

const loadViewCodes = async () => {
  loading.value = true
  try {
    const { data } = await viewCodesApi.list()
    viewCodes.value = data
  } catch (e) {
    ElMessage.error('加载观看码失败')
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

const editViewCode = (viewCode: ViewCode) => {
  editingViewCode.value = viewCode
  form.code = viewCode.code
  form.is_active = viewCode.is_active
  form.expires_at = viewCode.expires_at ? new Date(viewCode.expires_at) : null
  form.category_ids = [...viewCode.category_ids]
}

const toggleActive = async (viewCode: ViewCode) => {
  try {
    await viewCodesApi.update(viewCode.id, { is_active: viewCode.is_active })
    ElMessage.success(viewCode.is_active ? '已启用' : '已禁用')
  } catch (e: any) {
    viewCode.is_active = !viewCode.is_active
    ElMessage.error(e.response?.data?.detail || '操作失败')
  }
}

const handleSelectionChange = (selection: ViewCode[]) => {
  selectedViewCodes.value = selection
}

const handleBulkDelete = async () => {
  if (selectedViewCodes.value.length === 0) return

  try {
    await ElMessageBox.confirm(
      `确定删除选中的 ${selectedViewCodes.value.length} 个观看码吗？`,
      '批量删除',
      { type: 'warning' }
    )
    bulkDeleting.value = true
    const deletePromises = selectedViewCodes.value.map(c => viewCodesApi.delete(c.id))
    await Promise.allSettled(deletePromises)
    ElMessage.success('删除成功')
    selectedViewCodes.value = []
    loadViewCodes()
  } catch (e: any) {
    if (e !== 'cancel') {
      ElMessage.error(e.response?.data?.detail || '删除失败')
    }
  } finally {
    bulkDeleting.value = false
  }
}

const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate()

  submitting.value = true
  try {
    const data = {
      is_active: form.is_active,
      expires_at: form.expires_at ? form.expires_at.toISOString() : null,
      category_ids: form.category_ids
    }

    if (editingViewCode.value) {
      await viewCodesApi.update(editingViewCode.value.id, data)
      ElMessage.success('更新成功')
    } else {
      await viewCodesApi.create({
        code: form.code,
        ...data
      })
      ElMessage.success('创建成功')
    }
    showDialog.value = false
    loadViewCodes()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '操作失败')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadViewCodes()
  loadCategories()
  checkMobile()
  window.addEventListener('resize', checkMobile)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})
</script>

<style scoped>
.view-codes-page {
  padding: 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h2 {
  font-size: 20px;
  font-weight: 600;
  color: #fff;
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.code-cell {
  display: flex;
  align-items: center;
  gap: 4px;
}

.code-cell code {
  font-family: var(--font-mono);
  background: rgba(139, 92, 246, 0.2);
  color: #8B5CF6;
  padding: 4px 8px;
  border-radius: 6px;
  font-weight: 500;
}

.text-muted {
  color: rgba(255, 255, 255, 0.4);
}

/* Override Element Plus table styles for dark theme */
:deep(.el-table) {
  background: rgba(15, 20, 35, 0.6);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  overflow: hidden;
  color: #e4e7eb;
}

:deep(.el-table__header-wrapper) {
  background: rgba(233, 69, 96, 0.05);
}

:deep(.el-table th.el-table__cell) {
  background: transparent;
  color: rgba(255, 255, 255, 0.7);
  font-weight: 600;
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

:deep(.el-table tr) {
  background: transparent;
}

:deep(.el-table__row) {
  transition: all 0.3s ease;
}

:deep(.el-table__row:hover > td) {
  background: rgba(233, 69, 96, 0.08) !important;
}

:deep(.el-table td.el-table__cell) {
  border-bottom: 1px solid rgba(255, 255, 255, 0.03);
  color: #e4e7eb;
}

:deep(.el-table--striped .el-table__body tr.el-table__row--striped td) {
  background: rgba(255, 255, 255, 0.02);
}

:deep(.el-table__empty-block) {
  background: transparent;
}

:deep(.el-table__empty-text) {
  color: rgba(255, 255, 255, 0.4);
}

/* Button styles */
:deep(.el-button) {
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.3s ease;
}

:deep(.el-button--primary) {
  background: linear-gradient(135deg, #E94560 0%, #8B5CF6 100%);
  border: none;
  box-shadow: 0 4px 12px rgba(233, 69, 96, 0.3);
}

:deep(.el-button--primary:hover) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(233, 69, 96, 0.4);
}

:deep(.el-button--danger) {
  background: rgba(239, 68, 68, 0.2);
  border: 1px solid rgba(239, 68, 68, 0.4);
  color: #ef4444;
}

:deep(.el-button--danger:hover) {
  background: rgba(239, 68, 68, 0.3);
  border-color: rgba(239, 68, 68, 0.6);
}

:deep(.el-button--small) {
  padding: 6px 12px;
  font-size: 13px;
}

/* Tag styles */
:deep(.el-tag) {
  border-radius: 6px;
  border: none;
  font-weight: 500;
  font-size: 12px;
  padding: 4px 12px;
}

:deep(.el-tag--success) {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
}

:deep(.el-tag--danger) {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

/* Loading overlay */
:deep(.el-loading-mask) {
  background: rgba(10, 14, 26, 0.8);
  backdrop-filter: blur(4px);
}

:deep(.el-loading-spinner .circular) {
  stroke: #E94560;
}

/* ==================== Mobile Responsive ==================== */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .page-header h2 {
    font-size: 18px;
  }

  .page-header .el-button {
    width: 100%;
  }

  /* Hide default table on mobile */
  :deep(.el-table) {
    display: none;
  }

  .empty-state {
    text-align: center;
    padding: 40px 20px;
    color: rgba(255, 255, 255, 0.4);
  }
}

@media (min-width: 769px) {
  .mobile-viewcode-cards {
    display: none !important;
  }
}

/* Mobile Card Layout */
@media (max-width: 768px) {
  .mobile-viewcode-cards {
    display: block !important;
  }

  .viewcode-card {
    background: rgba(15, 20, 35, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 12px;
    backdrop-filter: blur(10px);
  }

  .viewcode-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    padding-bottom: 12px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  }

  .viewcode-card-code {
    display: flex;
    align-items: center;
    gap: 8px;
    flex: 1;
  }

  .viewcode-card-code code {
    font-family: var(--font-mono);
    background: rgba(139, 92, 246, 0.2);
    color: #8B5CF6;
    padding: 6px 10px;
    border-radius: 6px;
    font-weight: 500;
    font-size: 14px;
    word-break: break-all;
  }

  .viewcode-card-row {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    margin-bottom: 10px;
  }

  .viewcode-card-label {
    color: rgba(255, 255, 255, 0.5);
    font-size: 12px;
    min-width: 50px;
    padding-top: 2px;
  }

  .viewcode-card-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
    flex: 1;
  }

  .viewcode-card-value {
    flex: 1;
    font-size: 14px;
    color: #e4e7eb;
  }

  .viewcode-card-time {
    font-size: 11px;
    color: rgba(255, 255, 255, 0.4);
    margin-bottom: 10px;
  }

  .viewcode-card-actions {
    display: flex;
    gap: 8px;
    padding-top: 10px;
    border-top: 1px solid rgba(255, 255, 255, 0.08);
  }

  .viewcode-card-actions .el-button {
    flex: 1;
  }

  /* Dialog mobile styles */
  :deep(.el-dialog) {
    width: 90vw !important;
    max-width: 500px;
  }
}
</style>