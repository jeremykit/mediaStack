from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pathlib import Path
import logging
import os

# Set timezone to Asia/Shanghai (Beijing Time)
os.environ['TZ'] = 'Asia/Shanghai'

# Configure logging
import sys
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    stream=sys.stdout,
    force=True
)

from app.config import settings
from app.database import init_db, async_session, ensure_default_category
from app.api import auth, sources, tasks, schedules, videos, system, categories, tags, view_codes, upload, video_extensions, audio, thumbnail, video_trim, websocket
from app.services.scheduler import init_scheduler, shutdown_scheduler
from app.services.status_monitor import status_monitor
from app.init_admin import create_initial_admin

logger = logging.getLogger(__name__)


def run_migrations():
    """Run Alembic migrations on startup."""
    from alembic.config import Config
    from alembic import command

    alembic_cfg = Config(str(Path(__file__).parent.parent / "alembic.ini"))
    alembic_cfg.set_main_option("script_location", str(Path(__file__).parent.parent / "alembic"))

    try:
        command.upgrade(alembic_cfg, "head")
        logger.info("Database migrations completed successfully")
    except Exception as e:
        logger.error(f"Failed to run database migrations: {e}")
        raise


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

    # Run Alembic migrations before initializing the database
    run_migrations()

    await init_db()
    async with async_session() as db:
        await create_initial_admin(db)
    await ensure_default_category()
    await init_scheduler()
    await status_monitor.start(async_session)
    yield
    # Shutdown
    await status_monitor.stop()
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
app.include_router(websocket.router)
