"""Chunked upload service for large file uploads."""
import os
import uuid
import shutil
import asyncio
import subprocess
from pathlib import Path
from typing import Optional, List, Tuple

from app.config import settings
from app.models.upload_task import UploadStatus


# Allowed file extensions
ALLOWED_VIDEO_EXTENSIONS = {'.mp4'}
ALLOWED_AUDIO_EXTENSIONS = {'.mp3', '.m4a'}
ALLOWED_EXTENSIONS = ALLOWED_VIDEO_EXTENSIONS | ALLOWED_AUDIO_EXTENSIONS

# Max file sizes
MAX_VIDEO_SIZE = 10 * 1024 * 1024 * 1024  # 10GB
MAX_AUDIO_SIZE = 1 * 1024 * 1024 * 1024   # 1GB


def get_temp_dir(task_id: str) -> Path:
    """Get temporary directory for upload task."""
    return settings.storage_path / "temp" / task_id


def get_chunk_path(task_id: str, chunk_index: int) -> Path:
    """Get path for a specific chunk."""
    return get_temp_dir(task_id) / f"chunk_{chunk_index:06d}"


def validate_file(filename: str, file_size: int) -> Tuple[bool, str, str]:
    """
    Validate file extension and size.
    Returns: (is_valid, file_type, error_message)
    """
    ext = Path(filename).suffix.lower()

    if ext not in ALLOWED_EXTENSIONS:
        return False, "", f"File type not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"

    if ext in ALLOWED_VIDEO_EXTENSIONS:
        if file_size > MAX_VIDEO_SIZE:
            return False, "", f"Video file too large. Max: {MAX_VIDEO_SIZE // (1024**3)}GB"
        return True, "video", ""
    else:
        if file_size > MAX_AUDIO_SIZE:
            return False, "", f"Audio file too large. Max: {MAX_AUDIO_SIZE // (1024**3)}GB"
        return True, "audio", ""


def create_upload_task(filename: str, file_size: int, chunk_size: int) -> Tuple[str, int]:
    """
    Create upload task and return task_id and total_chunks.
    """
    task_id = str(uuid.uuid4())
    total_chunks = (file_size + chunk_size - 1) // chunk_size

    # Create temp directory
    temp_dir = get_temp_dir(task_id)
    temp_dir.mkdir(parents=True, exist_ok=True)

    return task_id, total_chunks


def save_chunk(task_id: str, chunk_index: int, chunk_data: bytes) -> bool:
    """Save a chunk to disk."""
    chunk_path = get_chunk_path(task_id, chunk_index)
    try:
        with open(chunk_path, 'wb') as f:
            f.write(chunk_data)
        return True
    except Exception:
        return False


def get_uploaded_chunks(task_id: str) -> List[int]:
    """Get list of uploaded chunk indices."""
    temp_dir = get_temp_dir(task_id)
    if not temp_dir.exists():
        return []

    chunks = []
    for f in temp_dir.iterdir():
        if f.name.startswith("chunk_"):
            try:
                index = int(f.name.split("_")[1])
                chunks.append(index)
            except (ValueError, IndexError):
                pass
    return sorted(chunks)


def merge_chunks(task_id: str, total_chunks: int, output_filename: str) -> Optional[Path]:
    """Merge all chunks into final file."""
    temp_dir = get_temp_dir(task_id)
    output_path = settings.storage_path / output_filename

    try:
        with open(output_path, 'wb') as outfile:
            for i in range(total_chunks):
                chunk_path = get_chunk_path(task_id, i)
                if not chunk_path.exists():
                    return None
                with open(chunk_path, 'rb') as chunk_file:
                    shutil.copyfileobj(chunk_file, outfile)
        return output_path
    except Exception:
        if output_path.exists():
            output_path.unlink()
        return None


def cleanup_temp(task_id: str):
    """Clean up temporary files for an upload task."""
    temp_dir = get_temp_dir(task_id)
    if temp_dir.exists():
        shutil.rmtree(temp_dir, ignore_errors=True)


async def generate_thumbnail(video_path: Path) -> Optional[Path]:
    """Generate thumbnail for video file."""
    thumbnail_path = video_path.with_suffix('.jpg')

    try:
        cmd = [
            'ffmpeg', '-y',
            '-i', str(video_path),
            '-ss', '00:00:01',
            '-vframes', '1',
            '-vf', 'scale=320:-1',
            str(thumbnail_path)
        ]

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL
        )
        await process.wait()

        if thumbnail_path.exists():
            return thumbnail_path
        return None
    except Exception:
        return None


async def get_media_duration(file_path: Path) -> Optional[int]:
    """Get duration of media file in seconds."""
    try:
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            str(file_path)
        ]

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL
        )
        stdout, _ = await process.communicate()

        if stdout:
            duration = float(stdout.decode().strip())
            return int(duration)
        return None
    except Exception:
        return None
