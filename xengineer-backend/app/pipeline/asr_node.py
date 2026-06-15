"""ASR Pipeline 节点

负责接收前端发来的 base64 编码 PCM 音频，
通过火山 Seed-ASR 2.0 实时识别为文本，
并将识别结果传递给下游 VLM+LLM 节点。
"""

from __future__ import annotations

import asyncio
import base64
from typing import Optional

from app.pipeline.base import PipelineNode
from app.services.volcengine_asr import VolcengineASR


class ASRNode(PipelineNode):
    """ASR Pipeline 节点 - 语音识别

    生命周期:
        start_session() → 多次 process(data) → stop_session()
    """

    def __init__(self, config):
        super().__init__("ASR")
        self.config = config
        self.asr_client: Optional[VolcengineASR] = None
        self._receive_task: Optional[asyncio.Task] = None
        self._latest_image: Optional[str] = None
        self.current_text: str = ""

    # ------------------------------------------------------------------
    # 会话生命周期
    # ------------------------------------------------------------------

    async def start_session(self):
        """启动 ASR 会话：创建客户端、建连、启动接收循环"""
        self.current_text = ""
        self._latest_image = None

        self.asr_client = VolcengineASR(
            app_id=self.config.VOLCENGINE_APP_ID,
            access_token=self.config.VOLCENGINE_ACCESS_TOKEN,
        )
        self.asr_client.on_interim = self._on_interim
        self.asr_client.on_result = self._on_final

        await self.asr_client.connect()

        # 在后台启动接收循环
        self._receive_task = asyncio.create_task(
            self.asr_client.receive_loop(), name="asr-receive"
        )

    async def stop_session(self):
        """结束 ASR 会话：先让 close() 发送 is_last 并等结果，再清理

        顺序很重要：
        1. 调用 asr_client.close() 发送 is_last=True 结束包、等待最终识别结果、关闭 ws
        2. receive_loop 在 ws 关闭后收到 ConnectionClosed 自然退出
        3. 若 receive_loop 未退出，超时后取消
        """
        # 1. 先关闭 ASR 客户端（发 is_last + 等最终结果 + 关 ws）
        if self.asr_client:
            await self.asr_client.close()
            self.asr_client = None

        # 2. receive_loop 在 ws 关闭后会自然退出（ConnectionClosed）
        if self._receive_task and not self._receive_task.done():
            try:
                await asyncio.wait_for(self._receive_task, timeout=3.0)
            except asyncio.TimeoutError:
                self._receive_task.cancel()
                try:
                    await self._receive_task
                except asyncio.CancelledError:
                    pass
        self._receive_task = None

    # ------------------------------------------------------------------
    # PipelineNode.process
    # ------------------------------------------------------------------

    async def process(self, data: dict) -> dict:
        """处理音频数据（由 orchestrator 调用）

        Args:
            data: {"audio": "base64_pcm", "image": "url|base64"}（可选）
        """
        if data.get("audio") and self.asr_client:
            pcm_bytes = base64.b64decode(data["audio"])
            await self.asr_client.send_audio(pcm_bytes)

        if data.get("image"):
            self._latest_image = data["image"]

        return data

    # ------------------------------------------------------------------
    # ASR 回调
    # ------------------------------------------------------------------

    async def _on_interim(self, text: str):
        """中间识别结果 - 推送给前端展示（不打断流水线）"""
        self.current_text = text
        if self.orchestrator:
            await self.orchestrator.send_to_frontend({
                "type": "asr_interim",
                "text": text,
            })

    async def _on_final(self, text: str):
        """最终识别结果 - 推送给前端并传递给下游节点"""
        self.current_text = text
        if self.orchestrator:
            await self.orchestrator.send_to_frontend({
                "type": "asr_final",
                "text": text,
            })
        # 将文本和最新的图像信息传递给下一个节点（VLM+LLM）
        await self.send_to_next({
            "text": text,
            "image": self._latest_image,
        })
