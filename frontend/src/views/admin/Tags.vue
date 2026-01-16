<template>
  <div class="tags-page">
    <div class="page-header">
      <h2>标签管理</h2>
      <el-button type="primary" @click="showAddDialog = true">
        <el-icon><Plus /></el-icon>
        新增标签
      </el-button>
    </div>

    <el-table :data="tags" v-loading="loading" stripe>
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="标签名称">
        <template #default="{ row }">
          <el-tag>{{ row.name }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="video_count" label="使用次数" width="100" />
      <el-table-column prop="created_at" label="创建时间" width="180">
        <template #default="{ row }">
          {{ formatDate(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="100" fixed="right">
        <template #default="{ row }">
          <el-button size="small" type="danger" @click="deleteTag(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- Add Dialog -->
    <el-dialog v-model="showAddDialog" title="新增标签" width="400px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入标签名称" maxlength="16" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { tagsApi, type Tag } from '../../api/tags'

const tags = ref<Tag[]>([])
const loading = ref(false)
const showAddDialog = ref(false)
const submitting = ref(false)
const formRef = ref<FormInstance>()

const form = reactive({
  name: ''
})

const rules: FormRules = {
  name: [
    { required: true, message: '请输入标签名称', trigger: 'blur' },
    { max: 16, message: '名称不能超过16个字符', trigger: 'blur' }
  ]
}

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleString('zh-CN')
}

const loadTags = async () => {
  loading.value = true
  try {
    const { data } = await tagsApi.list()
    tags.value = data
  } catch (e) {
    ElMessage.error('加载标签失败')
  } finally {
    loading.value = false
  }
}

const deleteTag = async (tag: Tag) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除标签 "${tag.name}" 吗？`,
      '确认删除',
      { type: 'warning' }
    )
    await tagsApi.delete(tag.id)
    ElMessage.success('删除成功')
    loadTags()
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
    await tagsApi.create({ name: form.name })
    ElMessage.success('创建成功')
    showAddDialog.value = false
    form.name = ''
    loadTags()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '创建失败')
  } finally {
    submitting.value = false
  }
}

onMounted(loadTags)
</script>

<style scoped>
.tags-page {
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
