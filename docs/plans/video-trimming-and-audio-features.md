# MediaStack Video Trimming and Audio Features Implementation Plan

## Overview

This plan implements four major features based on the updated requirements document:

1. **Video Trimming Module** - Trim recorded videos with optional audio extraction
2. **Audio Waveform Visualization** - Add wavesurfer.js for audio playback
3. **Simplified Audio Format Support** - Support only MP3/M4A with auto-detection
4. **Enhanced Audio Extraction** - Different bitrates for different scenarios (192kbps for trimming, 128kbps for regular downloads)

## User Clarifications

Based on user feedback:
- **Trimming Scope**: Only recorded videos (source_type='recorded') can be trimmed, not uploaded videos
- **Waveform Visualization**: Only for pure audio files (file_type='audio'), not for video files in audio mode
- **Trimmed Video Status**: After trimming, reset video status to 'pending' (待审核) for re-approval

## Architecture Approach

Following existing MediaStack patterns:
- **Task-based processing** (similar to AudioExtractorService)
- **Async FFmpeg subprocess management** with graceful shutdown
- **RESTful API design** with Pydantic schemas
- **Vue 3 Composition API** with Element Plus components
- **File naming conventions**: `{type}_YYYYMMDD_HHmmss_{id}.{ext}`

---

## Backend Implementation

### 1. Database Schema

**New Model: VideoTrimTask**

Create `backend/app/models/video_trim_task.py`:

```python
class TrimStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"

class VideoTrimTask(Base):
    __tablename__ = "video_trim_tasks"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("video_files.id", ondelete="CASCADE"), nullable=False)
    status = Column(Enum(TrimStatus), default=TrimStatus.pending, index=True)

    # Trim parameters
    start_time = Column(Integer, nullable=False)  # seconds
    end_time = Column(Integer, nullable=False)    # seconds

    # Options
    extract_audio = Column(Boolean, default=False)
    keep_original = Column(Boolean, default=False)
    audio_bitrate = Column(String(8), default="192k")

    # Output paths
    trimmed_video_path = Column(String(512), nullable=True)
    extracted_audio_path = Column(String(512), nullable=True)

    # Metadata
    created_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)

    # Relationships
    video = relationship("VideoFile", back_populates="trim_tasks")
```

**Update VideoFile Model** (`backend/app/models/video.py`):
- Add relationship: `trim_tasks = relationship("VideoTrimTask", back_populates="video", cascade="all, delete-orphan")`

**Update Models Init** (`backend/app/models/__init__.py`):
- Import VideoTrimTask and TrimStatus

### 2. Service Layer: VideoTrimmerService

Create `backend/app/services/video_trimmer.py`:

**Key Methods:**

1. **start_trimming(video_id, start_time, end_time, extract_audio, keep_original, db)**
   - Validate video exists and is a recorded video (source_type='recorded')
   - Validate times are valid (start < end, within duration)
   - Check for existing processing tasks
   - Create VideoTrimTask record
   - Generate output filenames: `trimmed_YYYYMMDD_HHmmss_{video_id}.mp4`
   - Start background task with `asyncio.create_task`
   - Return task immediately (non-blocking)

2. **_run_ffmpeg_trim(task_id, input_path, output_path, start_time, end_time)**
   - FFmpeg command: `ffmpeg -y -ss {start} -to {end} -i {input} -c copy -avoid_negative_ts make_zero -f mp4 -movflags +faststart {output}`
   - Track process in `_processes` dict
   - Update task status: pending → processing → completed/failed
   - Handle graceful shutdown (SIGTERM with 5s timeout, then SIGKILL)

3. **_extract_audio_from_trim(task_id, trimmed_video_path, audio_output_path)**
   - FFmpeg command: `ffmpeg -y -i {input} -vn -acodec libmp3lame -ab 192k -ar 44100 -ac 2 {output}`
   - Use 192kbps bitrate for trim extraction (per requirements)
   - Run after video trim completes

4. **_handle_original_file(video_id, keep_original, db)**
   - If keep_original=False: Delete original file and update VideoFile.file_path to trimmed version
   - If keep_original=True: Keep both files, update VideoFile to point to trimmed version
   - Reset video status to 'pending' (待审核) after trimming for re-approval

5. **get_task(video_id, db)** - Get latest trim task for video
6. **get_task_by_id(task_id, db)** - Get specific task for status polling
7. **cancel_task(task_id, db)** - Terminate FFmpeg process and clean up

**FFmpeg Commands:**

