import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.models import LiveSource, RecordTask, VideoFile, TaskStatus


class RecorderService:
    _processes: dict[int, asyncio.subprocess.Process] = {}

    @classmethod
    async def start_recording(cls, source_id: int, db: AsyncSession) -> RecordTask:
        result = await db.execute(
            select(RecordTask).where(
                RecordTask.source_id == source_id,
                RecordTask.status == TaskStatus.recording
            )
        )
        if result.scalar_one_or_none():
            raise ValueError("Source is already being recorded")

        result = await db.execute(select(LiveSource).where(LiveSource.id == source_id))
        source = result.scalar_one_or_none()
        if not source:
            raise ValueError("Source not found")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{source.name}_{timestamp}.mp4"
        file_path = settings.storage_path / filename

        task = RecordTask(
            source_id=source_id,
            status=TaskStatus.pending,
            file_path=str(file_path)
        )
        db.add(task)
        await db.commit()
        await db.refresh(task)

        asyncio.create_task(cls._run_ffmpeg(task.id, source.url, file_path))
        return task

    @classmethod
    async def _run_ffmpeg(cls, task_id: int, url: str, output_path: Path):
        from app.database import async_session

        async with async_session() as db:
            result = await db.execute(select(RecordTask).where(RecordTask.id == task_id))
            task = result.scalar_one()

            cmd = [
                "ffmpeg", "-y", "-i", url,
                "-c", "copy", "-f", "mp4", "-movflags", "+faststart",
                str(output_path)
            ]

            try:
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                cls._processes[task_id] = process

                task.status = TaskStatus.recording
                task.started_at = datetime.utcnow()
                await db.commit()

                _, stderr = await process.communicate()
                del cls._processes[task_id]

                if process.returncode == 0:
                    task.status = TaskStatus.completed
                elif process.returncode == 255:
                    task.status = TaskStatus.interrupted
                else:
                    task.status = TaskStatus.failed
                    task.error_message = stderr.decode()[-500:]

                task.ended_at = datetime.utcnow()

                if output_path.exists():
                    task.file_size = output_path.stat().st_size
                    task.duration = await cls._get_duration(output_path)
                    video = VideoFile(
                        task_id=task.id,
                        title=output_path.stem,
                        file_path=str(output_path),
                        file_size=task.file_size,
                        duration=task.duration
                    )
                    db.add(video)

                await db.commit()

            except Exception as e:
                task.status = TaskStatus.failed
                task.error_message = str(e)
                task.ended_at = datetime.utcnow()
                await db.commit()

    @classmethod
    async def stop_recording(cls, task_id: int, db: AsyncSession) -> RecordTask:
        result = await db.execute(select(RecordTask).where(RecordTask.id == task_id))
        task = result.scalar_one_or_none()
        if not task:
            raise ValueError("Task not found")
        if task.status != TaskStatus.recording:
            raise ValueError("Task is not recording")

        process = cls._processes.get(task_id)
        if process:
            process.terminate()
            try:
                await asyncio.wait_for(process.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
            except ProcessLookupError:
                pass  # Process already exited
        return task

    @classmethod
    async def _get_duration(cls, file_path: Path) -> Optional[int]:
        try:
            cmd = [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                str(file_path)
            ]
            process = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await asyncio.wait_for(process.communicate(), timeout=10.0)
            return int(float(stdout.decode().strip()))
        except (asyncio.TimeoutError, ValueError, OSError):
            return None
