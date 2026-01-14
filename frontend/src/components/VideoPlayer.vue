<template>
  <div class="video-player">
    <video ref="videoRef" controls class="player"></video>
    <div v-if="error" class="error">{{ error }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import Hls from 'hls.js'

const props = defineProps<{ src: string }>()

const videoRef = ref<HTMLVideoElement>()
const error = ref('')
let hls: Hls | null = null

const initPlayer = () => {
  if (!videoRef.value || !props.src) return

  error.value = ''

  if (Hls.isSupported()) {
    hls = new Hls()
    hls.on(Hls.Events.ERROR, (_, data) => {
      if (data.fatal) {
        error.value = '视频加载失败'
        hls?.destroy()
        hls = null
      }
    })
    hls.loadSource(props.src)
    hls.attachMedia(videoRef.value)
  } else if (videoRef.value.canPlayType('application/vnd.apple.mpegurl')) {
    videoRef.value.src = props.src
  }
}

const destroyPlayer = () => {
  if (hls) {
    hls.destroy()
    hls = null
  }
}

watch(() => props.src, () => {
  destroyPlayer()
  initPlayer()
})

onMounted(initPlayer)
onUnmounted(destroyPlayer)
</script>

<style scoped>
.video-player {
  width: 100%;
  background: #000;
  border-radius: 8px;
  overflow: hidden;
}
.player {
  width: 100%;
  aspect-ratio: 16/9;
}
.error {
  color: #f56c6c;
  text-align: center;
  padding: 20px;
}
</style>
