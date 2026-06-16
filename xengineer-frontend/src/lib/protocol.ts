// 前端 → 后端消息类型
export interface ClientMessage {
  type: 'audio' | 'image' | 'vad_status' | 'test'
  data?: string  // base64 编码的数据
  speaking?: boolean  // VAD 状态
}

// 后端 → 前端消息类型
export type ServerMessage = 
  | { type: 'asr_interim'; text: string }
  | { type: 'asr_final'; text: string }
  | { type: 'llm_chunk'; text: string }
  | { type: 'tts_audio'; data: string }  // base64 mp3
  | { type: 'tts_end' }
  | { type: 'status'; message: string }
  | { type: 'error'; message: string }

// 对话消息（UI 显示用）
export interface ChatMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: number
}

// 连接状态
export type ConnectionStatus = 'disconnected' | 'connecting' | 'connected' | 'error'

// VAD 状态
export type VADStatus = 'silent' | 'speaking'