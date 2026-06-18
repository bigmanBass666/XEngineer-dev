import { useState, useRef, useCallback, useEffect } from 'react'
import { EnergyVAD, type VADState } from '../lib/vad'

interface UseVADOptions {
  onStateChange?: (state: VADState) => void
  onAudioData?: (pcmBase64: string) => void
  sampleRate?: number
}

export function useVAD(options: UseVADOptions = {}) {
  const { onStateChange, onAudioData, sampleRate = 16000 } = options
  const [state, setState] = useState<VADState>('silent')
  const [isActive, setIsActive] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const audioContextRef = useRef<AudioContext | null>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const processorRef = useRef<ScriptProcessorNode | null>(null)
  const sourceRef = useRef<MediaStreamAudioSourceNode | null>(null)
  const vadRef = useRef<EnergyVAD | null>(null)
  const stateRef = useRef<VADState>('silent')
  // 使用 ref 保存回调，避免闭包过期
  const onStateChangeRef = useRef(options.onStateChange)
  const onAudioDataRef = useRef(options.onAudioData)

  // 保持回调引用最新
  useEffect(() => {
    onStateChangeRef.current = onStateChange
  }, [onStateChange])
  useEffect(() => {
    onAudioDataRef.current = onAudioData
  }, [onAudioData])

  const start = useCallback(async () => {
    try {
      setError(null)

      // Android: echoCancellation=false 阻止 Chrome 进入 MODE_IN_COMMUNICATION
      // 参考: Chromium issue 40866811 (Chrome 工程师确认)
      // iOS: echoCancellation=true 保持默认行为
      const isAndroid = /android/i.test(navigator.userAgent)
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: sampleRate,
          channelCount: 1,
          echoCancellation: !isAndroid,
          noiseSuppression: true,
        }
      })
      streamRef.current = stream

      const audioContext = new AudioContext({ sampleRate })
      audioContextRef.current = audioContext

      const source = audioContext.createMediaStreamSource(stream)
      sourceRef.current = source

      const processor = audioContext.createScriptProcessor(512, 1, 1)
      processorRef.current = processor

      vadRef.current = new EnergyVAD(0.02, 0.01, 512)

      processor.onaudioprocess = (e) => {
        const inputData = e.inputBuffer.getChannelData(0)
        const float32Data = new Float32Array(inputData)

        // VAD 检测
        const result = vadRef.current!.processFrame(float32Data)
        if (result.state !== stateRef.current) {
          stateRef.current = result.state
          setState(result.state)
          onStateChangeRef.current?.(result.state)
        }

        // 只有在说话状态时才发送音频数据
        if (result.state === 'speaking' && onAudioDataRef.current) {
          // Float32 → Int16 转换
          const int16Data = new Int16Array(float32Data.length)
          for (let i = 0; i < float32Data.length; i++) {
            const s = Math.max(-1, Math.min(1, float32Data[i]))
            int16Data[i] = s < 0 ? s * 0x8000 : s * 0x7FFF
          }
          // 转为 base64
          const bytes = new Uint8Array(int16Data.buffer)
          let binary = ''
          for (let i = 0; i < bytes.length; i++) {
            binary += String.fromCharCode(bytes[i])
          }
          const base64 = btoa(binary)
          onAudioDataRef.current(base64)
        }
      }

      source.connect(processor)
      processor.connect(audioContext.destination)
      setIsActive(true)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error'
      console.error('[VAD] Failed to start:', err)
      setError(message)
      setIsActive(false)
    }
  }, [sampleRate])

  const stop = useCallback(() => {
    processorRef.current?.disconnect()
    processorRef.current = null
    sourceRef.current?.disconnect()
    sourceRef.current = null
    streamRef.current?.getTracks().forEach(t => t.stop())
    streamRef.current = null
    audioContextRef.current?.close()
    audioContextRef.current = null
    vadRef.current?.reset()
    vadRef.current = null
    setIsActive(false)
    setState('silent')
    stateRef.current = 'silent'
    setError(null)
  }, [])

  // 组件卸载时自动清理
  useEffect(() => {
    return () => stop()
  }, [stop])

  return { state, isActive, error, start, stop }
}