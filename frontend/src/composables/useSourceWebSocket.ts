/**
 * WebSocket 连接管理 Composable
 * 用于实时接收直播源状态更新，支持断线重连
 */
import { ref, onUnmounted } from 'vue'

export interface SourceStatusMessage {
  type: 'source_status_changed' | 'connected' | 'pong'
  data: {
    source_id?: number
    is_online?: boolean
    timestamp?: string
    connection_id?: number
    attempt?: number      // 当前检测次数
    max_attempts?: number // 最大检测次数
    checking?: boolean    // 是否仍在检测中
  }
}

export interface UseSourceWebSocketOptions {
  onStatusChange?: (sourceId: number, isOnline: boolean, data?: SourceStatusMessage['data']) => void
  onConnected?: (connectionId: number) => void
  onDisconnected?: () => void
  onError?: (error: Event) => void
}

export function useSourceWebSocket(options: UseSourceWebSocketOptions = {}) {
  const {
    onStatusChange,
    onConnected,
    onDisconnected,
    onError
  } = options

  const ws = ref<WebSocket | null>(null)
  const connected = ref(false)
  const connectionId = ref<number | null>(null)
  const reconnecting = ref(false)

  // 重连配置
  const maxReconnectDelay = 30000 // 最大重连间隔 30 秒
  const initialReconnectDelay = 1000 // 初始重连间隔 1 秒
  let reconnectDelay = initialReconnectDelay
  let reconnectTimer: number | null = null
  let reconnectAttempts = 0
  let manualClose = false

  // 心跳定时器
  let heartbeatTimer: number | null = null

  /**
   * 获取 WebSocket URL
   */
  const getWsUrl = (): string => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = import.meta.env.VITE_API_HOST || window.location.host
    return `${protocol}//${host}/ws/sources`
  }

  /**
   * 启动心跳
   */
  const startHeartbeat = () => {
    stopHeartbeat()
    heartbeatTimer = window.setInterval(() => {
      if (ws.value && ws.value.readyState === WebSocket.OPEN) {
        try {
          ws.value.send(JSON.stringify({ type: 'ping' }))
        } catch (e) {
          console.warn('Failed to send heartbeat:', e)
        }
      }
    }, 30000) // 每 30 秒发送一次心跳
  }

  /**
   * 停止心跳
   */
  const stopHeartbeat = () => {
    if (heartbeatTimer) {
      clearInterval(heartbeatTimer)
      heartbeatTimer = null
    }
  }

  /**
   * 处理接收到的消息
   */
  const handleMessage = (event: MessageEvent) => {
    try {
      const message: SourceStatusMessage = JSON.parse(event.data)

      switch (message.type) {
        case 'connected':
          connectionId.value = message.data.connection_id || null
          console.log('[WebSocket] Connected:', connectionId.value)
          if (onConnected && connectionId.value) {
            onConnected(connectionId.value)
          }
          break

        case 'source_status_changed':
          if (message.data.source_id !== undefined && message.data.is_online !== undefined) {
            console.log('[WebSocket] Status changed:', message.data)
            if (onStatusChange) {
              onStatusChange(message.data.source_id, message.data.is_online, message.data)
            }
          }
          break

        case 'pong':
          // 心跳响应，无需处理
          break

        default:
          console.warn('[WebSocket] Unknown message type:', message.type)
      }
    } catch (e) {
      console.error('[WebSocket] Failed to parse message:', e)
    }
  }

  /**
   * 连接 WebSocket
   */
  const connect = () => {
    // 如果已经连接，不重复连接
    if (ws.value && (ws.value.readyState === WebSocket.CONNECTING || ws.value.readyState === WebSocket.OPEN)) {
      console.log('[WebSocket] Already connected or connecting')
      return
    }

    manualClose = false
    const url = getWsUrl()

    console.log('[WebSocket] Connecting to:', url)

    try {
      ws.value = new WebSocket(url)

      ws.value.onopen = () => {
        console.log('[WebSocket] Connected')
        connected.value = true
        reconnecting.value = false
        reconnectDelay = initialReconnectDelay
        reconnectAttempts = 0
        startHeartbeat()
      }

      ws.value.onmessage = handleMessage

      ws.value.onerror = (error) => {
        console.error('[WebSocket] Error:', error)
        if (onError) {
          onError(error)
        }
      }

      ws.value.onclose = (event) => {
        console.log('[WebSocket] Closed:', event.code, event.reason)
        connected.value = false
        connectionId.value = null
        stopHeartbeat()

        if (onDisconnected) {
          onDisconnected()
        }

        // 如果不是手动关闭，尝试重连
        if (!manualClose) {
          scheduleReconnect()
        }
      }
    } catch (e) {
      console.error('[WebSocket] Failed to create connection:', e)
      scheduleReconnect()
    }
  }

  /**
   * 安排重连
   */
  const scheduleReconnect = () => {
    if (manualClose) {
      return
    }

    if (reconnectTimer) {
      return // 已经有重连任务在运行
    }

    reconnecting.value = true
    reconnectAttempts++

    console.log(`[WebSocket] Reconnecting in ${reconnectDelay / 1000}s (attempt ${reconnectAttempts})`)

    reconnectTimer = window.setTimeout(() => {
      reconnectTimer = null
      connect()

      // 指数退避，每次翻倍，直到最大值
      reconnectDelay = Math.min(reconnectDelay * 2, maxReconnectDelay)
    }, reconnectDelay)
  }

  /**
   * 断开连接
   */
  const disconnect = () => {
    manualClose = true

    // 清除重连定时器
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }

    stopHeartbeat()

    if (ws.value) {
      ws.value.close(1000, 'Manual disconnect')
      ws.value = null
    }

    connected.value = false
    connectionId.value = null
    reconnecting.value = false
  }

  /**
   * 手动重连
   */
  const reconnect = () => {
    disconnect()
    reconnectDelay = initialReconnectDelay
    reconnectAttempts = 0
    connect()
  }

  // 组件卸载时断开连接
  onUnmounted(() => {
    disconnect()
  })

  return {
    connected,
    connecting: ref(false),
    reconnecting,
    connectionId,
    connect,
    disconnect,
    reconnect
  }
}
