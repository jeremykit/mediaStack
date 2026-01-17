<template>
  <div class="video-extensions">
    <el-tabs v-model="activeTab" type="border-card">
      <!-- Images Tab -->
      <el-tab-pane label="关联图片" name="images">
        <div class="tab-content">
          <div class="action-bar">
            <el-upload
              :show-file-list="false"
              :before-upload="handleImageBeforeUpload"
              accept="image/*"
            >
              <el-button type="primary" :loading="uploadingImage">
                上传图片
              </el-button>
            </el-upload>
          </div>
          <div class="image-list" v-loading="loadingImages">
            <div v-if="images.length === 0" class="empty-tip">
              暂无关联图片
            </div>
            <div v-else class="image-grid">
              <div v-for="image in images" :key="image.id" class="image-item">
                <el-image
                  :src="image.image_url"
                  fit="cover"
                  :preview-src-list="images.map(i => i.image_url)"
                  :initial-index="images.findIndex(i => i.id === image.id)"
                />
                <div class="image-actions">
                  <el-button
                    type="danger"
                    size="small"
                    :icon="Delete"
                    circle
                    @click="handleDeleteImage(image)"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <!-- Texts Tab -->
      <el-tab-pane label="关联文本" name="texts">
        <div class="tab-content">
          <div class="action-bar">
            <el-button type="primary" @click="showTextDialog()">
              添加文本
            </el-button>
          </div>
          <div class="text-list" v-loading="loadingTexts">
            <div v-if="texts.length === 0" class="empty-tip">
              暂无关联文本
            </div>
            <el-collapse v-else>
              <el-collapse-item
                v-for="text in texts"
                :key="text.id"
                :name="text.id"
              >
                <template #title>
                  <div class="text-title">
                    <span>{{ text.title }}</span>
                    <div class="text-actions" @click.stop>
                      <el-button
                        type="primary"
                        size="small"
                        :icon="Edit"
                        circle
                        @click="showTextDialog(text)"
                      />
                      <el-button
                        type="danger"
                        size="small"
                        :icon="Delete"
                        circle
                        @click="handleDeleteText(text)"
                      />
                    </div>
                  </div>
                </template>
                <div class="text-content">{{ text.content }}</div>
              </el-collapse-item>
            </el-collapse>
          </div>
        </div>
      </el-tab-pane>

      <!-- Links Tab -->
      <el-tab-pane label="关联链接" name="links">
        <div class="tab-content">
          <div class="action-bar">
            <el-button type="primary" @click="showLinkDialog()">
              添加链接
            </el-button>
          </div>
          <div class="link-list" v-loading="loadingLinks">
            <div v-if="links.length === 0" class="empty-tip">
              暂无关联链接
            </div>
            <el-table v-else :data="links" style="width: 100%">
              <el-table-column prop="title" label="标题" />
              <el-table-column prop="url" label="链接">
                <template #default="{ row }">
                  <el-link :href="row.url" target="_blank" type="primary">
                    {{ row.url }}
                  </el-link>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="120">
                <template #default="{ row }">
                  <el-button
                    type="primary"
                    size="small"
                    :icon="Edit"
                    circle
                    @click="showLinkDialog(row)"
                  />
                  <el-button
                    type="danger"
                    size="small"
                    :icon="Delete"
                    circle
                    @click="handleDeleteLink(row)"
                  />
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- Text Dialog -->
    <el-dialog
      v-model="textDialogVisible"
      :title="editingText ? '编辑文本' : '添加文本'"
      width="600px"
    >
      <el-form :model="textForm" :rules="textRules" ref="textFormRef" label-width="80px">
        <el-form-item label="标题" prop="title">
          <el-input v-model="textForm.title" placeholder="请输入标题" />
        </el-form-item>
        <el-form-item label="内容" prop="content">
          <el-input
            v-model="textForm.content"
            type="textarea"
            :rows="6"
            placeholder="请输入内容"
          />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="textForm.sort_order" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="textDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveText" :loading="savingText">
          保存
        </el-button>
      </template>
    </el-dialog>

    <!-- Link Dialog -->
    <el-dialog
      v-model="linkDialogVisible"
      :title="editingLink ? '编辑链接' : '添加链接'"
      width="500px"
    >
      <el-form :model="linkForm" :rules="linkRules" ref="linkFormRef" label-width="80px">
        <el-form-item label="标题" prop="title">
          <el-input v-model="linkForm.title" placeholder="请输入标题" />
        </el-form-item>
        <el-form-item label="链接" prop="url">
          <el-input v-model="linkForm.url" placeholder="请输入链接地址" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="linkForm.sort_order" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="linkDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveLink" :loading="savingLink">
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import type { FormInstance, FormRules, UploadRawFile } from 'element-plus'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Delete, Edit } from '@element-plus/icons-vue'
import {
  videoExtensionsApi,
  type VideoImage,
  type VideoText,
  type VideoLink
} from '../api/videoExtensions'