```bash
# Video Trimming (fast, no re-encoding)
ffmpeg -y -ss {start_seconds} -to {end_seconds} -i {input_video} \
  -c copy -avoid_negative_ts make_zero -f mp4 -movflags +faststart {output_video}

# Audio Extraction (192kbps for trim)
ffmpeg -y -i {trimmed_video} -vn -acodec libmp3lame -ab 192k \
  -ar 44100 -ac 2 {output_audio}
```

**File Storage:**
- Trimmed videos: `./data/videos/trimmed_YYYYMMDD_HHmmss_{video_id}.mp4`
- Extracted audio: `./data/videos/audio/audio_YYYYMMDD_HHmmss_{video_id}.mp3`

### 3. API Endpoints

Create `backend/app/api/video_trim.py`:

**Endpoints:**

1. **POST /api/videos/{video_id}/trim**
   - Request: `TrimVideoRequest(start_time, end_time, extract_audio, keep_original)`
   - Response: `TrimTaskResponse(task_id, status, created_at)`
   - Auth: Admin only
   - Creates trim task and returns immediately

2. **GET /api/videos/{video_id}/trim/tasks**
   - Response: `List[TrimTaskResponse]`
   - Auth: Admin only
   - Returns all trim tasks for a video

3. **GET /api/videos/trim/tasks/{task_id}**
   - Response: `TrimTaskDetailResponse`
   - Auth: Admin only
   - For polling task status

4. **DELETE /api/videos/trim/tasks/{task_id}**
   - Auth: Admin only
   - Cancel ongoing trim task

**Schemas** (`backend/app/schemas/video_trim.py`):

```python
class TrimVideoRequest(BaseModel):
    start_time: int = Field(..., ge=0, description="Start time in seconds")
    end_time: int = Field(..., gt=0, description="End time in seconds")
    extract_audio: bool = Field(default=False)
    keep_original: bool = Field(default=False)

class TrimTaskResponse(BaseModel):
    id: int
    video_id: int
    status: str
    start_time: int
    end_time: int
    extract_audio: bool
    keep_original: bool
    trimmed_video_path: Optional[str]
    extracted_audio_path: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]
    error_message: Optional[str]
```

### 4. Audio Format Simplification

**Update** `backend/app/services/uploader.py`:
- Change `ALLOWED_AUDIO_EXTENSIONS` from `{'.mp3', '.wav', '.aac', '.flac'}` to `{'.mp3', '.m4a'}`
- Auto-detection already implemented (checks extension and sets file_type)

### 5. Main App Integration

**Update** `backend/app/main.py`:
- Import video_trim router
- Add `app.include_router(video_trim.router)`

---

## Frontend Implementation

### 1. API Client Module

Create `frontend/src/api/videoTrim.ts`:

```typescript
export interface TrimVideoRequest {
  start_time: number
  end_time: number
  extract_audio: boolean
  keep_original: boolean
}

export interface TrimTask {
  id: number
  video_id: number
  status: 'pending' | 'processing' | 'completed' | 'failed'
  start_time: number
  end_time: number
  extract_audio: boolean
  keep_original: boolean
  trimmed_video_path: string | null
  extracted_audio_path: string | null
  created_at: string
  completed_at: string | null
  error_message: string | null
}

export const videoTrimApi = {
  trimVideo: (videoId: number, data: TrimVideoRequest) =>
    api.post(`/api/videos/${videoId}/trim`, data),

  getTrimTasks: (videoId: number) =>
    api.get<TrimTask[]>(`/api/videos/${videoId}/trim/tasks`),

  getTrimTask: (taskId: number) =>
    api.get<TrimTask>(`/api/videos/trim/tasks/${taskId}`),

  cancelTrimTask: (taskId: number) =>
    api.delete(`/api/videos/trim/tasks/${taskId}`)
}
```

### 2. Video Trimming Dialog Component

Create `frontend/src/components/VideoTrimDialog.vue`:

**Features:**
- Video preview player (HTML5 video element)
- Timeline with Element Plus slider (range mode)
- Time input fields (HH:MM:SS format)
- Real-time duration calculation
- "Extract Audio" checkbox
- "Keep Original File" checkbox (default unchecked)
- Submit button with loading state
- Task status polling (every 2 seconds)

**UI Layout:**
```
┌─────────────────────────────────────┐
│  Video Preview Player               │
│  [================================]  │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│  Timeline Slider                    │
│  |=====[Selected Range]=====|       │
│  0:00                      10:30    │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│  Start Time: [00:01:30]             │
│  End Time:   [00:08:45]             │
│  Duration:   00:07:15               │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│  ☑ Extract Audio (192kbps MP3)      │
│  ☐ Keep Original File               │
└─────────────────────────────────────┘
```

