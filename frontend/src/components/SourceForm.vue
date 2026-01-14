<template>
  <el-dialog :title="isEdit ? '编辑直播源' : '添加直播源'" v-model="visible" width="500px">
    <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
      <el-form-item label="名称" prop="name">
        <el-input v-model="form.name" placeholder="请输入直播源名称" />
      </el-form-item>
      <el-form-item label="协议" prop="protocol">
        <el-select v-model="form.protocol" placeholder="请选择协议">
          <el-option label="RTMP" value="rtmp" />
          <el-option label="HLS/M3U8" value="hls" />
        </el-select>
      </el-form-item>
      <el-form-item label="拉流地址" prop="url">
        <el-input v-model="form.url" placeholder="请输入拉流地址" />
      </el-form-item>
      <el-form-item label="保留天数" prop="retention_days">
        <el-input-number v-model="form.retention_days" :min="1" :max="3650" />
      </el-form-item>
      <el-form-item label="启用">
        <el-switch v-model="form.is_active" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" @click="handleSubmit" :loading="loading">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { sourcesApi, type Source, type SourceCreate } from '../api/sources'
import { ElMessage } from 'element-plus'

const props = defineProps<{
  modelValue: boolean
  source?: Source | null
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'success': []
}>()

const visible = ref(false)
const loading = ref(false)
const formRef = ref<FormInstance>()
const isEdit = ref(false)

const form = reactive<SourceCreate & { id?: number }>({
  name: '',
  protocol: 'rtmp',
  url: '',
  retention_days: 365,
  is_active: true
})

const rules: FormRules = {
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  protocol: [{ required: true, message: '请选择协议', trigger: 'change' }],
  url: [{ required: true, message: '请输入拉流地址', trigger: 'blur' }]
}

watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val && props.source) {
    isEdit.value = true
    Object.assign(form, props.source)
  } else {
    isEdit.value = false
    Object.assign(form, { name: '', protocol: 'rtmp', url: '', retention_days: 365, is_active: true })
  }
})

watch(visible, (val) => emit('update:modelValue', val))

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate()

  loading.value = true
  try {
    if (isEdit.value && form.id) {
      await sourcesApi.update(form.id, form)
      ElMessage.success('更新成功')
    } else {
      await sourcesApi.create(form)
      ElMessage.success('创建成功')
    }
    visible.value = false
    emit('success')
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '操作失败')
  } finally {
    loading.value = false
  }
}
</script>