const props = defineProps<{
  videoId: number
}>()

const emit = defineEmits<{
  'update': []
}>()

// Tab state
const activeTab = ref('images')

// Images state
const images = ref<VideoImage[]>([])
const loadingImages = ref(false)
const uploadingImage = ref(false)

// Texts state
const texts = ref<VideoText[]>([])
const loadingTexts = ref(false)
const textDialogVisible = ref(false)
const editingText = ref<VideoText | null>(null)
const textFormRef = ref<FormInstance>()
const savingText = ref(false)
const textForm = reactive({
  title: '',
  content: '',
  sort_order: 0
})
const textRules: FormRules = {
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  content: [{ required: true, message: '请输入内容', trigger: 'blur' }]
}

// Links state
const links = ref<VideoLink[]>([])
const loadingLinks = ref(false)
const linkDialogVisible = ref(false)
const editingLink = ref<VideoLink | null>(null)
const linkFormRef = ref<FormInstance>()
const savingLink = ref(false)
const linkForm = reactive({
  title: '',
  url: '',
  sort_order: 0
})
const linkRules: FormRules = {
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  url: [
    { required: true, message: '请输入链接地址', trigger: 'blur' },
    { type: 'url', message: '请输入有效的链接地址', trigger: 'blur' }
  ]
}

// Load data
const loadImages = async () => {
  loadingImages.value = true
  try {
    const res = await videoExtensionsApi.listImages(props.videoId)
    images.value = res.data
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '加载图片失败')
  } finally {
    loadingImages.value = false
  }
}

const loadTexts = async () => {
  loadingTexts.value = true
  try {
    const res = await videoExtensionsApi.listTexts(props.videoId)
    texts.value = res.data
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '加载文本失败')
  } finally {
    loadingTexts.value = false
  }
}

const loadLinks = async () => {
  loadingLinks.value = true
  try {
    const res = await videoExtensionsApi.listLinks(props.videoId)
    links.value = res.data
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '加载链接失败')
  } finally {
    loadingLinks.value = false
  }
}

// Image handlers
const handleImageBeforeUpload = async (file: UploadRawFile) => {
  uploadingImage.value = true
  try {
    await videoExtensionsApi.uploadImage(props.videoId, file)
    ElMessage.success('上传成功')
    await loadImages()
    emit('update')
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '上传失败')
  } finally {
    uploadingImage.value = false
  }
  return false // Prevent default upload
}

const handleDeleteImage = async (image: VideoImage) => {
  try {
    await ElMessageBox.confirm('确定要删除这张图片吗？', '确认删除', {
      type: 'warning'
    })
    await videoExtensionsApi.deleteImage(props.videoId, image.id)
    ElMessage.success('删除成功')
    await loadImages()
    emit('update')
  } catch (e: any) {
    if (e !== 'cancel') {
      ElMessage.error(e.response?.data?.detail || '删除失败')
    }
  }
}

// Text handlers
const showTextDialog = (text?: VideoText) => {
  editingText.value = text || null
  if (text) {
    textForm.title = text.title
    textForm.content = text.content
    textForm.sort_order = text.sort_order
  } else {
    textForm.title = ''
    textForm.content = ''
    textForm.sort_order = texts.value.length
  }
  textDialogVisible.value = true
}

const handleSaveText = async () => {
  if (!textFormRef.value) return
  await textFormRef.value.validate()

  savingText.value = true
  try {
    if (editingText.value) {
      await videoExtensionsApi.updateText(props.videoId, editingText.value.id, {
        title: textForm.title,
        content: textForm.content,
        sort_order: textForm.sort_order
      })
      ElMessage.success('更新成功')
    } else {
      await videoExtensionsApi.createText(props.videoId, {
        title: textForm.title,
        content: textForm.content,
        sort_order: textForm.sort_order
      })
      ElMessage.success('添加成功')
    }
    textDialogVisible.value = false
    await loadTexts()
    emit('update')
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '保存失败')
  } finally {
    savingText.value = false
  }
}

