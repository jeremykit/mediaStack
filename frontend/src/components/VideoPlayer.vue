<template>
  <div class="video-player">
    <video ref="videoRef" controls class="player"></video>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import Hls from 'hls.js'

const props = defineProps<{ src: string }>()
const videoRef = ref<HTMLVideoElement>()
let hls: Hls | null = null

const initPlayer = () => {
  if (!videoRef.value || !props.src) return
  if (Hls.isSupported()) {
    hls = new Hls()
    hls.loadSource(props.src)
    hls.attachMedia(videoRef.value)
  } else if (videoRef.value.canPlayType('application/vnd.apple.mpegurl')) {
    videoRef.value.src = props.src
  }
}

const destroyPlayer = () => {
  if (hls) { hls.destroy(); hls = null }
}

watch(() => props.src, () => { destroyPlayer(); initPlayer() })
onMounted(initPlayer)
onUnmounted(destroyPlayer)
</script>

<style scoped>
.video-player { width: 100%; background: #000; border-radius: 8px; overflow: hidden; }
.player { width: 100%; aspect-ratio: 16/9; }
</style>
