import { useWebSocket } from './hooks/useWebSocket'
import { StatusBar } from './components/StatusBar'
import { ChatBubble } from './components/ChatBubble'
import { StreamingMessage } from './components/StreamingMessage'
import { AudioRecorder } from './components/AudioRecorder'
import { AudioPlayer, audioPlayer } from './components/AudioPlayer'
import { Camera } from './components/Camera'
import { useState, useCallback, useRef, useEffect } from 'react'
import type { ServerMessage, ChatMessage, VADStatus } from './lib/protocol'
import type { VADState } from './lib/vad'

function App() {
  const { status, send, onMessage } = useWebSocket()
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [currentAIResponse, setCurrentAIResponse] = useState('')
  const [isAIProcessing, setIsAIProcessing] = useState(false)
  const [vadStatus, setVadStatus] = useState<VADStatus>('silent')
  const [shouldCapture, setShouldCapture] = useState(false)
  const currentResponseRef = useRef('')
  const chatEndRef = useRef<HTMLDivElement>(null)
  const chatContainerRef = useRef<HTMLDivElement>(null)

  // 自动滚动到底部
  const scrollToBottom = useCallback(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [])

  // 监听消息变化时自动滚动
  useEffect(() => {
    scrollToBottom()
  }, [messages, currentAIResponse, scrollToBottom])

  // 处理后端消息
  useEffect(() => {
    const unsub = onMessage((msg: ServerMessage) => {
      switch (msg.type) {
        case 'asr_interim':
          // 可以在 UI 上显示中间识别结果
          break
        case 'asr_final':
          setMessages(prev => [...prev, {
            id: crypto.randomUUID(),
            role: 'user',
            content: msg.text,
            timestamp: Date.now()
          }])
          break
        case 'llm_chunk':
          if (!isAIProcessing) setIsAIProcessing(true)
          currentResponseRef.current += msg.text
          setCurrentAIResponse(currentResponseRef.current)
          break
        case 'tts_audio':
          // 将 base64 mp3 数据推入播放队列
          audioPlayer.enqueue(msg.data)
          break
        case 'tts_end':
          if (currentResponseRef.current) {
            setMessages(prev => [...prev, {
              id: crypto.randomUUID(),
              role: 'assistant',
              content: currentResponseRef.current,
              timestamp: Date.now()
            }])
            currentResponseRef.current = ''
            setCurrentAIResponse('')
          }
          setIsAIProcessing(false)
          break
        case 'status':
          console.log('[Status]', msg.message)
          // 测试消息回显：在对话区显示系统消息
          if (msg.message.startsWith('WS echo:')) {
            const echoText = msg.message.replace('WS echo: ', '')
            setMessages(prev => [...prev, {
              id: crypto.randomUUID(),
              role: 'system',
              content: `测试消息已发送，服务端回显: "${echoText}"`,
              timestamp: Date.now()
            }])
          }
          break
        case 'error':
          console.error('[Error]', msg.message)
          setIsAIProcessing(false)
          break
      }
    })
    return unsub
  }, [onMessage, isAIProcessing])

  // 发送测试消息
  const sendTest = useCallback(() => {
    // 在对话区显示用户发送的测试消息
    setMessages(prev => [...prev, {
      id: crypto.randomUUID(),
      role: 'user',
      content: '测试消息: hello from frontend',
      timestamp: Date.now()
    }])
    send({ type: 'test', data: 'hello from frontend' })
  }, [send])

  // AudioRecorder 回调：发送音频数据到后端
  const handleAudioData = useCallback((base64: string) => {
    send({ type: 'audio', data: base64 })
  }, [send])

  // Camera 截图回调：发送图片到后端
  const handleCameraFrame = useCallback((base64: string) => {
    send({ type: 'image', data: base64 })
  }, [send])

  // AudioRecorder 回调：更新 VAD 状态 + Barge-in 打断 + 通知后端 + 触发截图
  const handleVADStateChange = useCallback((state: VADState) => {
    setVadStatus(state as VADStatus)
    // Barge-in：用户开始说话时立即停止 TTS 播放并清空队列
    if (state === 'speaking') {
      audioPlayer.stop()
    }
    // 通知后端VAD状态（关键！后端依赖此消息启动/停止ASR会话）
    send({ type: 'vad_status', speaking: state === 'speaking' })
    // VAD检测到说话时触发Camera截图
    if (state === 'speaking') {
      setShouldCapture(true)
      setTimeout(() => setShouldCapture(false), 100)
    }
  }, [send])

  const hasMessages = messages.length > 0 || !!currentAIResponse

  return (
    <div className="h-screen flex flex-col bg-gray-900">
      {/* 顶部标题栏 */}
      <header className="h-12 flex items-center px-4 bg-gray-800 border-b border-gray-700 flex-shrink-0">
        <div className="w-7 h-7 rounded-lg bg-blue-600 flex items-center justify-center mr-3">
          <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
          </svg>
        </div>
        <h1 className="text-base font-semibold text-gray-100">XEngineer - AI 视觉对话助手</h1>
      </header>

      {/* 主内容区 */}
      <main className="flex-1 flex overflow-hidden">
        {/* 左侧：摄像头区域 */}
        <div className="w-1/2 p-4 flex flex-col items-center justify-center border-r border-gray-700">
          <div className="w-full max-w-md">
            <Camera onFrame={handleCameraFrame} triggerCapture={shouldCapture} />
          </div>
          <button
            onClick={sendTest}
            className="mt-4 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm text-white transition-colors"
          >
            发送测试消息
          </button>
          {/* 录音控制 */}
          <div className="mt-4">
            <AudioRecorder
              onAudioData={handleAudioData}
              onVADStateChange={handleVADStateChange}
            />
          </div>
        </div>

        {/* 右侧：对话区域 */}
        <div className="w-1/2 flex flex-col">
          {/* 对话消息列表 */}
          <div
            ref={chatContainerRef}
            className="flex-1 overflow-y-auto p-4"
          >
            {!hasMessages && (
              <div className="h-full flex flex-col items-center justify-center text-gray-500">
                <svg className="w-16 h-16 mb-4 text-gray-700" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M8.625 12a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H8.25m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H12m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0h-.375M21 12c0 4.556-4.03 8.25-9 8.25a9.764 9.764 0 01-2.555-.337A5.972 5.972 0 015.41 20.97a5.969 5.969 0 01-.474-.065 4.48 4.48 0 00.978-2.025c.09-.457-.133-.901-.467-1.226C3.93 16.178 3 14.189 3 12c0-4.556 4.03-8.25 9-8.25s9 3.694 9 8.25z" />
                </svg>
                <p className="text-sm mb-1">暂无对话</p>
                <p className="text-xs text-gray-600">点击左侧"发送测试消息"或通过语音开始对话</p>
              </div>
            )}

            {hasMessages && (
              <>
                {messages.map(msg => (
                  <ChatBubble key={msg.id} message={msg} />
                ))}
                <StreamingMessage content={currentAIResponse} />
              </>
            )}

            {/* 滚动锚点 */}
            <div ref={chatEndRef} />
          </div>

          {/* 底部提示 */}
          <div className="p-3 border-t border-gray-700 flex-shrink-0">
            <p className="text-xs text-gray-600 text-center">语音输入已就绪，点击左侧"开始录音"进行对话</p>
          </div>
        </div>
      </main>

      {/* 底部状态栏 + 音频播放指示 */}
      <StatusBar
        connectionStatus={status}
        vadStatus={vadStatus}
        isAIProcessing={isAIProcessing}
        audioElement={
          <AudioPlayer
            isPlaying={false}
            onPlayStateChange={() => {}}
          />
        }
      />
    </div>
  )
}

export default App