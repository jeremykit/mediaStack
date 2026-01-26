# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MediaStack is a live streaming recording and video-on-demand (VOD) system. It supports recording live streams from RTMP/RTSP/HLS sources, managing recorded videos, uploading media files, and providing VOD playback with access control via viewing codes.

**Tech Stack:**
- Backend: FastAPI + SQLAlchemy (async) + SQLite
- Frontend: Vue 3 + Element Plus + TypeScript + Vite
- Media Processing: FFmpeg (recording, audio extraction)
- VOD Delivery: nginx-vod-module (MP4 to HLS conversion)

## Development Commands

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The backend runs on `http://localhost:8000` by default. API docs available at `/docs`.

**Environment Configuration:**
- Copy `backend/.env.example` to `backend/.env` for local development
- Key settings in `backend/app/config.py`: database URL, JWT secret, storage path, admin credentials

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend dev server runs on `http://localhost:5173` by default.

**Build for production:**
```bash
cd frontend
npm run build
```

### Docker Deployment

```bash
docker-compose up -d
```

Access the application at `http://localhost`.

## Architecture

### Backend Structure

**Core Components:**
- `app/main.py` - FastAPI application entry point with lifespan management (DB init, scheduler init, admin creation)
- `app/config.py` - Pydantic settings with environment variable support
- `app/database.py` - Async SQLAlchemy engine and session management

**API Layer (`app/api/`):**
- `auth.py` - JWT authentication (login, token generation)
- `sources.py` - Live source management (CRUD operations)
- `schedules.py` - Scheduled recording management (cron-based)
- `tasks.py` - Recording task management (start/stop recording)
- `videos.py` - Video file management (list, upload, metadata)
- `system.py` - System monitoring (CPU, memory, disk, bandwidth)
- `deps.py` - Dependency injection (authentication, DB session)

**Data Models (`app/models/`):**
- `admin.py` - Admin user model
- `source.py` - Live source configuration (name, URL, protocol)
- `schedule.py` - Scheduled recording plans (cron expression, source reference)
- `task.py` - Recording task tracking (status, file path, timestamps)
- `video.py` - Video file metadata (title, description, category, tags)

**Services (`app/services/`):**
- `recorder.py` - FFmpeg-based recording service (start/stop recording, process management)
- `scheduler.py` - APScheduler integration (cron job management, schedule persistence)
- `stream_checker.py` - Stream availability checking

**Key Patterns:**
- All database operations use async SQLAlchemy with `AsyncSession`
- Recording tasks run as background asyncio tasks spawning FFmpeg subprocesses
- Scheduler uses APScheduler with SQLAlchemy job store for persistence
- JWT authentication with dependency injection via `get_current_user`

### Frontend Structure

**Entry Point:**
- `src/main.ts` - Vue app initialization with Element Plus, Pinia, and Router

**Key Directories:**
- `src/api/` - Axios-based API client modules
- `src/views/` - Page components (admin dashboard, video player, etc.)
- `src/components/` - Reusable UI components
- `src/stores/` - Pinia state management stores
- `src/router/` - Vue Router configuration

### Data Flow

**Recording Workflow:**
1. Admin creates a live source via `sources.py` API
2. Admin creates a schedule (optional) or manually starts recording via `tasks.py` API
3. `RecorderService.start_recording()` creates a `RecordTask` and spawns FFmpeg subprocess
4. FFmpeg records stream to MP4 file in `storage_path`
5. On completion, `VideoFile` record is created with metadata
6. Admin can edit video metadata and publish for VOD playback

**Scheduled Recording:**
1. `schedules.py` API creates a `Schedule` with cron expression
2. `scheduler.py` registers APScheduler job
3. At scheduled time, `scheduled_recording_job()` checks if source is already recording
4. If not, starts recording via `RecorderService.start_recording()`

**VOD Playback:**
1. Frontend requests video list from `videos.py` API
2. nginx-vod-module serves MP4 files as HLS streams
3. Frontend uses hls.js to play HLS streams in browser

## Important Implementation Details

**FFmpeg Recording:**
- Command: `ffmpeg -y -i <url> -c copy -f mp4 -movflags +faststart <output>`
- Process management in `RecorderService._processes` dict (task_id -> Process)
- Graceful shutdown: SIGTERM with 5s timeout, then SIGKILL
- Duration extraction via ffprobe after recording completes

**Task Status Flow:**
- `pending` → `recording` → `completed`/`failed`/`interrupted`
- Status 255 from FFmpeg indicates user interruption (SIGTERM)

**Database Initialization:**
- Alembic migrations run on startup via `run_migrations()` in `main.py`
- `init_db()` creates any remaining tables via `Base.metadata.create_all`
- `create_initial_admin()` ensures default admin user exists

**Scheduler Persistence:**
- APScheduler uses SQLAlchemy job store (sync SQLite URL)
- Jobs survive application restarts
- Active schedules are reloaded on startup in `init_scheduler()`

**CORS Configuration:**
- Default origins: `http://localhost:5173`, `http://localhost:3000`
- Configure via `CORS_ORIGINS` environment variable (comma-separated)

## Common Workflows

**Adding a New API Endpoint:**
1. Define Pydantic schemas in `app/schemas/`
2. Create router in `app/api/` with endpoint handlers
3. Include router in `app/main.py`
4. Add corresponding API client function in `frontend/src/api/`

**Adding a New Database Model:**
1. Create model class in `app/models/` inheriting from `Base`
2. Import model in `app/models/__init__.py`
3. Generate migration: `cd backend && alembic revision --autogenerate -m "description"`
4. Review and adjust the generated migration file in `alembic/versions/`
5. Migrations run automatically on startup, or manually via `alembic upgrade head`

**Database Migrations (Alembic):**
- Alembic is used for database schema migrations
- Migrations run automatically on application startup via `run_migrations()` in `main.py`
- Migration files are in `backend/alembic/versions/`
- To create a new migration: `cd backend && alembic revision --autogenerate -m "description"`
- To manually run migrations: `cd backend && alembic upgrade head`
- To rollback: `cd backend && alembic downgrade -1`
- SQLite requires `render_as_batch=True` for ALTER TABLE operations (configured in `env.py`)

**Modifying Recording Logic:**
- Core logic in `RecorderService` class (`app/services/recorder.py`)
- FFmpeg command construction in `_run_ffmpeg()` method
- Process lifecycle management in `start_recording()` and `stop_recording()`

## Testing

Backend tests use pytest with async support:
```bash
cd backend
pytest
```

Test configuration in `backend/pytest.ini`. Test fixtures in `backend/tests/conftest.py`.

## Security Notes

- JWT tokens expire after 24 hours (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`)
- Admin password hashed with bcrypt
- Default credentials: `admin/admin123` (change in production via environment variables)
- Viewing codes control access to video categories (not yet implemented)

## External Dependencies

**Required System Tools:**
- FFmpeg 5.0+ (for recording and media processing)
- FFprobe (bundled with FFmpeg, for duration extraction)
- nginx with nginx-vod-module (for production VOD delivery)

**Python Dependencies:**
- FastAPI for async web framework
- SQLAlchemy 2.0+ with aiosqlite for async database
- Alembic for database migrations
- APScheduler for cron-based scheduling
- python-jose for JWT handling
- passlib with bcrypt for password hashing
- psutil for system monitoring

**Frontend Dependencies:**
- Vue 3 with Composition API
- Element Plus for UI components
- hls.js for HLS playback
- Pinia for state management
- Vue Router for routing
