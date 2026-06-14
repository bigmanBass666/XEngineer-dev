"""Pipeline 编排器

负责将 ASR → VLM+LLM → TTS 节点串联成完整的处理流水线，
并管理与前端 WebSocket 的通信。

VAD 驱动的 ASR 会话生命周期:
    vad_status speaking=true  → start_session() → 接收 audio → ASR 识别
    vad_status speaking=false → stop_session()  → ASR 最终结果 → VLM → TTS
"""

from __future__ import annotations

import logging
from typing import Optional

from fastapi import WebSocket

from app.pipeline.base import PipelineNode

logger = logging.getLogger("xengineer")


class PipelineOrchestrator:
    """Pipeline 编排器 - 串联 ASR → VLM+LLM → TTS

    职责:
        1. 构建节点链路
        2. 根据 VAD 信号管理 ASR 会话生命周期
        3. 维护最新截图引用
        4. 将节点输出路由到前端 WebSocket
        5. 错误隔离：单个节点失败不影响其他功能
    """

    def __init__(self):
        self.asr_node: Optional[PipelineNode] = None
        self.vlm_node: Optional[PipelineNode] = None
        self.tts_node: Optional[PipelineNode] = None
        self.ws_connection: Optional[WebSocket] = None

        # VAD 驱动的状态
        self._session_active: bool = False
        self._latest_image: Optional[str] = None  # base64 JPEG

    # ------------------------------------------------------------------
    # 构建
    # ------------------------------------------------------------------

    def build(self, asr: PipelineNode, vlm: PipelineNode, tts: PipelineNode):
        """构建 Pipeline 链: asr → vlm → tts

        Args:
            asr: ASR（语音识别）节点
            vlm: VLM+LLM（视觉语言模型+大语言模型）节点
            tts: TTS（文本转语音）节点
        """
        asr.set_next(vlm)
        vlm.set_next(tts)
        # 注入 orchestrator 引用，使节点可直接与前端通信
        asr.orchestrator = self
        vlm.orchestrator = self
        tts.orchestrator = self
        self.asr_node = asr
        self.vlm_node = vlm
        self.tts_node = tts

    # ------------------------------------------------------------------
    # WebSocket 连接管理
    # ------------------------------------------------------------------

    def set_ws_connection(self, ws: WebSocket):
        """绑定前端 WebSocket 连接"""
        self.ws_connection = ws

    async def send_to_frontend(self, msg: dict):
        """发送消息给前端

        Args:
            msg: 要发送的 JSON 消息字典
        """
        if self.ws_connection:
            try:
                await self.ws_connection.send_json(msg)
            except Exception as e:
                logger.warning(f"send_to_frontend failed: {e}")

    # ------------------------------------------------------------------
    # 消息处理入口（由 main.py 调用）
    # ------------------------------------------------------------------

    async def handle_audio(self, audio_data: str):
        """处理前端发来的音频

        仅在 ASR 会话激活时转发音频数据。

        Args:
            audio_data: Base64 编码的 PCM 音频
        """
        if not self._session_active:
            return
        if self.asr_node is None:
            logger.warning("handle_audio called but pipeline not built")
            return
        try:
            await self.asr_node.process({"audio": audio_data})
        except Exception as e:
            logger.error(f"ASR node error: {e}", exc_info=True)
            await self.send_to_frontend({
                "type": "error",
                "message": f"语音识别出错: {e}",
            })

    async def handle_image(self, image_data: str):
        """处理前端发来的截图

        保存最新的 base64 JPEG 图片，并传递给 VLM 节点实现多模态理解。

        Args:
            image_data: Base64 编码的 JPEG 图片
        """
        self._latest_image = image_data
        # 将 base64 图片传入 VLM 节点（修复 D1：之前未调用，VLM 始终无图）
        if self.vlm_node and hasattr(self.vlm_node, "update_image"):
            self.vlm_node.update_image(image_data)
        logger.debug("Latest screenshot updated and sent to VLM node")

    async def handle_vad_status(self, speaking: bool):
        """处理前端 VAD 状态变化

        speaking=true  → 启动 ASR 会话（如未启动）
        speaking=false → 结束 ASR 会话，触发最终识别 → VLM → TTS 链路

        Args:
            speaking: 是否正在说话
        """
        if speaking and not self._session_active:
            await self._start_asr_session()
        elif not speaking and self._session_active:
            await self._stop_asr_session()

    # ------------------------------------------------------------------
    # ASR 会话生命周期（VAD 驱动）
    # ------------------------------------------------------------------

    async def _start_asr_session(self):
        """启动 ASR 会话"""
        if self.asr_node is None:
            logger.warning("Cannot start ASR session: pipeline not built")
            return

        self._session_active = True

        # 如果 ASR 节点有 start_session 方法（真实节点），调用它
        if hasattr(self.asr_node, "start_session"):
            try:
                await self.asr_node.start_session()
                logger.info("ASR session started (real node)")
            except Exception as e:
                logger.error(f"ASR start_session failed: {e}", exc_info=True)
                self._session_active = False
                await self.send_to_frontend({
                    "type": "error",
                    "message": f"语音识别启动失败: {e}",
                })
        else:
            logger.info("ASR session started (stub node)")

        await self.send_to_frontend({
            "type": "status",
            "message": "asr_session_started",
        })

    async def _stop_asr_session(self):
        """结束 ASR 会话，触发最终识别结果 → VLM → TTS"""
        self._session_active = False

        if hasattr(self.asr_node, "stop_session"):
            try:
                await self.asr_node.stop_session()
                logger.info("ASR session stopped (real node)")
            except Exception as e:
                logger.error(f"ASR stop_session failed: {e}", exc_info=True)
                await self.send_to_frontend({
                    "type": "error",
                    "message": f"语音识别结束异常: {e}",
                })
        else:
            logger.info("ASR session stopped (stub node)")

        await self.send_to_frontend({
            "type": "status",
            "message": "asr_session_stopped",
        })

    # ------------------------------------------------------------------
    # 清理（WS 断开时调用）
    # ------------------------------------------------------------------

    async def cleanup(self):
        """清理资源：停止 ASR 会话、关闭客户端连接"""
        logger.info("Orchestrator cleanup")

        # 停止可能正在运行的 ASR 会话
        if self._session_active:
            self._session_active = False
            if self.asr_node and hasattr(self.asr_node, "stop_session"):
                try:
                    await self.asr_node.stop_session()
                except Exception:
                    pass

        # 关闭 Agnes 客户端（如果 VLM 节点持有一个）
        if self.vlm_node and hasattr(self.vlm_node, "agnes"):
            try:
                await self.vlm_node.agnes.close()
            except Exception:
                pass

        # 重置状态
        self.ws_connection = None
        self._latest_image = None