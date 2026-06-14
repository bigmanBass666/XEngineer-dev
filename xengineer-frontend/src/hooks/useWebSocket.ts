import { useState, useEffect, useRef, useCallback } from 'react'
import type { ClientMessage, ServerMessage, ConnectionStatus } from '../lib/protocol'

const WS_URL = import.meta.env.VITE_WS_URL || `ws://${window.location.hostname}:8000/ws`

export function useWebSocket() {
  const [status, setStatus] = useState<ConnectionStatus>('disconnected')
  const wsRef = useRef<WebSocket | null>(null)
  const messageHandlersRef = useRef<Set<(msg: ServerMessage) => void>>(new Set())
  const reconnectTimerRef = useRef<number | null>(null)
  const connectRef = useRef<() => void>(() => {})

  const connect = useCallback(() => {
    setStatus('connecting')
    const ws = new WebSocket(WS_URL)

    ws.onopen = () => {
      setStatus('connected')
      console.log('[WS] Connected')
    }

    ws.onclose = () => {
      setStatus('disconnected')
      console.log('[WS] Disconnected')
      // 自动重连 — use ref to avoid stale closure
      reconnectTimerRef.current = window.setTimeout(() => connectRef.current(), 3000)
    }

    ws.onerror = (error) => {
      console.error('[WS] Error:', error)
      setStatus('error')
    }

    ws.onmessage = (event) => {
      try {
        const msg: ServerMessage = JSON.parse(event.data)
        messageHandlersRef.current.forEach(handler => handler(msg))
      } catch (e) {
        console.error('[WS] Failed to parse message:', e)
      }
    }

    wsRef.current = ws
  }, [])

  // Keep the ref in sync so ws.onclose always calls the latest connect
  useEffect(() => {
    connectRef.current = connect
  }, [connect])

  const send = useCallback((msg: ClientMessage) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(msg))
    } else {
      console.warn('[WS] Cannot send, not connected')
    }
  }, [])

  const onMessage = useCallback((handler: (msg: ServerMessage) => void) => {
    messageHandlersRef.current.add(handler)
    return () => { messageHandlersRef.current.delete(handler) }
  }, [])

  const disconnect = useCallback(() => {
    if (reconnectTimerRef.current) {
      clearTimeout(reconnectTimerRef.current)
    }
    wsRef.current?.close()
    wsRef.current = null
    setStatus('disconnected')
  }, [])

  useEffect(() => {
    connect()
    return () => disconnect()
  }, [connect, disconnect])

  return { status, send, onMessage, connect, disconnect }
}
