import { useCallback, useEffect, useRef } from 'react'

/**
 * 移动端音频会话管理 hook
 * 
 * 解决：getUserMedia 持续活跃 + 同时播放 TTS → OS 识别为"语音通话" → 音量键走通话通道
 * 
 * 方案 B（iOS）：navigator.audioSession.type 动态切换音频路由
 * 方案 C（Android）：echoCancellation:false 阻止 MODE_IN_COMMUNICATION（在 useVAD 中处理）
 * 
 * 核心原则：麦克风始终活跃，完整保留 barge-in 能力
 */

/** 检测是否为移动设备 */
function isMobileDevice(): boolean {
  if (typeof navigator === 'undefined') return false
  const ua = navigator.userAgent.toLowerCase()
  return /android|iphone|ipad|ipod|mobile/.test(ua)
}

/** 检测 iOS Safari 是否支持 audioSession API */
function supportsAudioSession(): boolean {
  return 'audioSession' in navigator
}

export function useAudioSession() {
  const initializedRef = useRef(false)

  // 初始化：在 getUserMedia 之前设置音频会话类型（iOS Safari 16.4+）
  useEffect(() => {
    if (!isMobileDevice() || !supportsAudioSession()) return
    if (initializedRef.current) return
    initializedRef.current = true

    try {
      // 设置为 play-and-record 模式，让 iOS 正确路由音频
      ;(navigator as any).audioSession.type = 'play-and-record'
      console.log('[AudioSession] 初始化: play-and-record')
    } catch (e) {
      console.warn('[AudioSession] 初始化失败:', e)
    }
  }, [])

  /** TTS 开始播放时调用 — 切换到 playback 模式，让音量键控制媒体音量 */
  const handleTTSPlay = useCallback(() => {
    if (!supportsAudioSession()) return
    try {
      ;(navigator as any).audioSession.type = 'playback'
      console.log('[AudioSession] TTS 播放: playback')
    } catch (e) {
      console.warn('[AudioSession] 切换到 playback 失败:', e)
    }
  }, [])

  /** TTS 停止时调用 — 恢复到 play-and-record 模式 */
  const handleTTSStop = useCallback(() => {
    if (!supportsAudioSession()) return
    try {
      ;(navigator as any).audioSession.type = 'play-and-record'
      console.log('[AudioSession] TTS 结束: play-and-record')
    } catch (e) {
      console.warn('[AudioSession] 恢复到 play-and-record 失败:', e)
    }
  }, [])

  return { handleTTSPlay, handleTTSStop }
}