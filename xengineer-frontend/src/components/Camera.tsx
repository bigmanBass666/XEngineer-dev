import { useCamera } from '../hooks/useCamera'
import { useEffect } from 'react'

interface CameraProps {
  onFrame?: (base64: string) => void
  triggerCapture?: boolean  // 外部触发截图（VAD 说话时）
}

export function Camera({ onFrame, triggerCapture }: CameraProps) {
  const {
    isActive,
    error,
    videoRef,
    canvasRef,
    start,
    stop,
    captureAndSend,
  } = useCamera({
    width: 640,
    height: 480,
    onFrame,
  })

  // VAD 触发截图
  useEffect(() => {
    if (triggerCapture && isActive) {
      captureAndSend()
    }
  }, [triggerCapture, isActive, captureAndSend])

  return (
    <div className="relative w-full aspect-[4/3] bg-gray-800 rounded-lg overflow-hidden">
      {/* 隐藏的 Canvas（用于截图） */}
      <canvas ref={canvasRef} className="hidden" />

      {/* 视频预览 */}
      <video
        ref={videoRef}
        className="w-full h-full object-cover" style={{ transform: 'scaleX(-1)' }}
        playsInline
        muted
      />

      {/* 覆盖层 */}
      {!isActive && !error && (
        <div className="absolute inset-0 flex flex-col items-center justify-center bg-gray-800/80">
          <svg className="w-12 h-12 text-gray-500 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
              d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
          </svg>
          <button
            onClick={start}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm font-medium transition-colors"
          >
            开启摄像头
          </button>
        </div>
      )}

      {/* 摄像头开启后可以停止 */}
      {isActive && (
        <div className="absolute bottom-3 right-3">
          <button
            onClick={stop}
            className="px-3 py-1.5 bg-black/50 hover:bg-black/70 rounded-lg text-xs font-medium transition-colors backdrop-blur-sm"
          >
            关闭
          </button>
        </div>
      )}

      {/* 错误提示 */}
      {error && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-800/80">
          <div className="text-center">
            <p className="text-red-400 text-sm">{error}</p>
          </div>
        </div>
      )}

      {/* 截图闪光效果 */}
      {triggerCapture && isActive && (
        <div className="absolute inset-0 bg-white/20 animate-pulse pointer-events-none" />
      )}
    </div>
  )
}