import asyncio
import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import LiveSource
from app.services.stream_checker import check_stream_status

logger = logging.getLogger(__name__)

class StatusMonitor:
    def __init__(self):
        self._task = None
        self._running = False

    async def start(self, db_session_factory):
        """Start the background monitoring task."""
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._monitor_loop(db_session_factory))
        logger.info("Status monitor started")

    async def stop(self):
        """Stop the background monitoring task."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Status monitor stopped")

    async def _monitor_loop(self, db_session_factory):
        """Main monitoring loop that checks all sources every 30 seconds."""
        while self._running:
            try:
                async with db_session_factory() as db:
                    await self._check_all_sources(db)
            except Exception as e:
                logger.error(f"Error in status monitor: {e}")

            await asyncio.sleep(30)

    async def _check_all_sources(self, db: AsyncSession):
        """Check status of all active sources."""
        result = await db.execute(select(LiveSource).where(LiveSource.is_active == True))
        sources = result.scalars().all()

        for source in sources:
            try:
                online, _ = await check_stream_status(source.url, source.protocol.value)
                source.is_online = online
                source.last_check_time = datetime.now()
            except Exception as e:
                logger.error(f"Error checking source {source.id}: {e}")
                source.is_online = False
                source.last_check_time = datetime.now()

        await db.commit()

status_monitor = StatusMonitor()
