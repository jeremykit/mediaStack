<template>
  <div class="view-codes-page">
    <div class="page-header">
      <h2>观看码管理</h2>
      <el-button type="primary" @click="showAddDialog = true">
        <el-icon><Plus /></el-icon>
        新增观看码
      </el-button>
    </div>

    <el-table :data="viewCodes" v-loading="loading" stripe>
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
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="editViewCode(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="deleteViewCode(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- Add/Edit Dialog -->
    <el-dialog
      v-model="showDialog"
      :title="editingViewCode ? '编辑观看码' : '新增观看码'"
      width="500px"
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
import { ref, reactive, onMounted, computed } from 'vue'
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

const deleteViewCode = async (viewCode: ViewCode) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除观看码 "${viewCode.code}" 吗？`,
      '确认删除',
      { type: 'warning' }
    )
    await viewCodesApi.delete(viewCode.id)
    ElMessage.success('删除成功')
    loadViewCodes()
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
})
</script>

<style scoped>
.view-codes-page {
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

.code-cell {
  display: flex;
  align-items: center;
  gap: 4px;
}

.code-cell code {
  font-family: monospace;
  background: #f5f5f5;
  padding: 2px 6px;
  border-radius: 4px;
}

.text-muted {
  color: #999;
}
</style>
