import asyncio
import logging
import traceback

logger = logging.getLogger(__name__)


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
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=20.0)
        except asyncio.TimeoutError:
            process.kill()
            return False, "连接超时（20秒），请检查网络或流地址是否正确"

        if process.returncode == 0 and b"codec_type" in stdout:
            return True, "直播流在线"

        error_msg = stderr.decode().strip()
        if not error_msg:
            return False, "直播流离线或无法访问"

        # 提供更友好的错误信息
        if "Connection refused" in error_msg:
            return False, "连接被拒绝，请检查流地址和端口"
        elif "Connection timed out" in error_msg:
            return False, "连接超时，请检查网络连接"
        elif "Invalid data found" in error_msg:
            return False, "无效的流数据，请检查流格式"
        elif "Server returned 404" in error_msg or "404 Not Found" in error_msg:
            return False, "流不存在（404），请检查流路径"
        else:
            return False, f"检测失败: {error_msg[:100]}"
    except Exception as e:
        logger.error(f"Stream check error for {url}: {type(e).__name__}: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        error_detail = str(e) if str(e) else f"{type(e).__name__}"
        return False, f"系统错误: {error_detail}"
