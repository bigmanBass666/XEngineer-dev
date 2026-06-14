"""TTS Pipeline 节点

将 LLM 输出的文本通过火山 TTS 2.0 合成为语音，
并实时推送给前端播放。
"""

import base64

from app.pipeline.base import PipelineNode
from app.services.volcengine_tts import VolcengineTTS


class TTSNode(PipelineNode):
    """TTS Pipeline 节点 - 文本转语音

    接收上游节点传入的文本数据，调用火山 TTS API 合成音频，
    将 base64 编码的音频通过 WebSocket 推送给前端。
    """

    def __init__(self, config):
        super().__init__("TTS")
        self.config = config
        self.tts_client = VolcengineTTS(access_token=config.VOLCENGINE_ACCESS_TOKEN)

    async def process(self, data: dict) -> dict:
        """将文本转为语音并推送给前端

        Args:
            data: 包含 'text' 字段的数据字典

        Returns:
            原样返回 data（TTS 结果通过 orchestrator 异步推送）
        """
        text = data.get("text", "")
        if not text:
            return data

        audio_bytes = await self.tts_client.synthesize(text)
        if audio_bytes and self.orchestrator:
            audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
            await self.orchestrator.send_to_frontend({
                "type": "tts_audio",
                "data": audio_base64,
            })
            await self.orchestrator.send_to_frontend({
                "type": "tts_end",
            })

        return data
