<template>
  <el-dialog :title="isEdit ? '编辑定时计划' : '添加定时计划'" v-model="visible" width="500px">
    <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
      <el-form-item label="直播源" prop="source_id" v-if="!isEdit">
        <el-select v-model="form.source_id" placeholder="请选择直播源" style="width: 100%">
          <el-option v-for="source in sources" :key="source.id" :label="source.name" :value="source.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="Cron 表达式" prop="cron_expr">
        <el-input v-model="form.cron_expr" placeholder="如: 0 8 * * 6 (每周六8点)" />
        <div class="cron-help">格式: 分 时 日 月 周 | 示例: 0 8 * * * (每天8点), 0 8 * * 6 (每周六8点)</div>
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
import { schedulesApi, type Schedule, type ScheduleCreate } from '../api/schedules'
import { sourcesApi, type Source } from '../api/sources'
import { ElMessage } from 'element-plus'

const props = defineProps<{ modelValue: boolean; schedule?: Schedule | null }>()
const emit = defineEmits<{ 'update:modelValue': [value: boolean]; success: [] }>()

const visible = ref(false)
const loading = ref(false)
const formRef = ref<FormInstance>()
const isEdit = ref(false)
const sources = ref<Source[]>([])

const form = reactive<ScheduleCreate & { id?: number }>({ source_id: 0, cron_expr: '', is_active: true })

const rules: FormRules = {
  source_id: [{ required: true, message: '请选择直播源', trigger: 'change' }],
  cron_expr: [{ required: true, message: '请输入 Cron 表达式', trigger: 'blur' }]
}

watch(() => props.modelValue, async (val) => {
  visible.value = val
  if (val) {
    try { sources.value = (await sourcesApi.list()).data } catch {}
    if (props.schedule) {
      isEdit.value = true
      Object.assign(form, props.schedule)
    } else {
      isEdit.value = false
      Object.assign(form, { source_id: 0, cron_expr: '', is_active: true })
    }
  }
})

watch(visible, (val) => emit('update:modelValue', val))

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate()
  loading.value = true
  try {
    if (isEdit.value && form.id) {
      await schedulesApi.update(form.id, { cron_expr: form.cron_expr, is_active: form.is_active })
    } else {
      await schedulesApi.create(form)
    }
    ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
    visible.value = false
    emit('success')
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '操作失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.cron-help { font-size: 12px; color: #909399; margin-top: 4px; }
</style>
