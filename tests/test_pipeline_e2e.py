#!/usr/bin/env python3
"""XEngineer Pipeline 端到端测试

测试完整链路：WebSocket → ASR → VLM+LLM → TTS → 音频输出

用法: python3 tests/test_pipeline_e2e.py

不需要真实麦克风/摄像头 — 用合成数据模拟：
  - 音频：生成一段 16kHz PCM 正弦波（模拟说话声）
  - 图片：生成一张带文字的测试图片（模拟摄像头截图）
"""

import asyncio
import json
import base64
import struct
import sys
import os
import time
from pathlib import Path

WS_URL = os.environ.get("WS_URL", "wss://xengineer-dev-production.up.railway.app/ws")

# ============ 合成数据生成 ============

def generate_sine_pcm(duration_ms: int = 1000, freq: int = 440, sample_rate: int = 16000) -> bytes:
    """生成正弦波 PCM 音频（16bit mono）— 模拟一段语音"""
    import math
    n_samples = int(sample_rate * duration_ms / 1000)
    samples = []
    for i in range(n_samples):
        envelope = min(1.0, i / (sample_rate * 0.05)) * min(1.0, (n_samples - i) / (sample_rate * 0.05))
        val = int(16000 * envelope * math.sin(2 * math.pi * freq * i / sample_rate))
        val = max(-32768, min(32767, val))
        samples.append(struct.pack('<h', val))
    return b''.join(samples)


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


