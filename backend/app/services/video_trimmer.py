"""Video trimming service using FFmpeg."""
import asyncio
import os
from datetime import datetime
from pathlib import Path
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.models import VideoFile, VideoTrimTask, TrimStatus, SourceType, VideoStatus


class VideoTrimmerService:
    """Service for trimming video files using FFmpeg."""

    _processes: dict[int, asyncio.subprocess.Process] = {}
    _background_tasks: set = set()  # Track background tasks to prevent garbage collection

    @classmethod
    async def start_trimming(
        cls,
        video_id: int,
        start_time: int,
        end_time: int,
        extract_audio: bool,
        keep_original: bool,
        db: AsyncSession
    ) -> VideoTrimTask:
        """
        Start video trimming operation.

        Args:
            video_id: ID of the video to trim
            start_time: Start time in seconds
            end_time: End time in seconds
            extract_audio: Whether to extract audio from trimmed video
            keep_original: Whether to keep the original file
            db: Database session

        Returns:
            VideoTrimTask: The created trim task

        Raises:
            ValueError: If validation fails
        """
        # Check if video exists
        result = await db.execute(
            select(VideoFile).where(VideoFile.id == video_id)
        )
        video = result.scalar_one_or_none()
        if not video:
            raise ValueError("Video not found")

        # Validate video is recorded (not uploaded)
        if video.source_type != SourceType.recorded:
            raise ValueError("Only recorded videos can be trimmed")

        # Validate times
        if start_time < 0:
            raise ValueError("Start time must be non-negative")
        if end_time <= start_time:
            raise ValueError("End time must be greater than start time")
        if video.duration and end_time > video.duration:
            raise ValueError(f"End time exceeds video duration ({video.duration}s)")

        # Get absolute path to video file
        video_path = Path(video.file_path)
        if not video_path.is_absolute():
            video_path = settings.storage_path / video.file_path

        # Check if video file exists
        if not video_path.exists():
            raise ValueError(f"Video file not found: {video_path}")

        # Check if there's already a processing task
        result = await db.execute(
            select(VideoTrimTask).where(
                VideoTrimTask.video_id == video_id,
                VideoTrimTask.status == TrimStatus.processing
            )
        )
        if result.scalar_one_or_none():
            raise ValueError("Video trimming already in progress for this video")

        # Generate output filenames with timestamp
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        trimmed_filename = f"trimmed_{timestamp_str}_{video_id}.mp4"
        trimmed_path = settings.storage_path / trimmed_filename

        # Generate audio filename if needed
        audio_path = None
        if extract_audio:
            audio_dir = settings.storage_path / "audio"
            audio_dir.mkdir(parents=True, exist_ok=True)
            audio_filename = f"audio_{timestamp_str}_{video_id}.mp3"
            audio_path = audio_dir / audio_filename

        # Create trim task
        task = VideoTrimTask(
            video_id=video_id,
            status=TrimStatus.pending,
            start_time=start_time,
            end_time=end_time,
            extract_audio=extract_audio,
            keep_original=keep_original,
            audio_bitrate="192k",  # Use 192k for trim extraction
            trimmed_video_path=str(trimmed_path),
            extracted_audio_path=str(audio_path) if audio_path else None
        )
        db.add(task)
        await db.commit()
        await db.refresh(task)

        # Start trimming in background
        bg_task = asyncio.create_task(
            cls._run_trim_workflow(task.id, str(video_path))
        )
        cls._background_tasks.add(bg_task)
        bg_task.add_done_callback(cls._background_tasks.discard)

        return task

    @classmethod
    async def _run_trim_workflow(cls, task_id: int, input_path: str):
        """
        Run the complete trim workflow: trim video, optionally extract audio, handle original file.

        Args:
            task_id: ID of the trim task
            input_path: Path to input video file
        """
        from app.database import async_session

        async with async_session() as db:
            result = await db.execute(
                select(VideoTrimTask).where(VideoTrimTask.id == task_id)
            )
            task = result.scalar_one()

            try:
                # Step 1: Trim video
                await cls._run_ffmpeg_trim(
                    task_id,
                    input_path,
                    task.trimmed_video_path,
                    task.start_time,
                    task.end_time
                )

                # Check if trim succeeded
                await db.refresh(task)
                if task.status == TrimStatus.failed:
                    return

                # Step 2: Extract audio if requested
                if task.extract_audio and task.extracted_audio_path:
                    await cls._extract_audio_from_trim(
                        task_id,
                        task.trimmed_video_path,
                        task.extracted_audio_path,
                        task.audio_bitrate
                    )

                # Check if extraction succeeded (if it was requested)
                await db.refresh(task)
                if task.status == TrimStatus.failed:
                    return

                # Step 3: Handle original file and update video record
                await cls._handle_original_file(task.video_id, task.keep_original, db)

                # Mark task as completed
                task.status = TrimStatus.completed
                task.completed_at = datetime.utcnow()
                await db.commit()

            except Exception as e:
                task.status = TrimStatus.failed
                task.error_message = str(e)[:500]
                await db.commit()

    @classmethod
    async def _run_ffmpeg_trim(
        cls,
        task_id: int,
        input_path: str,
        output_path: str,
        start_time: int,
        end_time: int
    ):
        """
        Run FFmpeg to trim video.

        Args:
            task_id: ID of the trim task
            input_path: Path to input video file
            output_path: Path for output trimmed video
            start_time: Start time in seconds
            end_time: End time in seconds
        """
        from app.database import async_session

        async with async_session() as db:
            result = await db.execute(
                select(VideoTrimTask).where(VideoTrimTask.id == task_id)
            )
            task = result.scalar_one()

            # FFmpeg command for video trimming (fast, no re-encoding)
            # -ss: start time
            # -to: end time
            # -i: input file
            # -c copy: copy codec (no re-encoding)
            # -avoid_negative_ts make_zero: handle timestamp issues
            # -f mp4: force MP4 format
            # -movflags +faststart: optimize for streaming
            cmd = [
                "ffmpeg", "-y",
                "-ss", str(start_time),
                "-to", str(end_time),
                "-i", input_path,
                "-c", "copy",
                "-avoid_negative_ts", "make_zero",
                "-f", "mp4",
                "-movflags", "+faststart",
                output_path
            ]

            try:
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                cls._processes[task_id] = process

                # Update status to processing
                task.status = TrimStatus.processing
                await db.commit()

                # Wait for process to complete
                _, stderr = await process.communicate()

                if task_id in cls._processes:
                    del cls._processes[task_id]

                if process.returncode != 0:
                    task.status = TrimStatus.failed
                    error_msg = stderr.decode()[-500:] if stderr else "Unknown error"
                    task.error_message = f"FFmpeg trim failed: {error_msg}"
                    await db.commit()

            except Exception as e:
                if task_id in cls._processes:
                    del cls._processes[task_id]
                task.status = TrimStatus.failed
                task.error_message = f"Trim error: {str(e)[:500]}"
                await db.commit()

    @classmethod
    async def _extract_audio_from_trim(
        cls,
        task_id: int,
        trimmed_video_path: str,
        audio_output_path: str,
        bitrate: str
    ):
        """
        Extract audio from trimmed video.

        Args:
            task_id: ID of the trim task
            trimmed_video_path: Path to trimmed video file
            audio_output_path: Path for output audio file
            bitrate: Audio bitrate (e.g., "192k")
        """
        from app.database import async_session

        async with async_session() as db:
            result = await db.execute(
                select(VideoTrimTask).where(VideoTrimTask.id == task_id)
            )
            task = result.scalar_one()

            # FFmpeg command for audio extraction
            cmd = [
                "ffmpeg", "-y",
                "-i", trimmed_video_path,
                "-vn",
                "-acodec", "libmp3lame",
                "-ab", bitrate,
                "-ar", "44100",
                "-ac", "2",
                audio_output_path
            ]

            try:
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )

                # Wait for process to complete
                _, stderr = await process.communicate()

                if process.returncode != 0:
                    task.status = TrimStatus.failed
                    error_msg = stderr.decode()[-500:] if stderr else "Unknown error"
                    task.error_message = f"Audio extraction failed: {error_msg}"
                    await db.commit()

            except Exception as e:
                task.status = TrimStatus.failed
                task.error_message = f"Audio extraction error: {str(e)[:500]}"
                await db.commit()

    @classmethod
    async def _handle_original_file(
        cls,
        video_id: int,
        keep_original: bool,
        db: AsyncSession
    ):
        """
        Handle original file based on keep_original flag and update video record.

        Args:
            video_id: ID of the video
            keep_original: Whether to keep the original file
            db: Database session
        """
        result = await db.execute(
            select(VideoFile).where(VideoFile.id == video_id)
        )
        video = result.scalar_one()

        # Get the latest completed trim task
        result = await db.execute(
            select(VideoTrimTask)
            .where(
                VideoTrimTask.video_id == video_id,
                VideoTrimTask.status == TrimStatus.processing
            )
            .order_by(VideoTrimTask.created_at.desc())
        )
        task = result.scalar_one_or_none()

        if not task or not task.trimmed_video_path:
            return

        # Get absolute paths
        original_path = Path(video.file_path)
        if not original_path.is_absolute():
            original_path = settings.storage_path / video.file_path

        trimmed_path = Path(task.trimmed_video_path)

        # Delete original file if keep_original is False
        if not keep_original and original_path.exists():
            try:
                os.remove(original_path)
            except Exception:
                pass  # Ignore deletion errors

        # Update video record to point to trimmed version
        # Store relative path
        video.file_path = str(trimmed_path.relative_to(settings.storage_path))

        # Reset video status to pending for re-approval
        video.status = VideoStatus.pending
        video.reviewed_at = None
        video.reviewed_by = None

        # Update duration if we can calculate it
        duration = task.end_time - task.start_time
        video.duration = duration

        await db.commit()

    @classmethod
    async def get_task(cls, video_id: int, db: AsyncSession) -> Optional[VideoTrimTask]:
        """
        Get the latest trim task for a video.

        Args:
            video_id: ID of the video
            db: Database session

        Returns:
            VideoTrimTask or None
        """
        result = await db.execute(
            select(VideoTrimTask)
            .where(VideoTrimTask.video_id == video_id)
            .order_by(VideoTrimTask.created_at.desc())
        )
        return result.scalar_one_or_none()

    @classmethod
    async def get_task_by_id(cls, task_id: int, db: AsyncSession) -> Optional[VideoTrimTask]:
        """
        Get a specific trim task by ID.

        Args:
            task_id: ID of the task
            db: Database session

        Returns:
            VideoTrimTask or None
        """
        result = await db.execute(
            select(VideoTrimTask).where(VideoTrimTask.id == task_id)
        )
        return result.scalar_one_or_none()

    @classmethod
    async def cancel_task(cls, task_id: int, db: AsyncSession) -> bool:
        """
        Cancel an ongoing trim task.

        Args:
            task_id: ID of the task to cancel
            db: Database session

        Returns:
            bool: True if task was cancelled, False otherwise
        """
        result = await db.execute(
            select(VideoTrimTask).where(VideoTrimTask.id == task_id)
        )
        task = result.scalar_one_or_none()

        if not task or task.status != TrimStatus.processing:
            return False

        # Terminate FFmpeg process if running
        if task_id in cls._processes:
            process = cls._processes[task_id]
            try:
                process.terminate()
                await asyncio.wait_for(process.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                process.kill()
            finally:
                del cls._processes[task_id]

        # Update task status
        task.status = TrimStatus.failed
        task.error_message = "Task cancelled by user"
        task.completed_at = datetime.utcnow()
        await db.commit()

        return True
