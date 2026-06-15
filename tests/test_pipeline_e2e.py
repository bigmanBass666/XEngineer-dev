#!/usr/bin/env python3
"""XEngineer Pipeline 端到端测试

测试完整链路：WebSocket → ASR → VLM+LLM → TTS → 音频输出

用法: python3 tests/test_pipeline_e2e.py

不需要真实麦克风/摄像头 — 用合成数据模拟：
  - 音频：通过沙箱 TTS (z-ai tts) 合成真实中文语音，再 ffmpeg 重采样至 16kHz
  - 图片：生成一张带文字的测试图片（模拟摄像头截图）
  - 回退：如果 z-ai 或 ffmpeg 不可用，降级为正弦波（ASR 无法识别，仅验证连通性）
"""

import asyncio
import json
import base64
import struct
import subprocess
import sys
import os
import time
import shutil
import tempfile
from pathlib import Path

WS_URL = os.environ.get("WS_URL", "wss://xengineer-dev-production.up.railway.app/ws")

# ============ 测试数据集 ============

TEST_UTTERANCES = [
    {
        "id": 1,
        "text": "你好，请介绍一下你自己",
        "keywords": ["你好", "介绍"],
        "description": "基础对话",
    },
    {
        "id": 2,
        "text": "你看到了什么？",
        "keywords": ["看到"],
        "description": "触发 VLM 视觉描述",
    },
    {
        "id": 3,
        "text": "画面中有几个人？",
        "keywords": ["几个"],
        "description": "VLM 计数能力",
    },
    {
        "id": 4,
        "text": "请用中文回答",
        "keywords": ["中文"],
        "description": "语言控制",
    },
    {
        "id": 5,
        "text": "谢谢，再见",
        "keywords": ["谢谢", "再见"],
        "description": "结束对话",
    },
]

# ============ 工具可用性检测 ============

def _check_tool(name: str) -> bool:
    """检测命令行工具是否可用"""
    return shutil.which(name) is not None

TTS_AVAILABLE = _check_tool("z-ai")
FFMPEG_AVAILABLE = _check_tool("ffmpeg")

# ============ 音频合成 ============

