import type { ChatMessage } from '../lib/protocol'

interface ChatBubbleProps {
  message: ChatMessage
}

export function ChatBubble({ message }: ChatBubbleProps) {
  const isUser = message.role === 'user'
  const isSystem = message.role === 'system'

  // 系统消息样式
  if (isSystem) {
    return (
      <div className="flex justify-center mb-3">
        <div className="max-w-[80%] px-4 py-2 rounded-xl text-xs text-gray-400 bg-gray-800 border border-gray-700 text-center">
          {message.content}
        </div>
      </div>
    )
  }

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-3`}>
      {!isUser && (
        <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-xs font-bold mr-2 flex-shrink-0">
          AI
        </div>
      )}
      <div
        className={`max-w-[75%] px-4 py-2.5 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap break-words ${
          isUser
            ? 'bg-blue-600 text-white rounded-br-sm'
            : 'bg-gray-700 text-gray-100 rounded-bl-sm'
        }`}
      >
        {message.content}
      </div>
    </div>
  )
}