**Implementation:**
- Use `el-dialog` for modal
- Use `el-slider` with `range` prop for timeline
- Convert seconds ↔ HH:MM:SS format
- Validate: start < end, both within video duration
- Poll task status after submission
- Show progress: pending → processing → completed/failed
- On completion: emit success event and close dialog

### 3. Audio Waveform Visualization

**Install Dependency:**
Add to `frontend/package.json`: `"wavesurfer.js": "^7.0.0"`

**Create Component** `frontend/src/components/WaveformPlayer.vue`:

```vue
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
        <el-button :icon="isPlaying ? Pause : Play" @click="togglePlay" circle />
        <span class="time-display">{{ currentTime }} / {{ duration }}</span>
      </div>
    </div>

    <!-- Cover Mode -->
    <div v-show="displayMode === 'cover'" class="cover-container">
      <div class="audio-cover">
        <img v-if="cover" :src="cover" alt="封面" />
        <el-icon v-else :size="64"><Headset /></el-icon>
      </div>
      <audio ref="audioRef" :src="audioUrl" controls class="audio-player"></audio>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import WaveSurfer from 'wavesurfer.js'
import { Play, Pause, Headset } from '@element-plus/icons-vue'

const props = defineProps<{
  audioUrl: string
  cover?: string
}>()

const displayMode = ref<'waveform' | 'cover'>('waveform')
const waveformRef = ref<HTMLDivElement>()
const isPlaying = ref(false)
const currentTime = ref('0:00')
const duration = ref('0:00')

let wavesurfer: WaveSurfer | null = null

onMounted(() => {
  if (waveformRef.value) {
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

    wavesurfer.on('play', () => { isPlaying.value = true })
    wavesurfer.on('pause', () => { isPlaying.value = false })
    wavesurfer.on('audioprocess', (time) => {
      currentTime.value = formatTime(time)
    })
    wavesurfer.on('ready', () => {
      duration.value = formatTime(wavesurfer!.getDuration())
    })
  }
})

onUnmounted(() => {
  wavesurfer?.destroy()
})

const togglePlay = () => {
  wavesurfer?.playPause()
}

const formatTime = (seconds: number) => {
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return `${m}:${s.toString().padStart(2, '0')}`
}
</script>
```

**Styling:**
- Match existing gradient theme: `linear-gradient(135deg, #667eea 0%, #764ba2 100%)`
- Responsive design for mobile/desktop
- Smooth transitions between display modes

### 4. Integration Points

**Update** `frontend/src/views/VideoDetail.vue`:
- Replace audio player section with `<WaveformPlayer>` component (only for file_type='audio')
- Keep existing HTML5 audio player for video files in audio mode
- Import WaveformPlayer component
- Pass `audioDownloadUrl` and `video.thumbnail` as props
- Conditional rendering: Use WaveformPlayer only when `video.file_type === 'audio'`

**Update** `frontend/src/views/admin/Recordings.vue`:
- Add "裁剪" button in table actions (only for recorded videos: source_type='recorded' AND file_type='video')
- Add `<VideoTrimDialog>` component
- Implement `handleTrim()` and `handleTrimSuccess()` methods
- Import VideoTrimDialog component

---

## Critical Files to Modify

### Backend (New Files)
1. `backend/app/models/video_trim_task.py` - VideoTrimTask model
2. `backend/app/services/video_trimmer.py` - Core trimming service
3. `backend/app/api/video_trim.py` - API endpoints
4. `backend/app/schemas/video_trim.py` - Request/response schemas

### Backend (Modifications)
5. `backend/app/models/video.py` - Add trim_tasks relationship
6. `backend/app/models/__init__.py` - Import new models
7. `backend/app/main.py` - Include video_trim router
8. `backend/app/services/uploader.py` - Update ALLOWED_AUDIO_EXTENSIONS

### Frontend (New Files)
9. `frontend/src/api/videoTrim.ts` - API client
10. `frontend/src/components/VideoTrimDialog.vue` - Trim dialog
11. `frontend/src/components/WaveformPlayer.vue` - Waveform player

### Frontend (Modifications)
12. `frontend/src/views/VideoDetail.vue` - Integrate WaveformPlayer
13. `frontend/src/views/admin/Recordings.vue` - Add trim button and dialog
14. `frontend/package.json` - Add wavesurfer.js dependency

---

## Implementation Sequence

### Phase 1: Backend Core
1. Create VideoTrimTask model and update VideoFile relationship
2. Implement VideoTrimmerService with FFmpeg commands
3. Create API endpoints and schemas
4. Update main.py to include router
5. Test API endpoints manually