async def run_pipeline_test():
    """完整 pipeline 端到端测试"""
    import websockets

    results = TestResults()

    print("=" * 50)
    print("XEngineer Pipeline 端到端测试")
    print(f"目标: {WS_URL}")
    print(f"时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    # 生成合成数据
    print("\n[准备] 生成合成测试数据...")
    pcm_data = generate_sine_pcm(duration_ms=800, freq=440)
    image_base64 = generate_test_image_base64()
    print(f"  音频: {len(pcm_data)} bytes PCM ({len(pcm_data)//32}ms @16kHz)")
    print(f"  图片: {len(image_base64)} chars base64 JPEG")

    # WebSocket 连接
    print(f"\n[测试1] WebSocket 连接...")
    try:
        ws = await websockets.connect(WS_URL, open_timeout=10)
        results.ok("WebSocket 连接成功")
    except Exception as e:
        results.fail("WebSocket 连接", str(e))
        return results.summary()

    # 收集消息
    received = []
    receive_done = asyncio.Event()

    async def receiver():
        try:
            async for msg in ws:
                received.append(json.loads(msg))
                if len(received) >= 30:
                    break
        except websockets.exceptions.ConnectionClosed:
            pass
        receive_done.set()

    recv_task = asyncio.create_task(receiver())

    # 测试2: Echo
    print(f"\n[测试2] Echo 消息...")
    await ws.send(json.dumps({"type": "test", "data": "pipeline-e2e-test"}))
    await asyncio.sleep(2)
    echo_found = any(
        m.get("type") == "status" and "pipeline-e2e-test" in m.get("message", "")
        for m in received
    )
    if echo_found:
        results.ok("Echo 消息返回正确")
    else:
        results.fail("Echo 消息", f"未收到 echo 响应, received={len(received)}")

    # 测试3: VAD 会话启动
    print(f"\n[测试3] VAD 会话启动 (vad_status: speaking=true)...")
    await ws.send(json.dumps({"type": "vad_status", "speaking": True}))
    await asyncio.sleep(3)
    session_started = any(
        m.get("type") == "status" and "asr_session_started" in m.get("message", "")
        for m in received
    )
    if session_started:
        results.ok("ASR 会话启动成功")
    else:
        results.fail("ASR 会话启动", f"未收到 asr_session_started, received={len(received)}")

    # 测试4: 发送图片
    print(f"\n[测试4] 发送测试图片...")
    await ws.send(json.dumps({"type": "image", "data": image_base64}))
    await asyncio.sleep(1)
    results.ok("图片发送完成（无 crash 即通过）")

    # 测试5: 发送音频数据
    print(f"\n[测试5] 发送合成音频 (440Hz 正弦波, 800ms)...")
    chunk_size = len(pcm_data) // 5
    for i in range(5):
        chunk = pcm_data[i * chunk_size : (i + 1) * chunk_size]
        chunk_b64 = base64.b64encode(chunk).decode('utf-8')
        await ws.send(json.dumps({"type": "audio", "data": chunk_b64}))
        await asyncio.sleep(0.3)
    print("  5 个音频分片已发送")
    await asyncio.sleep(2)
    results.ok("音频数据发送完成（无 crash 即通过）")

    # 测试6: VAD 会话结束 → 触发 ASR → VLM → TTS
    print(f"\n[测试6] VAD 会话结束 → 触发完整 pipeline...")
    await ws.send(json.dumps({"type": "vad_status", "speaking": False}))
    print("  等待 pipeline 响应（最长 30 秒）...")

    try:
        await asyncio.wait_for(receive_done.wait(), timeout=30)
    except asyncio.TimeoutError:
        recv_task.cancel()

    await asyncio.sleep(2)

    # 分析 pipeline 输出
    print(f"\n[分析] 收到 {len(received)} 条消息")
    msg_types = [m.get("type") for m in received]
    type_counts = dict((t, msg_types.count(t)) for t in set(msg_types))
    print(f"  消息类型分布: {type_counts}")

    # 测试7: ASR 结果
    print(f"\n[测试7] ASR 识别结果...")
    asr_msgs = [m for m in received if m.get("type") in ("asr_interim", "asr_final")]
    if asr_msgs:
        for m in asr_msgs[-3:]:  # 显示最后3条
            print(f"  ASR [{m['type']}]: {m.get('text', '')[:100]}")
        results.ok(f"ASR 返回 {len(asr_msgs)} 条识别结果")
    else:
        results.fail("ASR 识别", "未收到 ASR 结果（正弦波非真实语音，可能无法识别）")

    # 测试8: LLM 回复
    print(f"\n[测试8] VLM+LLM 回复...")
    llm_msgs = [m for m in received if m.get("type") == "llm_chunk"]
    if llm_msgs:
        full_text = ''.join(m.get("text", "") for m in llm_msgs)
        print(f"  LLM 回复 ({len(full_text)} chars): {full_text[:200]}")
        results.ok(f"VLM+LLM 返回 {len(llm_msgs)} 个 chunk")
    else:
        results.fail("VLM+LLM 回复", "未收到 LLM chunk（ASR 无文本导致链路中断）")

    # 测试9: TTS 音频
    print(f"\n[测试9] TTS 音频输出...")
    tts_msgs = [m for m in received if m.get("type") == "tts_audio"]
    if tts_msgs:
        total_len = sum(len(m.get("data", "")) for m in tts_msgs)
        print(f"  TTS 返回 {len(tts_msgs)} 个音频分片, 总计 {total_len} chars base64")
        try:
            decoded = base64.b64decode(tts_msgs[0].get("data", "")[:100])
            print(f"  音频数据前缀: {decoded[:4].hex()}")
            results.ok("TTS 返回有效音频数据")
        except Exception as e:
            results.fail("TTS 音频解码", str(e))
    else:
        results.fail("TTS 音频", "未收到 TTS 音频")

    # 测试10: 错误检查
    print(f"\n[测试10] 后端错误检查...")
    error_msgs = [m for m in received if m.get("type") == "error"]
    if error_msgs:
        for m in error_msgs:
            print(f"  ⚠️ Error: {m.get('message', 'unknown')}")
        results.fail("后端错误", f"收到 {len(error_msgs)} 条错误消息")
    else:
        results.ok("无后端错误")

    # 保存日志
    log_dir = Path(__file__).resolve().parent.parent / "download"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "pipeline-test-log.json"
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "ws_url": WS_URL,
            "messages": received,
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
