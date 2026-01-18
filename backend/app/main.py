from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pathlib import Path

from app.config import settings
from app.database import init_db, async_session
from app.api import auth, sources, tasks, schedules, videos, system, categories, tags, view_codes, upload, video_extensions, audio, thumbnail, video_trim
from app.services.scheduler import init_scheduler, shutdown_scheduler
from app.init_admin import create_initial_admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    # Create necessary directories
    settings.storage_path.mkdir(parents=True, exist_ok=True)

    # Create temp directory for uploads
    (settings.storage_path / "temp").mkdir(parents=True, exist_ok=True)

    # Create audio directory for extracted audio files
    (settings.storage_path / "audio").mkdir(parents=True, exist_ok=True)

    # Create thumbnails directory for video thumbnails
    (settings.storage_path / "thumbnails").mkdir(parents=True, exist_ok=True)

    # Create database directory
    db_path = Path(settings.database_url.replace("sqlite+aiosqlite:///", ""))
    db_path.parent.mkdir(parents=True, exist_ok=True)

    await init_db()
    async with async_session() as db:
        await create_initial_admin(db)
    await init_scheduler()
    yield
    # Shutdown
    shutdown_scheduler()


app = FastAPI(
    title=settings.app_name,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

app.include_router(auth.router)
app.include_router(sources.router)
app.include_router(tasks.router)
app.include_router(schedules.router)
app.include_router(videos.router)
app.include_router(system.router)
app.include_router(categories.router)
app.include_router(tags.router)
app.include_router(view_codes.router)
app.include_router(upload.router)
app.include_router(video_extensions.router)
app.include_router(audio.router)
app.include_router(thumbnail.router)
app.include_router(video_trim.router)
