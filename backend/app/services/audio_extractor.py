"""Audio extraction service using FFmpeg."""
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.models import VideoFile, AudioExtractTask, AudioExtractStatus


class AudioExtractorService:
    """Service for extracting audio from video files using FFmpeg."""

    _processes: dict[int, asyncio.subprocess.Process] = {}

    @classmethod
    async def start_extraction(
        cls,
        video_id: int,
        db: AsyncSession,
        format: str = "mp3",
        bitrate: str = "128k"
    ) -> AudioExtractTask:
        """
        Start audio extraction from a video file.

        Args:
            video_id: ID of the video to extract audio from
            db: Database session
            format: Output audio format (default: mp3)
            bitrate: Output audio bitrate (default: 128k)

        Returns:
            AudioExtractTask: The created extraction task

        Raises:
            ValueError: If video not found or extraction already in progress
        """
        # Check if video exists
        result = await db.execute(
            select(VideoFile).where(VideoFile.id == video_id)
        )
        video = result.scalar_one_or_none()
        if not video:
            raise ValueError("Video not found")

        # Check if there's already a processing task
        result = await db.execute(
            select(AudioExtractTask).where(
                AudioExtractTask.video_id == video_id,
                AudioExtractTask.status == AudioExtractStatus.processing
            )
        )
        if result.scalar_one_or_none():
            raise ValueError("Audio extraction already in progress for this video")

        # Check if there's already a completed task with the same format
        result = await db.execute(
            select(AudioExtractTask).where(
                AudioExtractTask.video_id == video_id,
                AudioExtractTask.status == AudioExtractStatus.completed,
                AudioExtractTask.format == format
            )
        )
        existing_task = result.scalar_one_or_none()
        if existing_task and existing_task.output_path:
            output_file = Path(existing_task.output_path)
            if output_file.exists():
                # Return existing completed task
                return existing_task

        # Create audio output directory
        audio_dir = settings.storage_path / "audio"
        audio_dir.mkdir(parents=True, exist_ok=True)

        # Generate output filename
        video_path = Path(video.file_path)
        output_filename = f"{video_path.stem}.{format}"
        output_path = audio_dir / output_filename

        # Create extraction task
        task = AudioExtractTask(
            video_id=video_id,
            status=AudioExtractStatus.pending,
            format=format,
            bitrate=bitrate,
            output_path=str(output_path)
        )
        db.add(task)
        await db.commit()
        await db.refresh(task)

        # Start extraction in background
        asyncio.create_task(cls._run_ffmpeg(task.id, video.file_path, output_path, bitrate))
        return task

    @classmethod
    async def _run_ffmpeg(
        cls,
        task_id: int,
        input_path: str,
        output_path: Path,
        bitrate: str
    ):
        """
        Run FFmpeg to extract audio from video.

        Args:
            task_id: ID of the extraction task
            input_path: Path to input video file
            output_path: Path for output audio file
            bitrate: Audio bitrate
        """
        from app.database import async_session

        async with async_session() as db:
            result = await db.execute(
                select(AudioExtractTask).where(AudioExtractTask.id == task_id)
            )
            task = result.scalar_one()

            # FFmpeg command for audio extraction
            # -vn: no video
            # -acodec libmp3lame: use MP3 encoder
            # -ab: audio bitrate
            # -ar 44100: sample rate 44100Hz
            # -ac 2: stereo (2 channels)
            cmd = [
                "ffmpeg", "-y",
                "-i", input_path,
                "-vn",
                "-acodec", "libmp3lame",
                "-ab", bitrate,
                "-ar", "44100",
                "-ac", "2",
                str(output_path)
            ]

            try:
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                cls._processes[task_id] = process

                # Update status to processing
                task.status = AudioExtractStatus.processing
                await db.commit()

                # Wait for process to complete
                _, stderr = await process.communicate()
                del cls._processes[task_id]

                if process.returncode == 0:
                    task.status = AudioExtractStatus.completed
                    task.completed_at = datetime.utcnow()
                else:
                    task.status = AudioExtractStatus.failed
                    # Store last 500 chars of error message
                    error_msg = stderr.decode()[-500:] if stderr else "Unknown error"
                    # Note: AudioExtractTask doesn't have error_message field
                    # We just mark it as failed

                await db.commit()

            except Exception as e:
                task.status = AudioExtractStatus.failed
                await db.commit()

    @classmethod
    async def get_task(cls, video_id: int, db: AsyncSession) -> Optional[AudioExtractTask]:
        """
        Get the latest audio extraction task for a video.

        Args:
            video_id: ID of the video
            db: Database session

        Returns:
            AudioExtractTask or None
        """
        result = await db.execute(
            select(AudioExtractTask)
            .where(AudioExtractTask.video_id == video_id)
            .order_by(AudioExtractTask.created_at.desc())
        )
        return result.scalar_one_or_none()

    @classmethod
    async def get_completed_task(cls, video_id: int, db: AsyncSession) -> Optional[AudioExtractTask]:
        """
        Get the completed audio extraction task for a video.

        Args:
            video_id: ID of the video
            db: Database session

        Returns:
            AudioExtractTask or None if no completed task exists
        """
        result = await db.execute(
            select(AudioExtractTask)
            .where(
                AudioExtractTask.video_id == video_id,
                AudioExtractTask.status == AudioExtractStatus.completed
            )
            .order_by(AudioExtractTask.created_at.desc())
        )
        return result.scalar_one_or_none()