### Phase 2: Backend Audio Updates
1. Update ALLOWED_AUDIO_EXTENSIONS in uploader.py
2. Verify audio auto-detection works for MP3/M4A
3. Test audio file uploads

### Phase 3: Frontend Trimming
1. Create videoTrim API client module
2. Implement VideoTrimDialog component
3. Add trim button to Recordings.vue
4. Test trim workflow end-to-end

### Phase 4: Frontend Audio Waveform
1. Install wavesurfer.js dependency
2. Create WaveformPlayer component
3. Integrate into VideoDetail.vue
4. Test audio playback with waveform

### Phase 5: Testing & Polish
1. Integration testing all features
2. Test with various video/audio files
3. UI/UX refinements
4. Bug fixes

---

## Verification Steps

### Backend Verification
1. Start backend: `cd backend && uvicorn app.main:app --reload`
2. Check API docs: `http://localhost:8000/docs`
3. Verify new endpoints appear: `/api/videos/{video_id}/trim`
4. Test trim API with Postman:
   - POST trim request with valid times on a recorded video
   - Verify uploaded videos are rejected (source_type validation)
   - GET task status (should show "processing")
   - Wait for completion
   - Verify trimmed file exists in `./data/videos/`
   - Verify video status is reset to 'pending'
5. Test audio extraction option
6. Test keep_original flag (both true and false)
7. Upload MP3 and M4A files, verify auto-detection

### Frontend Verification
1. Start frontend: `cd frontend && npm run dev`
2. Login to admin panel
3. Navigate to Recordings page
4. Verify "裁剪" button only appears for recorded videos (not uploaded videos)
5. Click "裁剪" button on a recorded video
6. Verify trim dialog opens with video preview
7. Test timeline slider and time inputs
8. Submit trim request
9. Verify task status updates (pending → processing → completed)
10. Verify trimmed video status is reset to 'pending' (待审核)
11. Upload MP3/M4A files, verify they appear as audio type
12. Navigate to audio file detail page
13. Verify waveform visualization loads and plays (only for audio files)
14. Test display mode toggle (waveform ↔ cover)
15. Navigate to video file detail page, switch to audio mode
16. Verify it uses simple HTML5 audio player (not waveform)

### End-to-End Testing
1. Record a live stream
2. Verify "裁剪" button appears for recorded video
3. Trim the recorded video (extract audio, keep original)
4. Verify trimmed video status is reset to 'pending'
5. Approve trimmed video
6. Verify trimmed video plays correctly
7. Verify extracted audio file has waveform visualization
8. Test audio download
9. Trim again (don't keep original)
10. Verify original file is deleted and status reset to 'pending'
11. Upload MP3 file
12. Verify it auto-detects as audio type
13. Verify waveform visualization works for uploaded audio
14. Upload MP4 video file
15. Verify "裁剪" button does NOT appear (uploaded videos can't be trimmed)
16. Switch to audio mode on uploaded video
17. Verify it uses simple HTML5 audio player (not waveform)

---

## Risk Mitigation

### FFmpeg Process Management
- Use existing graceful shutdown pattern (SIGTERM → SIGKILL)
- Track all processes in `_processes` dict
- Implement timeout for trim operations (30 minutes max)
- Clean up processes on application shutdown

### Disk Space Management
- Check available disk space before starting trim
- Default to deleting original file (keep_original=False)
- Implement cleanup on failed operations
- Monitor disk space in system status

### Concurrent Operations
- Check for existing processing tasks before starting new one
- Prevent multiple trim operations on same video simultaneously
- Queue trim requests if video is already being processed

### Waveform Performance
- Use wavesurfer.js backend: 'WebAudio' for better performance
- Implement lazy loading (only load when audio mode selected)
- Add file size warning for very large files (>100MB)
- Provide fallback to simple audio player if waveform fails

### File Naming Collisions
- Use timestamp + video_id in filename (unique)
- Check file existence before writing
- Add random suffix if collision detected

---

## Notes

- Database migration: New VideoTrimTask table will be created automatically on startup (SQLite auto-creation via `Base.metadata.create_all()`)
- Audio bitrate: 192kbps for trim extraction, 128kbps for regular downloads (as per requirements)
- File storage: All files in `./data/videos/` directory, audio in `./data/videos/audio/` subdirectory
- FFmpeg commands use `-c copy` for fast trimming without re-encoding
- Waveform visualization adds ~100KB to frontend bundle size
- Task-based processing allows non-blocking API responses and progress tracking
- **Trimming restriction**: Only recorded videos (source_type='recorded') can be trimmed
- **Waveform restriction**: Only pure audio files (file_type='audio') show waveform visualization
- **Status reset**: Trimmed videos are reset to 'pending' status and require re-approval before publishing
