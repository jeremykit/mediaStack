"""
WebSocket 连接管理，用于实时推送直播源状态变化
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from typing import Set, Dict, Any
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["websocket"])

# 存储所有活跃的 WebSocket 连接
active_connections: Set[WebSocket] = set()

# 连接ID计数器
_connection_id_counter = 0
# 连接ID到 WebSocket 的映射
connection_map: Dict[int, WebSocket] = {}
# WebSocket 到连接ID的映射
websocket_to_id: Dict[WebSocket, int] = {}


@router.websocket("/sources")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket 端点，用于接收直播源状态更新

    客户端连接后，服务器会推送以下消息：
    {
        "type": "source_status_changed",
        "data": {
            "source_id": 1,
            "is_online": true,
            "timestamp": "2025-02-06T12:00:00Z"
        }
    }
    """
    global _connection_id_counter

    await websocket.accept()
    _connection_id_counter += 1
    conn_id = _connection_id_counter

    active_connections.add(websocket)
    connection_map[conn_id] = websocket
    websocket_to_id[websocket] = conn_id

    logger.info(f"WebSocket connection #{conn_id} established. Total connections: {len(active_connections)}")

    # 发送连接成功消息
    try:
        await websocket.send_json({
            "type": "connected",
            "data": {
                "connection_id": conn_id,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        })
    except Exception as e:
        logger.warning(f"Failed to send connected message to #{conn_id}: {e}")

    try:
        # 保持连接，接收客户端消息（用于心跳保活）
        while True:
            data = await websocket.receive_text()
            # 收到任何消息都视为心跳，回复 pong
            try:
                message = json.loads(data)
                if message.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
            except json.JSONDecodeError:
                # 不是 JSON 格式，也回复 pong
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        logger.info(f"WebSocket connection #{conn_id} disconnected")
    except Exception as e:
        logger.warning(f"WebSocket error on connection #{conn_id}: {e}")
    finally:
        # 清理连接
        active_connections.discard(websocket)
        if conn_id in connection_map:
            del connection_map[conn_id]
        if websocket in websocket_to_id:
            del websocket_to_id[websocket]
        logger.info(f"WebSocket connection #{conn_id} cleaned up. Total connections: {len(active_connections)}")


async def broadcast_source_status(source_id: int, is_online: bool, attempt: int = 0, max_attempts: int = 0):
    """
    广播直播源状态变化到所有连接的客户端

    Args:
        source_id: 直播源ID
        is_online: 在线状态
        attempt: 当前检测次数（0表示非检测任务触发）
        max_attempts: 最大检测次数
    """
    if not active_connections:
        logger.debug("No active WebSocket connections to broadcast to")
        return

    message = {
        "type": "source_status_changed",
        "data": {
            "source_id": source_id,
            "is_online": is_online,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    }

    # 如果是检测任务触发，添加检测进度信息
    if attempt > 0:
        message["data"]["attempt"] = attempt
        message["data"]["max_attempts"] = max_attempts
        message["data"]["checking"] = attempt < max_attempts and not is_online

    # 记录需要移除的断开连接
    dead_connections = set()

    for websocket in active_connections:
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.warning(f"Failed to send message to connection: {e}")
            dead_connections.add(websocket)

    # 清理断开的连接
    for ws in dead_connections:
        active_connections.discard(ws)
        if ws in websocket_to_id:
            conn_id = websocket_to_id[ws]
            del connection_map[conn_id]
            del websocket_to_id[ws]

    if dead_connections:
        logger.info(f"Cleaned up {len(dead_connections)} dead connections. Active: {len(active_connections)}")

    logger.debug(f"Broadcasted status change for source {source_id}: online={is_online} to {len(active_connections)} connections")


async def broadcast_message(message: Dict[str, Any]):
    """
    广播任意消息到所有连接的客户端

    Args:
        message: 要广播的消息字典
    """
    if not active_connections:
        return

    dead_connections = set()

    for websocket in active_connections:
        try:
            await websocket.send_json(message)
        except Exception:
            dead_connections.add(websocket)

    # 清理断开的连接
    for ws in dead_connections:
        active_connections.discard(ws)
        if ws in websocket_to_id:
            conn_id = websocket_to_id[ws]
            del connection_map[conn_id]
            del websocket_to_id[ws]


def get_connection_count() -> int:
    """获取当前活跃连接数"""
    return len(active_connections)
