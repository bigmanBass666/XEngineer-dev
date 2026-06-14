"""火山 TTS 2.0 HTTP 客户端

通过火山引擎 OpenSpeech API 实现文本转语音。
API 文档: https://www.volcengine.com/docs/6561/1161849
"""

import uuid
import httpx
import base64
from typing import Optional


class VolcengineTTS:
    """火山 TTS 2.0 HTTP 客户端

    使用 httpx 异步客户端调用火山引擎 Seed TTS 2.0 API，
    将文本合成为 MP3/WAV/PCM 音频并返回原始字节。
    """

    API_URL = "https://openspeech.bytedance.com/api/v3/tts/unidirectional"
    RESOURCE_ID = "seed-tts-2.0"
    DEFAULT_SPEAKER = "zh_female_vv_uranus_bigtts"  # Vivi 2.0

    def __init__(self, access_token: str):
        """初始化 TTS 客户端

        Args:
            access_token: 火山引擎 Access Token，用于 X-Api-Key 认证
        """
        self.access_token = access_token
        self.client = httpx.AsyncClient(timeout=30.0)

    async def synthesize(
        self,
        text: str,
        speaker: str = DEFAULT_SPEAKER,
        format: str = "mp3",
        sample_rate: int = 24000,
        speech_rate: int = 0,
    ) -> Optional[bytes]:
        """文本转语音

        Args:
            text: 要合成的文本
            speaker: 音色 ID（默认 Vivi 2.0）
            format: 音频格式（mp3 / pcm / wav）
            sample_rate: 采样率（8000 / 16000 / 24000）
            speech_rate: 语速调节（-50 ~ 100，0 为正常）

        Returns:
            音频数据 bytes，失败返回 None
        """
        headers = {
            "X-Api-Key": self.access_token,
            "X-Api-Resource-Id": self.RESOURCE_ID,
            "X-Api-Request-Id": str(uuid.uuid4()),
            "Content-Type": "application/json",
        }

        payload = {
            "req_params": {
                "text": text,
                "speaker": speaker,
                "audio_params": {
                    "format": format,
                    "sample_rate": sample_rate,
                    "bit_rate": 128000,
                    "speech_rate": speech_rate,
                    "loudness_rate": 0,
                },
            }
        }

        try:
            resp = await self.client.post(
                self.API_URL,
                json=payload,
                headers=headers,
            )
            resp.raise_for_status()
            data = resp.json()

            if data.get("code") != 3000:
                print(f"[TTS Error] code={data.get('code')}, msg={data.get('message')}")
                return None

            audio_base64 = data.get("data", "")
            if not audio_base64:
                print("[TTS Error] No audio data in response")
                return None

            return base64.b64decode(audio_base64)
        except Exception as e:
            print(f"[TTS Error] {e}")
            return None

    async def close(self):
        """关闭异步 HTTP 客户端"""
        await self.client.aclose()
