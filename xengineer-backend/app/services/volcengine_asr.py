"""火山 Seed-ASR 2.0 二进制 WebSocket 协议客户端

通过火山引擎 OpenSpeech API 实现流式语音识别。
使用 bigmodel_async 模式（结果变化时才返回，RTF 最优）。
协议文档: https://www.volcengine.com/docs/6561/1161814
"""

import asyncio
import gzip
import json
import struct
import uuid
from typing import Optional, Callable, Awaitable

import websockets


class VolcengineASR:
    """火山 Seed-ASR 2.0 客户端（二进制 WebSocket 协议）

    协议帧格式:
        Header (4 bytes) + PayloadSize (4 bytes) + Payload

    Header 字节布局（每字段 4 bit）:
        Byte 0: version(4bit) | header_size(4bit)
        Byte 1: message_type(4bit) | flags(4bit)
        Byte 2: serialization(4bit) | compression(4bit)
        Byte 3: reserved(8bit)
    """

    # bigmodel_async 模式：结果变化时才返回，RTF 最优
    WS_URL = "wss://openspeech.bytedance.com/api/v3/sauc/bigmodel_async"
    RESOURCE_ID = "volc.seedasr.sauc.duration"

    # ---- Message Types ----
    MSG_FULL_CLIENT_REQUEST = 0x01
    MSG_AUDIO_ONLY = 0x02
    MSG_SERVER_RESPONSE = 0x09
    MSG_ERROR = 0x0F

    # ---- Flags ----
    FLAG_NO_SEQUENCE = 0x00
    FLAG_POSITIVE_SEQ = 0x01
    FLAG_LAST_NO_SEQ = 0x02
    FLAG_NEGATIVE_SEQ_LAST = 0x03

    # ---- Serialization ----
    SER_NONE = 0x00
    SER_JSON = 0x01

    # ---- Compression ----
    COMP_NONE = 0x00
    COMP_GZIP = 0x01

    def __init__(self, app_id: str, access_token: str):
        """初始化 ASR 客户端

        Args:
            app_id: 火山引擎 App ID
            access_token: 火山引擎 Access Token
        """
        self.app_id = app_id
        self.access_token = access_token
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self.on_result: Optional[Callable[[str], Awaitable[None]]] = None
        self.on_interim: Optional[Callable[[str], Awaitable[None]]] = None

    # ------------------------------------------------------------------
    # Header / 帧构造
    # ------------------------------------------------------------------

    def _build_header(
        self,
        msg_type: int,
        flags: int,
        serialization: int = 0,
        compression: int = 0,
    ) -> bytes:
        """构造 4 字节协议头

        Byte 0: version=0001 | header_size=0001 => 0x11
        Byte 1: message_type(高4位) | flags(低4位)
        Byte 2: serialization(高4位) | compression(低4位)
        Byte 3: reserved => 0x00
        """
        byte0 = 0x11  # version=1, header_size=1（单位为4字节）
        byte1 = (msg_type << 4) | (flags & 0x0F)
        byte2 = (serialization << 4) | (compression & 0x0F)
        byte3 = 0x00
        return bytes([byte0, byte1, byte2, byte3])

    def _build_full_client_request(self) -> bytes:
        """构造 full client request（建连后的第一个消息）

        包含用户信息、音频参数和模型配置。
        """
        payload = json.dumps({
            "user": {"uid": "xengineer_user"},
            "audio": {
                "format": "pcm",
                "rate": 16000,
                "bits": 16,
                "channel": 1,
            },
            "request": {
                "model_name": "bigmodel",
                "enable_nonstream": True,   # 二遍识别
                "enable_itn": True,          # 逆文本正则化（数字/日期等）
                "enable_punc": True,         # 标点符号
                "enable_ddc": True,          # 语义顺滑
                "ssd_version": "200",
                "result_type": "full",
                "end_window_size": 800,      # VAD 判停 800ms
            },
        }).encode("utf-8")

        compressed = gzip.compress(payload)
        header = self._build_header(
            msg_type=self.MSG_FULL_CLIENT_REQUEST,
            flags=self.FLAG_NO_SEQUENCE,
            serialization=self.SER_JSON,
            compression=self.COMP_GZIP,
        )
        payload_size = struct.pack(">I", len(compressed))
        return header + payload_size + compressed

    def _build_audio_packet(self, pcm_data: bytes, is_last: bool = False) -> bytes:
        """构造 audio only request（音频数据帧）

        Args:
            pcm_data: PCM 音频原始字节（16kHz, 16bit, mono）
            is_last: 是否为最后一包（触发服务端最终识别）
        """
        compressed = gzip.compress(pcm_data) if pcm_data else b""
        flags = self.FLAG_LAST_NO_SEQ if is_last else self.FLAG_NO_SEQUENCE
        header = self._build_header(
            msg_type=self.MSG_AUDIO_ONLY,
            flags=flags,
            serialization=self.SER_NONE,
            compression=self.COMP_GZIP,
        )
        payload_size = struct.pack(">I", len(compressed))
        return header + payload_size + compressed

    # ------------------------------------------------------------------
    # 响应解析
    # ------------------------------------------------------------------

    def _parse_response(self, data: bytes) -> dict:
        """解析服务端响应帧

        Returns:
            包含 error/is_last/result 等字段的字典
        """
        if len(data) < 4:
            return {"error": True, "message": "Response too short"}

        header = data[:4]
        msg_type = (header[1] >> 4) & 0x0F
        flags = header[1] & 0x0F
        is_last = flags in (self.FLAG_LAST_NO_SEQ, self.FLAG_NEGATIVE_SEQ_LAST)

        # ---- 错误响应 ----
        if msg_type == self.MSG_ERROR:
            # error 帧格式: header(4) + error_code(4) + error_msg_size(4) + error_msg
            if len(data) < 12:
                return {"error": True, "message": "Malformed error response"}
            error_code = struct.unpack(">I", data[4:8])[0]
            error_size = struct.unpack(">I", data[8:12])[0]
            error_msg = data[12 : 12 + error_size].decode("utf-8", errors="replace")
            return {"error": True, "code": error_code, "message": error_msg}

        if msg_type != self.MSG_SERVER_RESPONSE:
            return {"error": True, "message": f"Unknown message type: 0x{msg_type:02X}"}

        # ---- 正常响应: header(4) + sequence(4) + payload_size(4) + payload ----
        if len(data) < 12:
            return {"error": True, "message": "Malformed server response"}

        compression = header[2] & 0x0F
        payload_size = struct.unpack(">I", data[8:12])[0]
        compressed_payload = data[12 : 12 + payload_size]

        try:
            if compression == self.COMP_GZIP:
                payload = gzip.decompress(compressed_payload).decode("utf-8")
            else:
                payload = compressed_payload.decode("utf-8")
            result = json.loads(payload)
            return {"error": False, "is_last": is_last, **result}
        except Exception as e:
            return {"error": True, "message": f"Parse error: {e}"}

    # ------------------------------------------------------------------
    # 连接管理
    # ------------------------------------------------------------------

    async def connect(self):
        """建立 WebSocket 连接并发送 full client request"""
        headers = {
            "X-Api-App-Key": self.app_id,
            "X-Api-Access-Key": self.access_token,
            "X-Api-Resource-Id": self.RESOURCE_ID,
            "X-Api-Request-Id": str(uuid.uuid4()),
            "X-Api-Connect-Id": str(uuid.uuid4()),
        }
        self.ws = await websockets.connect(self.WS_URL, additional_headers=headers)
        # 发送 full client request 完成握手
        await self.ws.send(self._build_full_client_request())

    async def send_audio(self, pcm_data: bytes, is_last: bool = False):
        """发送音频数据

        Args:
            pcm_data: PCM 音频字节（16kHz, 16bit, mono）
            is_last: 是否为最后一包
        """
        if self.ws:
            await self.ws.send(self._build_audio_packet(pcm_data, is_last))

    async def receive_loop(self):
        """接收响应循环（应在后台任务中运行）

        根据回调函数分发 interim / final 结果。
        """
        if not self.ws:
            return
        async for data in self.ws:
            result = self._parse_response(data)
            if result.get("error"):
                print(f"[ASR Error] {result.get('message', result)}")
                continue

            text = result.get("result", {}).get("text", "")
            if not text:
                continue

            is_last = result.get("is_last", False)
            if is_last and self.on_result:
                await self.on_result(text)
            elif not is_last and self.on_interim:
                await self.on_interim(text)

    async def close(self):
        """发送结束信号并关闭连接

        1. 发送空音频包（is_last=True）通知服务端音频结束
        2. 等待最终识别结果
        3. 关闭 WebSocket 连接
        """
        if not self.ws:
            return

        # 发送空音频包作为结束信号
        await self.send_audio(b"", is_last=True)

        # 等待最终结果
        try:
            data = await asyncio.wait_for(self.ws.recv(), timeout=5.0)
            result = self._parse_response(data)
            if not result.get("error") and self.on_result:
                text = result.get("result", {}).get("text", "")
                if text:
                    await self.on_result(text)
        except asyncio.TimeoutError:
            pass
        except Exception as e:
            print(f"[ASR Warning] Error receiving final result: {e}")

        await self.ws.close()
        self.ws = None
