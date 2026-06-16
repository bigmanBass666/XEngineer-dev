"""XEngineer FastAPI 入口

提供 WebSocket 端点、健康检查和 CORS 配置。
通过环境变量 USE_REAL_NODES 控制使用真实节点还是 Stub 节点。
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.pipeline.base import PipelineNode
from app.pipeline.orchestrator import PipelineOrchestrator

# 预生成的 0.5 秒静音 MP3（24kHz mono, 788 bytes）
# 用于 TTS stub 节点发送真实可解码的 mp3 给前端
_STUB_SILENCE_MP3_BASE64 = (
    "SUQzBAAAAAAAIlRTU0UAAAAOAAADTGF2ZjYxLjcuMTAyAAAAAAAAAAAAAAD/84TAAAAAAAAAAAAASW5m"
    "bwAAAA8AAAAXAAAC6ABKSkpKUlJSUlpaWlpaY2NjY2tra2tzc3Nzc3t7e3uEhISEjIyMjIyUlJSUnJyc"
    "nKWlpaWlra2trbW1tbW9vb29vcbGxsbOzs7O1tbW1tbe3t7e5+fn5+/v7+/v9/f39/////8AAAAATGF2"
    "YzYxLjE5AAAAAAAAAAAAAAAAJAKgAAAAAAAAAuhmdbRPAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD/8xTE"
    "AAAAA0gAAAAATEFNRTMuMTAwVVX/8xTECwAAA0gAAAAAVVVVVVVVVVVVVVX/8xTEFgAAA0gAAAAAVVVV"
    "VVVVVVVVVVX/8xTEIQAAA0gAAAAAVVVVVVVVVVVVVVX/8xTELAAAA0gAAAAAVVVVVVVVVVVVVVX/8xTE"
    "NwAAA0gAAAAAVVVVVVVVVVVVVVX/8xTEQgAAA0gAAAAAVVVVVVVVVVVVVVX/8xTETQAAA0gAAAAAVVVV"
    "VVVVVVVVVVX/8xTEWAAAA0gAAAAAVVVVVVVVVVVVVVX/8xTEYwAAA0gAAAAAVVVVVVVVVVVVVVX/8xTE"
    "bgAAA0gAAAAAVVVVVVVVVVVVVVX/8xTEeQAAA0gAAAAAVVVVVVVVVVVVVVX/8xTEhAAAA0gAAAAAVVVV"
    "VVVVVVVVVVX/8xTEjwAAA0gAAAAAVVVVVVVVVVVVVVX/8xTEmgAAA0gAAAAAVVVVVVVVVVVVVVX/8xTE"
    "pQAAA0gAAAAAVVVVVVVVVVVVVVX/8xTEsAAAA0gAAAAAVVVVVVVVVVVVVVX/8xTEuwAAA0gAAAAAVVVV"
    "VVVVVVVVVVX/8xTExgAAA0gAAAAAVVVVVVVVVVVVVVX/8xTE0QAAA0gAAAAAVVVVVVVVVVVVVVX/8xTE"
    "3AAAA0gAAAAAVVVVVVVVVVVVVVX/8xTE5wAAA0gAAAAAVVVVVVVVVVVVVVX/8xTE8gAAA0gAAAAAVVVV"
    "VVVVVVVVVVU="
)

logger = logging.getLogger("xengineer")

# 创建全局编排器实例
orchestrator = PipelineOrchestrator()

USE_REAL = settings.USE_REAL_NODES


def _mask_secret(value: str) -> str:
    """隐藏敏感信息的中间部分"""
    if not value:
        return "(empty)"
    if len(value) <= 8:
        return "****"
    return value[:4] + "****" + value[-4:]


def _print_config_status():
    """启动时打印配置状态（隐藏敏感信息）"""
    print("=" * 50)
    print("XEngineer Backend - Configuration Status")
    print("=" * 50)
    print(f"  USE_REAL_NODES:     {USE_REAL}")
    print(f"  AGNES_API_Key:      {_mask_secret(settings.AGNES_API_Key)}")
    print(f"  VOLCENGINE_APP_ID:   {_mask_secret(settings.VOLCENGINE_APP_ID)}")
    print(f"  VOLCENGINE_ACCESS_TOKEN: {_mask_secret(settings.VOLCENGINE_ACCESS_TOKEN)}")
    print(f"  VOLCENGINE_SECRET_KEY: {_mask_secret(settings.VOLCENGINE_SECRET_KEY)}")
    print("=" * 50)


# ------------------------------------------------------------------
# Stub Pipeline 节点（开发模式）
# ------------------------------------------------------------------


class StubASRNode(PipelineNode):
    """Stub ASR 节点 — 发送 asr_final 给前端并触发下游链路

    与真实 ASR 不同，stub ASR 不会在每帧音频时触发链路，
    而是由 orchestrator._stop_asr_session() 调用 process({}) 时
    才触发最终识别 → VLM → TTS 完整链路。
    """

    async def process(self, data: dict) -> dict:
        # 音频帧时仅消费，不触发链路（模拟真实 ASR 行为）
        if data.get("audio"):
            return data

        # 收到空 data（来自 _stop_asr_session），触发最终识别
        text = "[ASR stub] 识别结果"
        if self.orchestrator:
            await self.orchestrator.send_to_frontend({
                "type": "asr_final",
                "text": text,
            })
        await self.send_to_next({"text": text})
        return data


class StubVLMNode(PipelineNode):
    """Stub VLM+LLM 节点 — 发送 llm_chunk 给前端并传递给 TTS"""

    async def process(self, data: dict) -> dict:
        text = data.get("text", "")
        if not text:
            return data

        response = "[VLM stub] AI 回复"
        if self.orchestrator:
            await self.orchestrator.send_to_frontend({
                "type": "llm_chunk",
                "text": response,
            })
        await self.send_to_next({"text": response})
        return data


class StubTTSNode(PipelineNode):
    """Stub TTS 节点 — 发送真实静音 MP3 给前端验证播放链路"""

    async def process(self, data: dict) -> dict:
        text = data.get("text", "")
        if not text:
            return data

        if self.orchestrator:
            await self.orchestrator.send_to_frontend({
                "type": "tts_audio",
                "data": _STUB_SILENCE_MP3_BASE64,
            })
            await self.orchestrator.send_to_frontend({
                "type": "tts_end",
            })
        return data


def _build_pipeline():
    """根据 USE_REAL_NODES 构建真实或 Stub Pipeline"""
    if USE_REAL:
        from app.pipeline.asr_node import ASRNode
        from app.pipeline.vlm_node import VLMNode
        from app.pipeline.tts_node import TTSNode
        from app.services.agnes_client import AgnesClient

        agnes = AgnesClient()
        asr = ASRNode(config=settings)
        vlm = VLMNode(agnes_client=agnes)
        tts = TTSNode(config=settings)
        logger.info("Pipeline built with REAL nodes (ASR → VLM+LLM → TTS)")
        return asr, vlm, tts
    else:
        asr = StubASRNode("ASR-Stub")
        vlm = StubVLMNode("VLM-Stub")
        tts = StubTTSNode("TTS-Stub")
        logger.info("Pipeline built with STUB nodes (development mode, sends frontend messages)")
        return asr, vlm, tts


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    _print_config_status()

    # 构建 Pipeline
    asr, vlm, tts = _build_pipeline()
    orchestrator.build(asr, vlm, tts)

    yield

    # 应用关闭时清理：停止 ASR 会话，然后关闭全局 agnes client
    try:
        await orchestrator.cleanup()
    except Exception:
        pass
    if USE_REAL and orchestrator.vlm_node and hasattr(orchestrator.vlm_node, "agnes"):
        try:
            await orchestrator.vlm_node.agnes.close()
        except Exception:
            pass


app = FastAPI(
    title="XEngineer Backend",
    description="XEngineer 语音交互后端服务",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS 中间件 - 开发阶段允许所有 origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "ok", "service": "xengineer-backend"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket 端点 - 前端通过此端点与 Pipeline 交互

    接收消息类型:
    - {"type": "audio", "data": "<base64 PCM>"}
        → 转发给 ASR 节点（仅 VAD speaking 时）
    - {"type": "image", "data": "<base64 JPEG>"}
        → 更新最新截图（当前纯文本模式，暂不传入 VLM）
    - {"type": "vad_status", "speaking": true/false}
        → 控制 ASR 会话生命周期
    - {"type": "test", "data": "..."}
        → 连通性测试

    发送消息类型:
    - asr_interim / asr_final / llm_chunk / tts_audio / tts_end
    - status / error
    """
    await websocket.accept()
    orchestrator.set_ws_connection(websocket)
    logger.info("WebSocket client connected")

    try:
        while True:
            message = await websocket.receive_json()
            msg_type = message.get("type")

            if msg_type == "audio":
                audio_data = message.get("data", "")
                if audio_data:
                    await orchestrator.handle_audio(audio_data)
                else:
                    await orchestrator.send_to_frontend({
                        "type": "error",
                        "message": "Empty audio data received",
                    })

            elif msg_type == "image":
                image_data = message.get("data", "")
                if image_data:
                    await orchestrator.handle_image(image_data)

            elif msg_type == "vad_status":
                speaking = message.get("speaking", False)
                await orchestrator.handle_vad_status(speaking)

            elif msg_type == "test":
                await orchestrator.send_to_frontend({
                    "type": "status",
                    "message": f"WS echo: {message.get('data', '')}",
                })

            else:
                await orchestrator.send_to_frontend({
                    "type": "error",
                    "message": f"Unknown message type: {msg_type}",
                })

    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.close(code=1011, reason=str(e))
        except Exception:
            pass
    finally:
        await orchestrator.cleanup()