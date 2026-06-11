/**
 * Agnes AI LLM 封装
 * OpenAI Chat Completions 兼容格式
 */

interface ChatMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

interface LLMResponse {
  content: string;
  usage?: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
}

export async function chatCompletion(
  messages: ChatMessage[],
  options?: {
    temperature?: number;
    max_tokens?: number;
    stream?: boolean;
  }
): Promise<LLMResponse> {
  const baseUrl = process.env.LLM_BASE_URL || '';
  const apiKey = process.env.LLM_API_KEY || '';
  const model = process.env.LLM_MODEL || 'agnes-2.0-flash';

  const response = await fetch(`${baseUrl}/chat/completions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${apiKey}`,
    },
    body: JSON.stringify({
      model,
      messages,
      temperature: options?.temperature ?? 0.7,
      max_tokens: options?.max_tokens ?? 2048,
      stream: options?.stream ?? false,
    }),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`LLM API error: ${response.status} - ${error}`);
  }

  const data = await response.json();
  return {
    content: data.choices[0]?.message?.content || '',
    usage: data.usage,
  };
}

/**
 * 流式输出的 SSE 解析
 */
export async function* streamChatCompletion(
  messages: ChatMessage[],
  options?: {
    temperature?: number;
    max_tokens?: number;
  }
): AsyncGenerator<string> {
  const baseUrl = process.env.LLM_BASE_URL || '';
  const apiKey = process.env.LLM_API_KEY || '';
  const model = process.env.LLM_MODEL || 'agnes-2.0-flash';

  const response = await fetch(`${baseUrl}/chat/completions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${apiKey}`,
    },
    body: JSON.stringify({
      model,
      messages,
      temperature: options?.temperature ?? 0.7,
      max_tokens: options?.max_tokens ?? 2048,
      stream: true,
    }),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`LLM API error: ${response.status} - ${error}`);
  }

  const reader = response.body?.getReader();
  if (!reader) throw new Error('No response body');

  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop() || '';

    for (const line of lines) {
      if (line.startsWith('data: ') && line !== 'data: [DONE]') {
        try {
          const json = JSON.parse(line.slice(6));
          const content = json.choices[0]?.delta?.content;
          if (content) yield content;
        } catch {
          // skip malformed chunks
        }
      }
    }
  }
}