const handleDeleteText = async (text: VideoText) => {
  try {
    await ElMessageBox.confirm('确定要删除这条文本吗？', '确认删除', {
      type: 'warning'
    })
    await videoExtensionsApi.deleteText(props.videoId, text.id)
    ElMessage.success('删除成功')
    await loadTexts()
    emit('update')
  } catch (e: any) {
    if (e !== 'cancel') {
      ElMessage.error(e.response?.data?.detail || '删除失败')
    }
  }
}

// Link handlers
const showLinkDialog = (link?: VideoLink) => {
  editingLink.value = link || null
  if (link) {
    linkForm.title = link.title
    linkForm.url = link.url
    linkForm.sort_order = link.sort_order
  } else {
    linkForm.title = ''
    linkForm.url = ''
    linkForm.sort_order = links.value.length
  }
  linkDialogVisible.value = true
}

const handleSaveLink = async () => {
  if (!linkFormRef.value) return
  await linkFormRef.value.validate()

  savingLink.value = true
  try {
    if (editingLink.value) {
      await videoExtensionsApi.updateLink(props.videoId, editingLink.value.id, {
        title: linkForm.title,
        url: linkForm.url,
        sort_order: linkForm.sort_order
      })
      ElMessage.success('更新成功')
    } else {
      await videoExtensionsApi.createLink(props.videoId, {
        title: linkForm.title,
        url: linkForm.url,
        sort_order: linkForm.sort_order
      })
      ElMessage.success('添加成功')
    }
    linkDialogVisible.value = false
    await loadLinks()
    emit('update')
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '保存失败')
  } finally {
    savingLink.value = false
  }
}

const handleDeleteLink = async (link: VideoLink) => {
  try {
    await ElMessageBox.confirm('确定要删除这条链接吗？', '确认删除', {
      type: 'warning'
    })
    await videoExtensionsApi.deleteLink(props.videoId, link.id)
    ElMessage.success('删除成功')
    await loadLinks()
    emit('update')
  } catch (e: any) {
    if (e !== 'cancel') {
      ElMessage.error(e.response?.data?.detail || '删除失败')
    }
  }
}

// Watch for tab changes to load data
watch(activeTab, (tab) => {
  if (tab === 'images' && images.value.length === 0) {
    loadImages()
  } else if (tab === 'texts' && texts.value.length === 0) {
    loadTexts()
  } else if (tab === 'links' && links.value.length === 0) {
    loadLinks()
  }
})

// Watch for videoId changes
watch(() => props.videoId, () => {
  images.value = []
  texts.value = []
  links.value = []
  if (activeTab.value === 'images') {
    loadImages()
  } else if (activeTab.value === 'texts') {
    loadTexts()
  } else if (activeTab.value === 'links') {
    loadLinks()
  }
})

// Initial load
onMounted(() => {
  loadImages()
})

// Expose refresh method
defineExpose({
  refresh: () => {
    loadImages()
    loadTexts()
    loadLinks()
  }
})
</script>

<style scoped>
.video-extensions {
  width: 100%;
}

.tab-content {
  padding: 16px 0;
}

.action-bar {
  margin-bottom: 16px;
}

.empty-tip {
  text-align: center;
  color: #909399;
  padding: 40px 0;
}

/* Image styles */
.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 16px;
}

.image-item {
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  aspect-ratio: 1;
}

.image-item :deep(.el-image) {
  width: 100%;
  height: 100%;
}

.image-actions {
  position: absolute;
  top: 8px;
  right: 8px;
  opacity: 0;
  transition: opacity 0.2s;
}

.image-item:hover .image-actions {
  opacity: 1;
}

/* Text styles */
.text-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding-right: 16px;
}

.text-actions {
  display: flex;
  gap: 8px;
}

.text-content {
  white-space: pre-wrap;
  color: #606266;
  line-height: 1.6;
}

/* Link styles */
.link-list :deep(.el-table) {
  margin-top: 0;
}
</style>
