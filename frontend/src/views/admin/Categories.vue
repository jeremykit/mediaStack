<template>
  <div class="categories-page">
    <div class="page-header">
      <h2>分类管理</h2>
      <div class="header-actions">
        <el-button
          v-if="selectedCategories.length > 0"
          type="danger"
          @click="handleBulkDelete"
          :loading="bulkDeleting"
        >批量删除 ({{ selectedCategories.length }})</el-button>
        <el-button type="primary" @click="showAddDialog = true">
          <el-icon><Plus /></el-icon>
          新增分类
        </el-button>
      </div>
    </div>

    <el-table :data="categories" v-loading="loading" stripe @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="55" />
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="分类名称" />
      <el-table-column prop="sort_order" label="排序" width="100" />
      <el-table-column prop="video_count" label="视频数" width="100" />
      <el-table-column prop="created_at" label="创建时间" width="180">
        <template #default="{ row }">
          {{ formatDate(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="100" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="editCategory(row)">编辑</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- Mobile Card Layout -->
    <div class="mobile-category-cards" v-loading="loading">
      <div
        v-for="category in categories"
        :key="category.id"
        class="category-card"
      >
        <div class="category-card-header">
          <span class="category-card-name">{{ category.name }}</span>
          <span class="category-card-meta">排序: {{ category.sort_order }}</span>
        </div>
        <div class="category-card-meta">{{ category.video_count }} 个视频</div>
        <div class="category-card-time">{{ formatDate(category.created_at) }}</div>
        <div class="category-card-actions">
          <el-button size="small" @click="editCategory(category)">编辑</el-button>
        </div>
      </div>

      <div v-if="categories.length === 0 && !loading" class="empty-state">
        <p>暂无分类</p>
      </div>
    </div>

    <!-- Add/Edit Dialog -->
    <el-dialog
      v-model="showDialog"
      :title="editingCategory ? '编辑分类' : '新增分类'"
      width="400px"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入分类名称" maxlength="32" />
        </el-form-item>
        <el-form-item label="排序" prop="sort_order">
          <el-input-number v-model="form.sort_order" :min="0" :max="9999" />
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
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { categoriesApi, type Category } from '../../api/categories'

const categories = ref<Category[]>([])
const loading = ref(false)
const showAddDialog = ref(false)
const editingCategory = ref<Category | null>(null)
const submitting = ref(false)
const formRef = ref<FormInstance>()
const selectedCategories = ref<Category[]>([])
const bulkDeleting = ref(false)

const showDialog = computed({
  get: () => showAddDialog.value || editingCategory.value !== null,
  set: (val) => {
    if (!val) {
      showAddDialog.value = false
      editingCategory.value = null
    }
  }
})

const form = reactive({
  name: '',
  sort_order: 0
})

const rules: FormRules = {
  name: [
    { required: true, message: '请输入分类名称', trigger: 'blur' },
    { max: 32, message: '名称不能超过32个字符', trigger: 'blur' }
  ]
}

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleString('zh-CN')
}

const loadCategories = async () => {
  loading.value = true
  try {
    const { data } = await categoriesApi.list()
    categories.value = data
  } catch (e) {
    ElMessage.error('加载分类失败')
  } finally {
    loading.value = false
  }
}

const editCategory = (category: Category) => {
  editingCategory.value = category
  form.name = category.name
  form.sort_order = category.sort_order
}

const handleSelectionChange = (selection: Category[]) => {
  selectedCategories.value = selection
}

const handleBulkDelete = async () => {
  if (selectedCategories.value.length === 0) return

  try {
    await ElMessageBox.confirm(
      `确定删除选中的 ${selectedCategories.value.length} 个分类吗？`,
      '批量删除',
      { type: 'warning' }
    )
    bulkDeleting.value = true
    const deletePromises = selectedCategories.value.map(c => categoriesApi.delete(c.id))
    await Promise.allSettled(deletePromises)
    ElMessage.success('删除成功')
    selectedCategories.value = []
    loadCategories()
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
    if (editingCategory.value) {
      await categoriesApi.update(editingCategory.value.id, {
        name: form.name,
        sort_order: form.sort_order
      })
      ElMessage.success('更新成功')
    } else {
      await categoriesApi.create({
        name: form.name,
        sort_order: form.sort_order
      })
      ElMessage.success('创建成功')
    }
    showDialog.value = false
    form.name = ''
    form.sort_order = 0
    loadCategories()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '操作失败')
  } finally {
    submitting.value = false
  }
}

onMounted(loadCategories)
</script>

<style scoped>
.categories-page {
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

  /* Mobile cards */
  .mobile-category-cards {
    display: block !important;
  }

  .category-card {
    background: rgba(15, 20, 35, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 12px;
    backdrop-filter: blur(10px);
  }

  .category-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
  }

  .category-card-name {
    font-size: 16px;
    font-weight: 600;
    color: #fff;
  }

  .category-card-meta {
    font-size: 12px;
    color: rgba(255, 255, 255, 0.4);
    margin-bottom: 10px;
  }

  .category-card-actions {
    display: flex;
    gap: 8px;
  }

  .category-card-actions .el-button {
    flex: 1;
  }

  /* Dialog mobile styles */
  :deep(.el-dialog) {
    width: 90vw !important;
    max-width: 400px;
  }
}

@media (min-width: 769px) {
  .mobile-category-cards {
    display: none !important;
  }
}

/* ==================== Dialog Mobile Responsive ==================== */
@media (max-width: 768px) {
  :deep(.el-dialog) {
    width: 90vw !important;
    max-width: 400px;
  }

  :deep(.el-dialog__header) {
    padding: 16px;
  }

  :deep(.el-dialog__body) {
    padding: 12px 16px;
  }

  :deep(.el-dialog__footer) {
    padding: 12px 16px 16px;
  }

  :deep(.el-form-item__label) {
    font-size: 14px;
  }
}
</style>
