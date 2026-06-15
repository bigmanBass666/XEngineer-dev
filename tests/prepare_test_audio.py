#!/usr/bin/env python3
"""预合成测试音频集 → tests/fixtures/test_audio_set.json

功能：
  1. 调用沙箱 z-ai tts CLI 合成 5 条中文测试语音
  2. ffmpeg 重采样至 16kHz mono PCM (s16le)
  3. base64 编码（s16le + float32 两种格式）
  4. 输出 tests/fixtures/test_audio_set.json

降级：z-ai tts 或 ffmpeg 不可用时用正弦波替代，is_real = false

用法：
  python3 tests/prepare_test_audio.py          # 缓存复用
  python3 tests/prepare_test_audio.py --force  # 强制重新合成
"""

import argparse
import base64
import json
import math
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import time
from pathlib import Path

# ============ 常量 ============

SCRIPT_DIR = Path(__file__).resolve().parent
FIXTURES_DIR = SCRIPT_DIR / "fixtures"
OUTPUT_FILE = FIXTURES_DIR / "test_audio_set.json"

TARGET_SAMPLE_RATE = 16000
NUM_CHANNELS = 1
BITS_PER_SAMPLE = 16
TTS_VOICE = "tongtong"

TEST_UTTERANCES = [
    {"id": 1, "text": "你好，请介绍一下你自己", "keywords": ["你好", "介绍"]},
    {"id": 2, "text": "你看到了什么？", "keywords": ["看到"]},
    {"id": 3, "text": "画面中有几个人？", "keywords": ["几个"]},
    {"id": 4, "text": "请用中文回答", "keywords": ["中文"]},
    {"id": 5, "text": "谢谢，再见", "keywords": ["谢谢", "再见"]},
]


# ============ 工具检测 ============

def _check_tool(name: str) -> bool:
    """检测命令行工具是否可用"""
    return shutil.which(name) is not None


# ============ 音频合成 ============

def synthesize_tts_pcm(text: str, voice: str = TTS_VOICE, sample_rate: int = TARGET_SAMPLE_RATE) -> bytes:
    """通过 z-ai TTS 合成真实语音，ffmpeg 重采样到目标采样率，返回 raw PCM bytes (s16le)"""
    with tempfile.TemporaryDirectory() as tmpdir:
        wav_path = os.path.join(tmpdir, "tts_output.wav")
        pcm_path = os.path.join(tmpdir, "tts_resampled.pcm")

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


def generate_sine_pcm(duration_ms: int = 1000, freq: int = 440, sample_rate: int = TARGET_SAMPLE_RATE) -> bytes:
    """生成正弦波 PCM 音频（16bit mono）— 降级方案"""
    n_samples = int(sample_rate * duration_ms / 1000)
    samples = []
    for i in range(n_samples):
        envelope = min(1.0, i / (sample_rate * 0.05)) * min(1.0, (n_samples - i) / (sample_rate * 0.05))
        val = int(16000 * envelope * math.sin(2 * math.pi * freq * i / sample_rate))
        val = max(-32768, min(32767, val))
        samples.append(struct.pack("<h", val))
    return b"".join(samples)


def s16le_to_float32(pcm_s16le: bytes) -> bytes:
    """将 s16le PCM 转换为 float32 little-endian PCM"""
    n_samples = len(pcm_s16le) // 2
    int_samples = struct.unpack(f"<{n_samples}h", pcm_s16le)
    float_samples = [s / 32768.0 for s in int_samples]
    return struct.pack(f"<{n_samples}f", *float_samples)


def get_test_pcm(text: str, tts_available: bool, ffmpeg_available: bool) -> tuple[bytes, bool]:
    """获取测试音频 PCM 数据"""
    if tts_available and ffmpeg_available:
        try:
            pcm = synthesize_tts_pcm(text)
            duration_ms = len(pcm) / 2 / TARGET_SAMPLE_RATE * 1000
            print(f"    TTS 合成成功: {len(pcm)} bytes PCM ({duration_ms:.0f}ms @16kHz)")
            return pcm, True
        except RuntimeError as e:
            print(f"    TTS 合成失败，降级为正弦波: {e}")

    pcm = generate_sine_pcm(duration_ms=800, freq=440)
    print(f"    降级正弦波: {len(pcm)} bytes PCM ({len(pcm) // 32}ms @16kHz)")
    return pcm, False


