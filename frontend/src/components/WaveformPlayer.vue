<template>
  <div class="waveform-player">
    <!-- Display Mode Toggle -->
    <div class="display-mode-toggle">
      <el-radio-group v-model="displayMode" size="small">
        <el-radio-button value="waveform">波形可视化</el-radio-button>
        <el-radio-button value="cover">封面显示</el-radio-button>
      </el-radio-group>
    </div>

    <!-- Waveform Mode -->
    <div v-show="displayMode === 'waveform'" class="waveform-container">
      <div ref="waveformRef" class="waveform"></div>
      <div class="waveform-controls">
        <el-button
          :icon="isPlaying ? Pause : VideoPlay"
          @click="togglePlay"
          circle
          type="primary"
        />
        <span class="time-display">{{ currentTime }} / {{ duration }}</span>
        <el-slider
          v-model="volume"
          :min="0"
          :max="100"
          style="width: 100px; margin-left: 20px;"
          @input="handleVolumeChange"
        />
      </div>
    </div>

    <!-- Cover Mode -->
    <div v-show="displayMode === 'cover'" class="cover-container">
      <div class="audio-cover">
        <img v-if="cover" :src="cover" alt="封面" />
        <el-icon v-else :size="64" class="default-icon"><Headset /></el-icon>
      </div>
      <audio ref="audioRef" :src="audioUrl" controls class="audio-player"></audio>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import WaveSurfer from 'wavesurfer.js'
import { VideoPlay, Pause, Headset } from '@element-plus/icons-vue'

interface Props {
  audioUrl: string
  cover?: string
}

const props = defineProps<Props>()

const displayMode = ref<'waveform' | 'cover'>('waveform')
const waveformRef = ref<HTMLDivElement>()
const audioRef = ref<HTMLAudioElement>()
const isPlaying = ref(false)
const currentTime = ref('0:00')
const duration = ref('0:00')
const volume = ref(50)

let wavesurfer: WaveSurfer | null = null

const formatTime = (seconds: number): string => {
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return `${m}:${s.toString().padStart(2, '0')}`
}

const initWaveSurfer = () => {
  if (!waveformRef.value) return

  try {
    wavesurfer = WaveSurfer.create({
      container: waveformRef.value,
      waveColor: '#667eea',
      progressColor: '#764ba2',
      cursorColor: '#E94560',
      barWidth: 2,
      barRadius: 3,
      height: 128,
      normalize: true,
      backend: 'WebAudio'
    })

    wavesurfer.load(props.audioUrl)

    wavesurfer.on('play', () => {
      isPlaying.value = true
    })

    wavesurfer.on('pause', () => {
      isPlaying.value = false
    })

    wavesurfer.on('audioprocess', (time) => {
      currentTime.value = formatTime(time)
    })

    wavesurfer.on('ready', () => {
      duration.value = formatTime(wavesurfer!.getDuration())
      wavesurfer!.setVolume(volume.value / 100)
    })

    wavesurfer.on('error', (error) => {
      console.error('WaveSurfer error:', error)
    })
  } catch (error) {
    console.error('Failed to initialize WaveSurfer:', error)
  }
}

const togglePlay = () => {
  if (wavesurfer) {
    wavesurfer.playPause()
  }
}

const handleVolumeChange = (value: number) => {
  if (wavesurfer) {
    wavesurfer.setVolume(value / 100)
  }
}

onMounted(() => {
  if (displayMode.value === 'waveform') {
    initWaveSurfer()
  }
})

onUnmounted(() => {
  if (wavesurfer) {
    wavesurfer.destroy()
    wavesurfer = null
  }
})

// Watch display mode changes
watch(displayMode, (newMode) => {
  if (newMode === 'waveform' && !wavesurfer) {
    // Initialize waveform when switching to waveform mode
    setTimeout(() => {
      initWaveSurfer()
    }, 100)
  } else if (newMode === 'cover' && wavesurfer) {
    // Pause waveform when switching to cover mode
    if (isPlaying.value) {
      wavesurfer.pause()
    }
  }
})
</script>

<style scoped>
.waveform-player {
  width: 100%;
  padding: 20px;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-radius: 8px;
}

.display-mode-toggle {
  margin-bottom: 20px;
  text-align: center;
}

.waveform-container {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.waveform {
  margin-bottom: 20px;
}

.waveform-controls {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
}

.time-display {
  font-size: 14px;
  font-weight: 500;
  color: #606266;
  min-width: 100px;
  text-align: center;
}

.cover-container {
  background: white;
  border-radius: 8px;
  padding: 30px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.audio-cover {
  margin-bottom: 20px;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 200px;
}

.audio-cover img {
  max-width: 300px;
  max-height: 300px;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.default-icon {
  color: #909399;
}

.audio-player {
  width: 100%;
  max-width: 500px;
  margin: 0 auto;
}

/* Waveform gradient styling */
:deep(.wavesurfer-region) {
  background: rgba(102, 126, 234, 0.1);
}

/* Smooth transitions */
.waveform-container,
.cover-container {
  transition: all 0.3s ease;
}
</style>
