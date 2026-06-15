"""Agnes Text API 客户端 - 支持多模态流式调用

支持 OpenAI 兼容格式的 chat completions API，包括：
- SSE 流式调用（chat_stream）
- 非流式调用（chat）
- 多模态消息构建（文本 + 图片 URL）
- 句子级分割回调（用于触发 TTS）
"""

import httpx
import json
import logging
from typing import AsyncGenerator, Optional

from app.config import settings

logger = logging.getLogger(__name__)


class AgnesClient:
    """Agnes Text API 客户端"""

    API_URL = "https://apihub.agnes-ai.com/v1/chat/completions"
    DEFAULT_MODEL = "agnes-2.0-flash"

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化 Agnes 客户端

        Args:
            api_key: API Key，若不传则从 Settings 自动读取
        """
        self.api_key = api_key or settings.AGNES_API_Key
        self.client = httpx.AsyncClient(timeout=60.0)

        if not self.api_key:
            logger.warning("Agnes API Key 未配置，API 调用将会失败")

    async def chat_stream(
        self,
        messages: list[dict],
        on_chunk: Optional[callable] = None,
        on_sentence: Optional[callable] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> AsyncGenerator[str, None]:
        """
        流式调用 Agnes API（SSE）

        Args:
            messages: OpenAI 格式的消息列表，支持多模态（文本+图片URL）
            on_chunk: 每收到一个 text chunk 时的回调
            on_sentence: 积累到完整句子（遇到 。！？.!?）时的回调
            model: 模型名称，默认 agnes-2.0-flash
            temperature: 生成温度
            max_tokens: 最大 token 数

        Yields:
            每个 text chunk
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": model or self.DEFAULT_MODEL,
            "messages": messages,
            "stream": True,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        sentence_buffer = ""
        sentence_delimiters = "。！？.!?"

        try:
            async with self.client.stream("POST", self.API_URL, json=payload, headers=headers) as resp:
                resp.raise_for_status()

                async for line in resp.aiter_lines():
                    if not line.startswith("data: "):
                        continue

                    data_str = line[6:]
                    if data_str == "[DONE]":
                        # 流结束，处理 buffer 中剩余文本
                        if sentence_buffer.strip() and on_sentence:
                            await on_sentence(sentence_buffer.strip())
                        break

                    try:
                        data = json.loads(data_str)
                        delta = data["choices"][0].get("delta", {})
                        content = delta.get("content", "")

                        if content:
                            sentence_buffer += content

                            # 触发 chunk 回调
                            if on_chunk:
                                await on_chunk(content)

                            # 检查句子边界，分割出完整句子
                            for delimiter in sentence_delimiters:
                                if delimiter in sentence_buffer:
                                    parts = sentence_buffer.split(delimiter, 1)
                                    sentence = (parts[0] + delimiter).strip()
                                    if sentence and on_sentence:
                                        await on_sentence(sentence)
                                    sentence_buffer = parts[1]
                                    break

                            yield content

                    except (json.JSONDecodeError, KeyError, IndexError) as e:
                        logger.debug(f"跳过无法解析的 SSE 行: {e}")
                        continue

        except httpx.HTTPStatusError as e:
            body = await e.response.aread()
            logger.error(f"Agnes API HTTP 错误 (stream): {e.response.status_code} - {body.decode(errors='replace')}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Agnes API 请求异常: {e}")
            raise

    async def chat(
        self,
        messages: list[dict],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> str:
        """
        非流式调用 Agnes API

        Args:
            messages: OpenAI 格式的消息列表，支持多模态
            model: 模型名称
            temperature: 生成温度
            max_tokens: 最大 token 数

        Returns:
            模型生成的完整文本
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": model or self.DEFAULT_MODEL,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        try:
            resp = await self.client.post(self.API_URL, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
        except httpx.HTTPStatusError as e:
            body = await e.response.aread()
            logger.error(f"Agnes API HTTP 错误 (chat): {e.response.status_code} - {body.decode(errors='replace')}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Agnes API 请求异常: {e}")
            raise

    @staticmethod
    def build_vision_message(text: str, image_url: str) -> dict:
        """
        构建多模态消息（文本 + 图片 URL）

        Args:
            text: 文本提示
            image_url: 图片的公网可访问 URL

        Returns:
            OpenAI 格式的 content 列表消息
        """
        return {
            "role": "user",
            "content": [
                {"type": "text", "text": text},
                {
                    "type": "image_url",
                    "image_url": {"url": image_url},
                },
            ],
        }

    async def close(self):
        """关闭 HTTP 客户端连接"""
        await self.client.aclose()