# ============ 主逻辑 ============

def build_utterance_record(utt: dict, pcm_s16le: bytes, is_real: bool) -> dict:
    """构建单条语句的 JSON 记录"""
    num_samples = len(pcm_s16le) // 2
    duration_ms = num_samples / TARGET_SAMPLE_RATE * 1000

    pcm_base64 = base64.b64encode(pcm_s16le).decode("utf-8")

    pcm_float32 = s16le_to_float32(pcm_s16le)
    pcm_float32_base64 = base64.b64encode(pcm_float32).decode("utf-8")

    return {
        "id": utt["id"],
        "text": utt["text"],
        "keywords": utt["keywords"],
        "pcm_base64": pcm_base64,
        "pcm_float32_base64": pcm_float32_base64,
        "sample_rate": TARGET_SAMPLE_RATE,
        "num_channels": NUM_CHANNELS,
        "bits_per_sample": BITS_PER_SAMPLE,
        "duration_ms": round(duration_ms, 1),
        "num_samples": num_samples,
        "is_real": is_real,
    }


def main():
    parser = argparse.ArgumentParser(description="预合成测试音频集 → test_audio_set.json")
    parser.add_argument("--force", action="store_true", help="强制重新合成（忽略缓存）")
    args = parser.parse_args()

    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)

    if not args.force and OUTPUT_FILE.exists():
        print(f"缓存命中: {OUTPUT_FILE} 已存在，跳过合成。")
        print(f"使用 --force 强制重新合成。")
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            cached = json.load(f)
        print(f"已缓存 {len(cached.get("utterances", []))} 条语句。")
        return

    tts_available = _check_tool("z-ai")
    ffmpeg_available = _check_tool("ffmpeg")

    print("=" * 55)
    print("XEngineer 测试音频预合成")
    print(f"时间: {time.strftime("%Y-%m-%d %H:%M:%S")}")
    print(f"z-ai TTS: {"✅ 可用" if tts_available else "❌ 不可用"}")
    print(f"ffmpeg:   {"✅ 可用" if ffmpeg_available else "❌ 不可用"}")
    if tts_available and ffmpeg_available:
        print("音频模式: TTS 合成语音 (is_real=true)")
    else:
        print("音频模式: 降级正弦波 (is_real=false)")
    print(f"测试语句: {len(TEST_UTTERANCES)} 条")
    print(f"输出: {OUTPUT_FILE}")
    print("=" * 55)

    utterance_records = []
    for i, utt in enumerate(TEST_UTTERANCES):
        uid = utt["id"]
        text = utt["text"]
        print(f"
[{i + 1}/{len(TEST_UTTERANCES)}] 语句 #{uid}: "{text}"")

        pcm_s16le, is_real = get_test_pcm(text, tts_available, ffmpeg_available)
        record = build_utterance_record(utt, pcm_s16le, is_real)
        utterance_records.append(record)

        print(f"    → num_samples={record["num_samples"]}, "
              f"duration={record["duration_ms"]:.0f}ms, "
              f"s16le_b64={len(record["pcm_base64"])} chars, "
              f"f32_b64={len(record["pcm_float32_base64"])} chars, "
              f"is_real={record["is_real"]}")

    output = {
        "utterances": utterance_records,
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    file_size = OUTPUT_FILE.stat().st_size
    print(f"
{"=" * 55}")
    print(f"✅ 输出完成: {OUTPUT_FILE}")
    print(f"   文件大小: {file_size:,} bytes ({file_size / 1024:.1f} KB)")
    real_count = sum(1 for r in utterance_records if r["is_real"])
    print(f"   真实语音: {real_count}/{len(utterance_records)} 条")
    print(f"{"=" * 55}")


if __name__ == "__main__":
    main()
