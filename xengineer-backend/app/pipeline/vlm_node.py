"""VLM+LLM Pipeline 节点

接收 ASR 识别文本和最新截图，构建多模态 prompt，
调用 Agnes API 进行流式文本生成，同时：
- 逐 chunk 推送 llm_chunk 给前端实时显示
- 积累完整句子后通过 send_to_next() 传给 TTS 节点进行语音合成
"""

import logging

from app.pipeline.base import PipelineNode
from app.services.agnes_client import AgnesClient

logger = logging.getLogger(__name__)


class VLMNode(PipelineNode):
    """VLM+LLM Pipeline 节点 - 视觉理解 + 文本生成"""

    SYSTEM_PROMPT = (
        "你是一个 AI 视觉对话助手。用户通过摄像头向你展示他们看到的世界，并用语音与你交流。\n"
        "请结合画面内容和用户的问题，给出准确、简洁、友好的回答。\n"
        "如果用户的问题与画面无关，正常回答即可。\n"
        "回答请简短，适合语音播报（避免过长的段落）。"
    )

    def __init__(self, agnes_client: AgnesClient, max_history_rounds: int = 5):
        """
        初始化 VLM 节点

        Args:
            agnes_client: Agnes API 客户端实例
            max_history_rounds: 保留的最近对话轮数（默认 5 轮，即 10 条消息）
        """
        super().__init__("VLM+LLM")
        self.agnes = agnes_client
        self.conversation_history: list[dict] = []
        self.max_history_rounds = max_history_rounds
        self._latest_image_url: str | None = None

    async def process(self, data: dict) -> dict:
        """处理 ASR 文本 + 图片，调用 VLM/LLM

        Args:
            data: 包含以下字段的字典
                - text: ASR 识别的用户语音文本
                - image_url: 可选，当前帧截图的公网 URL

        Returns:
            包含 LLM 完整回复文本和所用图片 URL 的字典
        """
        text = data.get("text", "")
        # 兼容 ASR 传来的 "image" 和外部传入的 "image_url"
        raw_image = data.get("image_url") or data.get("image") or self._latest_image_url
        image_url = self._normalize_image(raw_image) if raw_image else None

        if not text:
            return data

        # 构建用户消息（多模态 content）
        user_content: list[dict] = [{"type": "text", "text": text}]
        if image_url:
            user_content.append(
                {"type": "image_url", "image_url": {"url": image_url}}
            )

        user_msg = {"role": "user", "content": user_content}

        # 追加到对话历史
        self.conversation_history.append(user_msg)

        # 裁剪历史，只保留最近 N 轮（每轮 = user + assistant 两条）
        max_messages = self.max_history_rounds * 2
        if len(self.conversation_history) > max_messages:
            self.conversation_history = self.conversation_history[-max_messages:]

        # 构建完整消息列表：system + 历史
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            *self.conversation_history,
        ]

        # 流式调用 Agnes，同时触发 chunk 和 sentence 回调
        full_response = ""
        try:
            async for chunk in self.agnes.chat_stream(
                messages=messages,
                on_chunk=self._on_chunk,
                on_sentence=self._on_sentence,
            ):
                full_response += chunk
        except Exception as e:
            logger.error(f"VLM 流式调用异常: {e}", exc_info=True)
            if self.orchestrator:
                await self.orchestrator.send_to_frontend({
                    "type": "error",
                    "message": f"AI 回复生成失败: {e}",
                })
            return {"text": "", "image_url": image_url}

        # 将 AI 完整回复写入对话历史
        if full_response:
            self.conversation_history.append({
                "role": "assistant",
                "content": full_response,
            })

        return {"text": full_response, "image_url": image_url}

    async def _on_chunk(self, chunk: str):
        """LLM 文本 chunk → 推送给前端实时显示"""
        if self.orchestrator:
            await self.orchestrator.send_to_frontend({
                "type": "llm_chunk",
                "text": chunk,
            })

    async def _on_sentence(self, sentence: str):
        """完整句子 → 传给下游 TTS 节点"""
        await self.send_to_next({"text": sentence})

    def update_image(self, image_data: str):
        """更新最新的图片（由 Orchestrator 在收到截图时调用）

        支持两种格式：
        - 公网 URL（http/https 开头）直接存储
        - base64 原始数据自动包装为 data URI（修复 D2）

        Args:
            image_data: 图片 URL 或 base64 编码的 JPEG 图片
        """
        self._latest_image_url = self._normalize_image(image_data)

    @staticmethod
    def _normalize_image(image_data: str) -> str:
        """将图片数据标准化为 VLM 可用的 URL

        - 如果已经是 data URI 或 http URL，直接返回
        - 如果是 raw base64，包装为 data:image/jpeg;base64,... 格式
        """
        if image_data.startswith(("data:", "http://", "https://")):
            return image_data
        # 修复 D2：raw base64 → VLM 可识别的 data URI
        return f"data:image/jpeg;base64,{image_data}"

    def clear_history(self):
        """清除对话历史"""
        self.conversation_history.clear()