<template>
  <div class="categories-page">
    <div class="page-header">
      <h2>分类管理</h2>
      <el-button type="primary" @click="showAddDialog = true">
        <el-icon><Plus /></el-icon>
        新增分类
      </el-button>
    </div>

    <el-table :data="categories" v-loading="loading" stripe>
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="分类名称" />
      <el-table-column prop="sort_order" label="排序" width="100" />
      <el-table-column prop="video_count" label="视频数" width="100" />
      <el-table-column prop="created_at" label="创建时间" width="180">
        <template #default="{ row }">
          {{ formatDate(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="editCategory(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="deleteCategory(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

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

const deleteCategory = async (category: Category) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除分类 "${category.name}" 吗？`,
      '确认删除',
      { type: 'warning' }
    )
    await categoriesApi.delete(category.id)
    ElMessage.success('删除成功')
    loadCategories()
  } catch (e: any) {
    if (e !== 'cancel') {
      ElMessage.error(e.response?.data?.detail || '删除失败')
    }
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
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
}
</style>