def synthesize_tts_pcm(text: str, voice: str = "tongtong", sample_rate: int = 16000) -> bytes:
    """通过 z-ai TTS 合成真实语音，ffmpeg 重采样到目标采样率，返回 raw PCM bytes

    流程: z-ai tts (24kHz WAV) → ffmpeg resample → raw PCM (s16le)

    Args:
        text: 要合成的文本（上限 1024 字符）
        voice: TTS 声音名称
        sample_rate: 目标采样率（默认 16000，匹配后端 ASR 期望）

    Returns:
        16-bit little-endian mono PCM bytes

    Raises:
        RuntimeError: TTS 合成或 ffmpeg 处理失败
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        wav_path = os.path.join(tmpdir, "tts_output.wav")
        pcm_path = os.path.join(tmpdir, "tts_resampled.pcm")

        # Step 1: TTS 合成
        try:
            result = subprocess.run(
                ["z-ai", "tts", "-i", text, "-o", wav_path, "--format", "wav", "-v", voice],
                capture_output=True, text=True, timeout=60,
            )
            if result.returncode != 0:
                raise RuntimeError(f"z-ai tts failed (rc={result.returncode}): {result.stderr}")
            if not os.path.exists(wav_path) or os.path.getsize(wav_path) == 0:
                raise RuntimeError("z-ai tts produced empty/missing output")
        except FileNotFoundError:
            raise RuntimeError("z-ai CLI not found")
        except subprocess.TimeoutExpired:
            raise RuntimeError("z-ai tts timed out")

        # Step 2: ffmpeg 重采样到目标采样率，输出 raw PCM
        try:
            result = subprocess.run(
                [
                    "ffmpeg", "-i", wav_path,
                    "-ar", str(sample_rate), "-ac", "1",
                    "-f", "s16le", "-y", pcm_path,
                ],
                capture_output=True, text=True, timeout=30,
            )
            if result.returncode != 0:
                raise RuntimeError(f"ffmpeg failed (rc={result.returncode}): {result.stderr}")
            if not os.path.exists(pcm_path) or os.path.getsize(pcm_path) == 0:
                raise RuntimeError("ffmpeg produced empty/missing output")
        except FileNotFoundError:
            raise RuntimeError("ffmpeg not found")
        except subprocess.TimeoutExpired:
            raise RuntimeError("ffmpeg timed out")

        with open(pcm_path, "rb") as f:
            return f.read()


def generate_sine_pcm(duration_ms: int = 1000, freq: int = 440, sample_rate: int = 16000) -> bytes:
    """生成正弦波 PCM 音频（16bit mono）— 降级方案，ASR 无法识别"""
    import math
    n_samples = int(sample_rate * duration_ms / 1000)
    samples = []
    for i in range(n_samples):
        envelope = min(1.0, i / (sample_rate * 0.05)) * min(1.0, (n_samples - i) / (sample_rate * 0.05))
        val = int(16000 * envelope * math.sin(2 * math.pi * freq * i / sample_rate))
        val = max(-32768, min(32767, val))
        samples.append(struct.pack('<h', val))
    return b''.join(samples)


def get_test_pcm(text: str) -> tuple[bytes, bool]:
    """获取测试音频 PCM 数据

    优先使用 TTS 合成语音，不可用时降级为正弦波。

    Returns:
        (pcm_bytes, is_real_voice)
    """
    if TTS_AVAILABLE and FFMPEG_AVAILABLE:
        try:
            pcm = synthesize_tts_pcm(text)
            duration_ms = len(pcm) / 2 / 16000 * 1000  # 16bit = 2 bytes/sample
            print(f"    TTS 合成成功: {len(pcm)} bytes PCM ({duration_ms:.0f}ms @16kHz)")
            return pcm, True
        except RuntimeError as e:
            print(f"    ⚠️ TTS 合成失败，降级为正弦波: {e}")

    pcm = generate_sine_pcm(duration_ms=800, freq=440)
    print(f"    降级正弦波: {len(pcm)} bytes PCM ({len(pcm)//32}ms @16kHz)")
    return pcm, False


def generate_test_image_base64() -> str:
    """生成一张简单的测试图片，返回 base64 JPEG"""
    try:
        from PIL import Image, ImageDraw
        img = Image.new('RGB', (640, 480), color=(73, 109, 137))
        draw = ImageDraw.Draw(img)
        draw.text((50, 50), "XEngineer Test Image", fill=(255, 255, 255))
        draw.text((50, 100), f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}", fill=(200, 200, 200))
        draw.rectangle([20, 20, 620, 460], outline=(255, 255, 255), width=2)
        import io
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=85)
        return base64.b64encode(buf.getvalue()).decode('utf-8')
    except ImportError:
        minimal_jpeg = bytes([
            0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46, 0x00, 0x01,
            0x01, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00, 0x00, 0xFF, 0xDB, 0x00, 0x43,
            0x00, 0x08, 0x06, 0x06, 0x07, 0x06, 0x05, 0x08, 0x07, 0x07, 0x07, 0x09,
            0x09, 0x08, 0x0A, 0x0C, 0x14, 0x0D, 0x0C, 0x0B, 0x0B, 0x0C, 0x19, 0x12,
            0x13, 0x0F, 0x14, 0x1D, 0x1A, 0x1F, 0x1E, 0x1D, 0x1A, 0x1C, 0x1C, 0x20,
            0x24, 0x2E, 0x27, 0x20, 0x22, 0x2C, 0x23, 0x1C, 0x1C, 0x28, 0x37, 0x29,
            0x2C, 0x30, 0x31, 0x34, 0x34, 0x34, 0x1F, 0x27, 0x39, 0x3D, 0x38, 0x32,
            0x3C, 0x2E, 0x33, 0x34, 0x32, 0xFF, 0xC0, 0x00, 0x0B, 0x08, 0x00, 0x01,
            0x00, 0x01, 0x01, 0x01, 0x11, 0x00, 0xFF, 0xC4, 0x00, 0x1F, 0x00, 0x00,
            0x01, 0x05, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08,
            0x09, 0x0A, 0x0B, 0xFF, 0xDA, 0x00, 0x08, 0x01, 0x01, 0x00, 0x00, 0x3F,
            0x00, 0x7B, 0x40, 0x1B, 0xFF, 0xD9,
        ])
        return base64.b64encode(minimal_jpeg).decode('utf-8')


# ============ 测试结果收集 ============

class TestResults:
    def __init__(self):
        self.messages = []
        self.errors = []
        self.passed = 0
        self.failed = 0

    def ok(self, test_name):
        self.passed += 1
        print(f"  ✅ {test_name}")

    def fail(self, test_name, reason=""):
        self.failed += 1
        self.errors.append((test_name, reason))
        print(f"  ❌ {test_name}: {reason}")

    def skip(self, test_name, reason=""):
        self.passed += 1  # skip 不算失败
        print(f"  ⏭️  {test_name}: {reason}")

    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'='*50}")
        print(f"测试结果: {self.passed}/{total} 通过")
        if self.errors:
            print(f"\n失败项:")
            for name, reason in self.errors:
                print(f"  - {name}: {reason}")
        print(f"{'='*50}")
        return self.failed == 0


# ============ 单次 Pipeline 会话 ============

async def run_single_utterance(ws, utterance: dict, image_base64: str, results: TestResults) -> list[dict]:
    """对单条测试语句执行一次完整的 VAD → ASR → VLM → TTS 会话

    Args:
        ws: 已连接的 WebSocket
        utterance: 测试语句 dict (id, text, keywords, description)
        image_base64: base64 JPEG 图片
        results: TestResults 收集器

    Returns:
        本次会话收到的所有消息列表
    """
    uid = utterance["id"]
    text = utterance["text"]
    keywords = utterance["keywords"]
    desc = utterance["description"]

    print(f"\n{'─'*50}")
    print(f"[测试语句 #{uid}] \"{text}\" — {desc}")
    print(f"{'─'*50}")

    # 收集本次会话的消息
    session_msgs: list[dict] = []
    receive_done = asyncio.Event()

    async def receiver():
        try:
            async for msg in ws:
                session_msgs.append(json.loads(msg))
                if len(session_msgs) >= 50:
                    break
        except Exception:
            pass
        receive_done.set()

    recv_task = asyncio.create_task(receiver())

    # Step 1: VAD 开始说话（triggers ASR session start + camera snapshot）
    await ws.send(json.dumps({"type": "vad_status", "speaking": True}))
    await asyncio.sleep(0.5)  # Brief wait for ASR session to initialize
    session_started = any(
        m.get("type") == "status" and "asr_session_started" in m.get("message", "")
        for m in session_msgs
    )
    if session_started:
        results.ok(f"#{uid} ASR 会话启动")
    else:
        results.fail(f"#{uid} ASR 会话启动", "未收到 asr_session_started")

    # Step 2: 发送图片（simulates camera snapshot triggered by VAD）
    await ws.send(json.dumps({"type": "image", "data": image_base64}))

    # Step 3: 合成语音并发送（1024B chunks at 32ms intervals, matching ScriptProcessorNode(512)）
    pcm_data, is_real = get_test_pcm(text)
    chunk_size = 1024  # 512 samples × 2 bytes (matches ScriptProcessorNode(512) output)
    n_chunks = len(pcm_data) // chunk_size
    for i in range(n_chunks):
        chunk = pcm_data[i * chunk_size : (i + 1) * chunk_size]
        chunk_b64 = base64.b64encode(chunk).decode('utf-8')
        await ws.send(json.dumps({"type": "audio", "data": chunk_b64}))
        await asyncio.sleep(0.032)  # 32ms between chunks (matches ScriptProcessorNode rate)
    # Handle remaining bytes
    remaining = pcm_data[n_chunks * chunk_size:]
    if remaining:
        chunk_b64 = base64.b64encode(remaining).decode('utf-8')
        await ws.send(json.dumps({"type": "audio", "data": chunk_b64}))
    print(f"    {n_chunks + (1 if remaining else 0)} 个音频分片已发送 (每片 {chunk_size} bytes @32ms)")

    # Brief pause after audio to let last chunks process
    await asyncio.sleep(0.5)

    # Step 4: VAD 停止说话（triggers ASR final recognition → VLM → TTS）
    await ws.send(json.dumps({"type": "vad_status", "speaking": False}))
    print(f"    等待 pipeline 响应（最长 35 秒）...")

    try:
        await asyncio.wait_for(receive_done.wait(), timeout=35)
    except asyncio.TimeoutError:
        recv_task.cancel()

    await asyncio.sleep(1)

    # Step 5: 分析结果
    print(f"    收到 {len(session_msgs)} 条消息")

    # 5a: ASR 识别
    asr_finals = [m for m in session_msgs if m.get("type") == "asr_final"]
    asr_interims = [m for m in session_msgs if m.get("type") == "asr_interim"]

    if asr_finals:
        final_text = asr_finals[-1].get("text", "")
        print(f"    ASR final: \"{final_text}\"")
        # 检查关键词匹配
        matched = any(kw in final_text for kw in keywords)
        if matched:
            results.ok(f"#{uid} ASR 识别正确 (关键词匹配)")
        elif is_real:
            # 真实语音但关键词不匹配，记录但不算严重失败
            results.fail(f"#{uid} ASR 关键词匹配", f"识别=\"{final_text}\", 期望含 {keywords}")
        else:
            results.skip(f"#{uid} ASR 关键词匹配", "降级正弦波，ASR 无法识别")
    elif asr_interims:
        last_interim = asr_interims[-1].get("text", "")
        print(f"    ASR interim (无 final): \"{last_interim}\"")
        if is_real:
            results.fail(f"#{uid} ASR final 结果", f"仅有 interim=\"{last_interim}\"，无 final")
        else:
            results.skip(f"#{uid} ASR 识别", "降级正弦波，ASR 无法识别")
    else:
        if is_real:
            results.fail(f"#{uid} ASR 识别", "未收到任何 ASR 结果")
        else:
            results.skip(f"#{uid} ASR 识别", "降级正弦波，ASR 无法识别")

    # 5b: LLM 回复
    llm_msgs = [m for m in session_msgs if m.get("type") == "llm_chunk"]
    if llm_msgs:
        full_text = ''.join(m.get("text", "") for m in llm_msgs)
        print(f"    LLM 回复 ({len(full_text)} chars): {full_text[:150]}...")
        results.ok(f"#{uid} VLM+LLM 回复")
    else:
        results.fail(f"#{uid} VLM+LLM 回复", "未收到 LLM chunk（ASR 无文本导致链路中断）")

    # 5c: TTS 音频
    tts_msgs = [m for m in session_msgs if m.get("type") == "tts_audio"]
    if tts_msgs:
        total_b64 = sum(len(m.get("data", "")) for m in tts_msgs)
        print(f"    TTS 音频: {len(tts_msgs)} 片, {total_b64} chars base64")
        results.ok(f"#{uid} TTS 音频输出")
    else:
        results.fail(f"#{uid} TTS 音频", "未收到 TTS 音频")

    # 5d: 错误检查
    error_msgs = [m for m in session_msgs if m.get("type") == "error"]
    if error_msgs:
        for m in error_msgs:
            print(f"    ⚠️ Error: {m.get('message', 'unknown')}")
        results.fail(f"#{uid} 后端错误", f"收到 {len(error_msgs)} 条错误")
    else:
        results.ok(f"#{uid} 无后端错误")

    return session_msgs


# ============ 主测试入口 ============

async def run_pipeline_test():
    """完整 pipeline 端到端测试"""
    import websockets

    results = TestResults()

    print("=" * 50)
    print("XEngineer Pipeline 端到端测试 (TTS 合成语音版)")
    print(f"目标: {WS_URL}")
    print(f"时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"z-ai TTS: {'✅ 可用' if TTS_AVAILABLE else '❌ 不可用'}")
    print(f"ffmpeg:   {'✅ 可用' if FFMPEG_AVAILABLE else '❌ 不可用'}")
    voice_mode = "TTS 合成语音" if (TTS_AVAILABLE and FFMPEG_AVAILABLE) else "⚠️ 降级正弦波"
    print(f"音频模式: {voice_mode}")
    print(f"测试语句: {len(TEST_UTTERANCES)} 条")
    print("=" * 50)

    # 生成测试图片
    print("\n[准备] 生成测试图片...")
    image_base64 = generate_test_image_base64()
    print(f"  图片: {len(image_base64)} chars base64 JPEG")

    # WebSocket 连接
    print(f"\n[连接] WebSocket...")
    try:
        ws = await websockets.connect(WS_URL, open_timeout=10)
        results.ok("WebSocket 连接成功")
    except Exception as e:
        results.fail("WebSocket 连接", str(e))
        return results.summary()

    # Echo 测试
    print(f"\n[Echo] 连通性测试...")
    echo_received = []
    echo_done = asyncio.Event()

    async def echo_receiver():
        try:
            async for msg in ws:
                echo_received.append(json.loads(msg))
                echo_done.set()
                break
        except Exception:
            pass

    echo_task = asyncio.create_task(echo_receiver())
    await ws.send(json.dumps({"type": "test", "data": "pipeline-e2e-tts-test"}))
    try:
        await asyncio.wait_for(echo_done.wait(), timeout=5)
    except asyncio.TimeoutError:
        echo_task.cancel()

    echo_found = any(
        m.get("type") == "status" and "pipeline-e2e-tts-test" in m.get("message", "")
        for m in echo_received
    )
    if echo_found:
        results.ok("Echo 消息返回正确")
    else:
        results.fail("Echo 消息", f"未收到 echo 响应")

    # 逐条执行测试语句
    all_session_msgs = []
    for utt in TEST_UTTERANCES:
        session_msgs = await run_single_utterance(ws, utt, image_base64, results)
        all_session_msgs.extend(session_msgs)
        # 会话间隔，避免后端状态污染
        await asyncio.sleep(2)

    # 保存完整日志
    log_dir = Path(__file__).resolve().parent.parent / "download"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "pipeline-test-log.json"
    msg_types_all = [m.get("type") for m in all_session_msgs]
    type_counts = dict((t, msg_types_all.count(t)) for t in set(msg_types_all))
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "ws_url": WS_URL,
            "voice_mode": voice_mode,
            "messages": all_session_msgs,
            "summary": {
                "passed": results.passed,
                "failed": results.failed,
                "msg_types": type_counts,
            }
        }, f, ensure_ascii=False, indent=2)
    print(f"\n[日志] 已保存: {log_file}")

    try:
        await ws.close()
    except Exception:
        pass

    return results.summary()


if __name__ == "__main__":
    try:
        import websockets
    except ImportError:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "websockets", "-q"])
        import websockets

    success = asyncio.run(run_pipeline_test())
    sys.exit(0 if success else 1)