import asyncio


async def check_stream_status(url: str, protocol: str) -> tuple[bool, str]:
    """Check if a stream is online using ffprobe."""
    try:
        cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "stream=codec_type",
            "-of", "default=noprint_wrappers=1",
            "-i", url
        ]
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=10.0)
        except asyncio.TimeoutError:
            process.kill()
            return False, "Connection timeout"

        if process.returncode == 0 and b"codec_type" in stdout:
            return True, "Stream is online"
        return False, stderr.decode().strip() or "Stream is offline"
    except Exception as e:
        return False, str(e)
