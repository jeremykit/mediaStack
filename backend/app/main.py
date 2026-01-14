from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import init_db, async_session
from app.api import auth, sources, tasks, schedules, videos
from app.services.scheduler import init_scheduler, shutdown_scheduler
from app.init_admin import create_initial_admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    settings.storage_path.mkdir(parents=True, exist_ok=True)
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
