# AI视觉对话助手 — 技术调研报告

> 调研目标：为七牛云AI Hackathon"AI视觉对话助手"赛题提供全面的技术调研支撑
> 调研时间：2025年7月
> 赛题要求：打开摄像头与麦克风，AI实时看到视频内容、听到语音并恰当回应，需综合考虑视觉理解准确性、语音交互流畅性、端云协同成本控制

---

## 一、开源项目搜索与分析

### 1.1 核心框架类项目

#### 1. Pipecat ⭐ 7k+ Stars

| 项目 | 详情 |
|------|------|
| **GitHub** | https://github.com/pipecat-ai/pipecat |
| **Star数** | ~7,000+（持续增长中） |
| **技术栈** | Python, WebRTC, Daily (会议平台), 多种LLM/VLM/STT/TTS服务集成 |
| **核心功能** | 开源Python框架，用于构建实时语音和多模态对话Agent。支持68+服务集成，支持级联(Cascaded: STT→LLM→TTS)和原生语音到语音(S2S)两种模式。支持音频、视频和文本通道的编排 |
| **更新时间** | 2025年持续活跃更新 |

**关键特性：**
- 提供 Pipeline/Flow 架构来编排 AI 服务、网络传输和音频处理
- 支持Google Gemini、OpenAI GPT-4o、Anthropic Claude等多种LLM
- 支持Deepgram、Whisper、AssemblyAI等ASR服务
- 支持Cartesia、ElevenLabs、OpenAI TTS等语音合成
- AWS官方推荐用于构建Bedrock语音Agent
- O'Reilly出版了基于Pipecat的《Multimodal, Real-Time AI Agent Systems》书籍

**代码示例（Pipecat Pipeline基础结构）：**
```python
from pipecat.pipeline import Pipeline
from pipecat.services.openai import OpenAILLMService
from pipecat.services.deepgram import DeepgramSTTService
from pipecat.services.cartesia import CartesiaTTSService

stt = DeepgramSTTService(api_key="your_key")
llm = OpenAILLMService(api_key="your_key", model="gpt-4o")
tts = CartesiaTTSService(api_key="your_key", voice_id="your_voice")

pipeline = Pipeline([
    stt,   # 语音→文字
    llm,   # 文字→推理
    tts,   # 文字→语音
])
```

---

#### 2. LiveKit Agents ⭐ 10.7k Stars

| 项目 | 详情 |
|------|------|
| **GitHub** | https://github.com/livekit/agents |
| **Star数** | ~10,700 |
| **技术栈** | Python / TypeScript, WebRTC, 实时音视频通信 |
| **核心功能** | 构建实时可编程语音/视频AI Agent的开源框架。基于WebRTC实现超低延迟音视频传输，支持对话式、多模态语音Agent |
| **更新时间** | 2025年持续活跃更新 |

**关键特性：**
- 基于WebRTC的实时音视频通信，全球排名#4843
- 完整的前后端SDK，支持Python和TypeScript
- 382个贡献者，社区非常活跃
- 支持多模态（语音+视频+文本）
- 原生支持打断（interruption）、VAD（语音活动检测）
- LiveKit Cloud提供托管服务，边缘网络覆盖全球

---

#### 3. Stream Vision Agents ⭐ 3k+ Stars

| 项目 | 详情 |
|------|------|
| **GitHub** | https://github.com/getstream/Vision-Agents |
| **Star数** | ~3,000+ |
| **技术栈** | Python, WebRTC, Stream边缘网络, 25+ AI模型集成 |
| **核心功能** | 开源Python框架，快速构建实时语音和视频AI Agent。利用Stream的边缘网络实现超低延迟 |
| **更新时间** | 2025年活跃更新 |

**关键特性：**
- 可接入任何LLM、语音、视觉模型（25+集成）
- 原生Tool Calling支持
- 可插拔的视觉Pipeline（可组合YOLO目标检测+Gemini/OpenAI实时理解）
- 设计用于telehealth、客服等生产场景
- WebRTC原生支持

---

#### 4. MiniCPM-o (OpenBMB) ⭐ 20k+ Stars

| 项目 | 详情 |
|------|------|
| **GitHub** | https://github.com/openbmb/MiniCPM-V |
| **Star数** | ~20,000+（MiniCPM-V系列） |
| **技术栈** | PyTorch, LLaVA架构, 端侧部署, 流式视频/音频处理 |
| **核心功能** | "口袋大小"的多模态大语言模型。MiniCPM-o 2.6/4.5支持实时全双工多模态交互，可接受连续视频和音频流输入，支持文本和语音输出 |
| **更新时间** | 2025年持续更新（最新版本MiniCPM-o 4.5） |

**关键特性：**
- MiniCPM-o 2.6 在视觉、语音和多模态实时流式传输上匹配 GPT-4o-202405
- MiniCPM-o 4.5 支持全双工交互（同时感知和响应）
- 可本地部署（Ollama支持），**不需要GPU集群**
- 支持30种语言和9种中文方言的语音理解
- 流式视频和音频输入，独立于用户查询
- **极适合Hackathon本地演示场景**

---

#### 5. VITA ⭐ 5k+ Stars

| 项目 | 详情 |
|------|------|
| **GitHub** | https://github.com/VITA-MLLM/VITA |
| **Star数** | ~5,000+ |
| **技术栈** | PyTorch, 多阶段训练, 并行音频/视觉解码 |
| **核心功能** | 首个开源交互式全多模态LLM，能同时处理视频、图像、文本和音频 |
| **更新时间** | 2024年12月（VITA-1.5），VITA-E（腾讯，具身交互版本） |

**关键特性：**
- VITA-1.5 达到接近GPT-4o级别的实时视觉-语音交互
- 三阶段渐进式训练方法
- 同时运行视觉和音频通道的并行处理
- VITA-E版本支持具身机器人交互（48GB显存需求）

---

#### 6. Vinci (OpenGVLab) ⭐ 8.9k Stars

| 项目 | 详情 |
|------|------|
| **GitHub** | https://github.com/opengvlab/vinci |
| **Star数** | ~8,989 |
| **技术栈** | Python, 自我中心视觉语言模型(Egocentric VLM), 智能手机/便携设备优化 |
| **核心功能** | 基于自我中心视觉语言模型的实时具身智能助手 |
| **更新时间** | 2024-2025年 |

**关键特性：**
- 专为便携设备设计，包括智能手机
- 自我中心(第一人称)视角的视觉理解
- 实时智能助手能力
- ACM UbiComp 2025收录
- 适合"AI助手看摄像头"的参考架构

---

#### 7. Ultravox (Fixie AI) ⭐ 5k+ Stars

| 项目 | 详情 |
|------|------|
| **GitHub** | https://github.com/fixie-ai/ultravox |
| **Star数** | ~5,000+ |
| **技术栈** | PyTorch, 多模态LLM, 端到端语音理解（无需独立ASR） |
| **核心功能** | 一种新型多模态LLM，能同时理解文本和人类语音，无需独立的ASR阶段 |
| **更新时间** | 2025年活跃 |

**关键特性：**
- **绕过ASR环节**，直接将音频编码输入LLM，大幅降低延迟
- 支持文本系统提示+语音用户消息的混合输入
- v0.4.1版本是专门为实时AI对话训练的开源语音模型族
- 可本地部署

---

#### 8. StreamingVLM (MIT & NVIDIA) ⭐ 2k+ Stars

| 项目 | 详情 |
|------|------|
| **GitHub** | https://github.com/mit-han-lab/streaming-vlm |
| **Star数** | ~2,000+ |
| **技术栈** | PyTorch, 高效KV缓存, 重叠窗口全注意力 |
| **核心功能** | 实时理解无限视频流，通过紧凑KV缓存和对齐训练实现高效推理 |
| **更新时间** | 2024年 |

**关键特性：**
- **单张H100上实现8FPS实时推理**
- 对抗GPT-4o mini达到66.18%胜率
- 训练推理统一的流式架构
- 高效KV缓存复用机制
- **成本优化的关键技术参考**：重叠窗口注意力

---

#### 9. aiwebcam2

| 项目 | 详情 |
|------|------|
| **GitHub** | https://github.com/catid/aiwebcam2 |
| **Star数** | 较小（个人项目） |
| **技术栈** | Whisper3 + GPT-4-Vision + OpenAI TTS + WebRTC前端 |
| **核心功能** | 可在家运行的完整交互式摄像头AI助手 |
| **更新时间** | 2024年 |

**关键特性：**
- **最接近赛题的完整实现**：WebRTC浏览器前端 + 后端Whisper/GPT-4V/TTS
- 展示了"摄像头→帧提取→VLM→语音回应"的完整链路
- WebRTC确保低延迟传输
- 适合作为架构参考

---

#### 10. PyGPT (Desktop AI Assistant)

| 项目 | 详情 |
|------|------|
| **GitHub** | https://github.com/szczyglis-dev/py-gpt |
| **Star数** | ~3,000+ |
| **技术栈** | Python, Qt Desktop, 多种AI服务 |
| **核心功能** | 开源桌面AI助手，支持实时视频摄像头捕获（Vision模式）、TTS/STT、插件、长期记忆 |
| **更新时间** | 2025年活跃 |

---

### 1.2 开源项目总结对比

| 项目 | Stars | 类型 | 语音 | 视觉 | 可本地部署 | 适合Hackathon |
|------|-------|------|------|------|-----------|-------------|
| **Pipecat** | 7k+ | 框架 | ✅ | ✅ | 部分 | ⭐⭐⭐⭐⭐ |
| **LiveKit Agents** | 10.7k | 框架 | ✅ | ✅ | 部分 | ⭐⭐⭐⭐ |
| **Stream Vision Agents** | 3k+ | 框架 | ✅ | ✅ | 否 | ⭐⭐⭐⭐ |
| **MiniCPM-o** | 20k+ | 模型+框架 | ✅ | ✅ | ✅ 完全本地 | ⭐⭐⭐⭐⭐ |
| **VITA** | 5k+ | 模型 | ✅ | ✅ | ✅ 需GPU | ⭐⭐⭐ |
| **Vinci** | 8.9k | 模型+应用 | ✅ | ✅ | ✅ | ⭐⭐⭐⭐ |
| **Ultravox** | 5k+ | 模型 | ✅ | ❌(仅语音) | ✅ | ⭐⭐⭐ |
| **StreamingVLM** | 2k+ | 模型 | ❌ | ✅ | ✅ 需H100 | ⭐⭐⭐ |
| **aiwebcam2** | 小 | 完整应用 | ✅ | ✅ | ✅ | ⭐⭐⭐⭐ |

---

## 二、技术方案研究

### 2.1 整体架构设计

AI视觉对话助手的核心架构可分为三种范式：

#### 范式一：级联架构（Cascaded Pipeline）

这是**最成熟、最适合Hackathon快速实现**的方案。

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│ 摄像头   │     │ 麦克风   │     │         │     │         │
│ getUser  │     │ getUser  │     │         │     │         │
│ Media()  │     │ Media()  │     │         │     │         │
└────┬─────┘     └────┬─────┘     │         │     │         │
     │                │           │         │     │         │
     ▼                ▼           │         │     │         │
┌─────────┐     ┌──────────┐     │         │     │         │
│ Canvas   │     │ ASR      │     │         │     │         │
│ 帧提取   │     │ 语音识别  │     │         │     │         │
│ Base64   │     │ (Whisper)│     │         │     │         │
└────┬─────┘     └────┬─────┘     │         │     │         │
     │                │           │         │     │         │
     │    ┌───────────▼───────────▼─┐       │     │         │
     │    │     LLM / VLM          │       │     │         │
     ├───▶│  (GPT-4o / Qwen-VL /   │       │     │         │
     │    │   Gemini / MiniCPM-o)  │       │     │         │
     │    └───────────┬───────────┬─┘       │     │         │
     │                │           │         │     │         │
     │                ▼           ▼         │     │         │
     │          ┌──────────┐ ┌─────────┐    │     │         │
     │          │ 对话文本  │ │ TTS     │    │     │         │
     │          │ 显示     │ │ 语音合成  │    │     │         │
     │          └──────────┘ └────┬────┘    │     │         │
     │                            │         │     │         │
     │                            ▼         │     │         │
     │                     ┌──────────┐     │     │         │
     │                     │ 音频播放  │     │     │         │
     │                     └──────────┘     │     │         │
```

**流程说明：**
1. **视频帧提取**：前端用Canvas定时截取摄像头画面，转为base64
2. **语音识别(ASR)**：麦克风音频流送入Whisper/Deepgram/阿里云ASR，转为文本
3. **多模态推理**：将文本+图像帧一起发送给VLM（如GPT-4o、Qwen-VL）
4. **语音合成(TTS)**：LLM输出的文本流式送入TTS服务
5. **音频播放**：前端接收TTS音频流并播放

#### 范式二：原生端到端（Native Speech-to-Speech）

以OpenAI Realtime API和Gemini Live API为代表，跳过独立ASR步骤。

```
浏览器                     云端
┌──────────┐           ┌──────────────┐
│ 麦克风    │──WebRTC──▶│  gpt-realtime │
│ 音频流    │           │  或 Gemini    │
│          │◀──WebRTC──│  Live API     │
│ 扬声器    │           │  (端到端模型)  │
└──────────┘           └──────────────┘
         + 视频帧通过附加通道发送
```

**优势：** 延迟最低（<500ms），对话最自然
**劣势：** 依赖特定API，灵活性低，成本高

#### 范式三：端侧部署（On-Device）

以MiniCPM-o为代表，所有推理在本地完成。

```
┌──────────────────────────────────────┐
│           本地设备                    │
│  ┌─────────┐   ┌───────────────┐    │
│  │ 摄像头   │──▶│  MiniCPM-o    │──▶ TTS │
│  │ +麦克风  │──▶│  (本地推理)    │──▶ 输出 │
│  └─────────┘   └───────────────┘    │
│                    Ollama/vLLM      │
└──────────────────────────────────────┘
```

---

### 2.2 前端视频帧提取方案

#### 方案一：Canvas截图（推荐，最简单）

```javascript
// 获取摄像头流
const stream = await navigator.mediaDevices.getUserMedia({
  video: { width: 640, height: 480, frameRate: { ideal: 1 } },  // 1fps足够
  audio: true
});

const video = document.createElement('video');
video.srcObject = stream;
await video.play();

const canvas = document.createElement('canvas');
canvas.width = 640;
canvas.height = 480;
const ctx = canvas.getContext('2d');

// 定时提取帧（每2秒一次，控制成本）
setInterval(() => {
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
  const base64 = canvas.toDataURL('image/jpeg', 0.7); // JPEG压缩，质量0.7
  // 发送到后端
  sendFrameToBackend(base64);
}, 2000);
```

#### 方案二：WebRTC传输（低延迟场景）

```javascript
// 使用WebRTC发送视频流到后端
const pc = new RTCPeerConnection({
  iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
});

// 添加摄像头track
const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
stream.getTracks().forEach(track => pc.addTrack(track, stream));

// 创建offer，通过信令服务器交换
const offer = await pc.createOffer();
await pc.setLocalDescription(offer);
// ... 信令交换 ...
```

#### 方案三：MediaRecorder录制片段

```javascript
const mediaRecorder = new MediaRecorder(stream, {
  mimeType: 'video/webm;codecs=vp8',
  videoBitsPerSecond: 500000  // 500kbps
});

// 每5秒切割一个片段
let chunks = [];
mediaRecorder.ondataavailable = (e) => {
  if (e.data.size > 0) {
    chunks.push(e.data);
    // 发送视频片段到后端
    sendVideoChunk(new Blob(chunks, { type: 'video/webm' }));
    chunks = [];
  }
};
mediaRecorder.start(5000); // 每5秒触发一次
```

**方案对比：**

| 方案 | 延迟 | 带宽 | 实现复杂度 | 适用场景 |
|------|------|------|-----------|---------|
| Canvas截图 | 中(200ms+) | 低(base64) | ⭐ 低 | Hackathon首选 |
| WebRTC | 低(<100ms) | 中 | ⭐⭐⭐ 高 | 生产级实时 |
| MediaRecorder | 高 | 中 | ⭐⭐ 中 | 视频片段分析 |

---

### 2.3 语音交互链路

#### ASR（语音→文本）方案对比

| 方案 | 延迟 | 价格 | 中文支持 | 特点 |
|------|------|------|---------|------|
| **Web Speech API** | 低 | 免费 | ✅ | 浏览器内置，零成本，但需在线 |
| **Whisper (OpenAI)** | 中 | $0.006/min | ✅ | 开源可本地部署，精度高 |
| **FunASR (阿里)** | 低 | 开源免费 | ✅✅ | 中文最优，SenseVoice非自回归超快 |
| **Deepgram** | 极低(<300ms) | $0.0043/min | ✅ | 流式实时，生产级 |
| **AssemblyAI** | 低 | $0.015/min | ✅ | 流式，支持语音活动检测 |

**推荐Hackathon方案：FunASR（中文场景）或 Web Speech API（快速原型）**

```javascript
// Web Speech API 方案（零成本，快速原型）
const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
recognition.continuous = true;
recognition.interimResults = true;
recognition.lang = 'zh-CN';

recognition.onresult = (event) => {
  const text = Array.from(event.results)
    .map(r => r[0].transcript)
    .join('');
  onUserSpeech(text);
};
recognition.start();
```

#### TTS（文本→语音）方案对比

| 方案 | 延迟 | 价格 | 音质 | 流式支持 |
|------|------|------|------|---------|
| **Web Speech API** | 低 | 免费 | 中 | ❌ |
| **Edge-TTS** | 低 | 免费 | 高 | ❌(可自行流式化) |
| **OpenAI TTS** | 中 | $15/1M字符 | 极高 | ✅ |
| **CosyVoice (阿里)** | 低 | 开源免费 | 高 | ✅ |
| **Fish Speech** | 低 | 开源免费 | 高 | ✅ 流式 |
| **ChatTTS** | 低 | 开源免费 | 自然 | ✅ |

**推荐Hackathon方案：Edge-TTS（零成本高质量）或 CosyVoice/Fish Speech（本地流式）**

```python
# Edge-TTS 零成本方案
import edge_tts

async def speak(text: str):
    communicate = edge_tts.Communicate(text, "zh-CN-YunxiNeural")
    await communicate.save("output.mp3")

# Fish Speech 流式TTS
# pip install fish-speech
# 支持流式音频输出，延迟极低
```

---

### 2.4 VLM（视觉理解）方案

#### 云端API方案

| 模型 | 输入格式 | 价格 | 视觉能力 | 推荐度 |
|------|---------|------|---------|--------|
| **GPT-4o** | base64图片/视频帧 | $2.5/1M输入token | 顶尖 | ⭐⭐⭐⭐⭐ |
| **Gemini 2.0/3.1** | base64/视频文件 | 免费额度+付费 | 顶尖(支持原生视频) | ⭐⭐⭐⭐⭐ |
| **Qwen-VL (通义千问)** | base64图片/视频URL | ¥0.008/千token | 优秀 | ⭐⭐⭐⭐⭐ |
| **Claude 3.5 Sonnet** | base64图片 | $3/1M输入token | 优秀 | ⭐⭐⭐⭐ |

```python
# GPT-4o Vision API 调用示例
from openai import OpenAI

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "描述你看到的画面"},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_frame}"
                }
            }
        ]
    }]
)
```

```python
# Qwen-VL API 调用示例（阿里云百炼）
from openai import OpenAI

client = OpenAI(
    api_key="your-dashscope-key",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

response = client.chat.completions.create(
    model="qwen-vl-max",
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "这是什么？"},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{frame}"}}
        ]
    }]
)
```

#### 端侧方案（Hackathon亮点）

```python
# 使用 Ollama 本地运行 MiniCPM-o
# ollama pull minicpm-o:2.6
from openai import OpenAI

client = OpenAI(base_url="http://localhost:11434/v1")

# 流式视频帧输入
response = client.chat.completions.create(
    model="minicpm-o:2.6",
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "用一句话描述画面中正在发生什么"},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{frame}"}}
        ]
    }],
    stream=True
)
```

---

### 2.5 流式响应方案（让对话感觉流畅）

实现流畅对话的关键在于**全链路流式处理**，目标端到端延迟 < 1秒。

#### 完整流式Pipeline架构

```
用户说话 ──▶ 流式ASR（边说边转）──▶ 检测到停顿 ──▶
  ▼
LLM流式生成（边想边输出）──▶ 流式TTS（边生成边合成）──▶
  ▼
边播放音频（首chunk延迟 < 500ms）
```

**关键代码（Python后端流式处理）：**

```python
import asyncio
import websockets
import json

async def handle_client(websocket):
    async for message in websocket:
        data = json.loads(message)

        if data["type"] == "audio_chunk":
            # 流式ASR处理
            text = await stream_asr(data["audio"])
            if text:
                # 发送VLM请求（含当前帧）
                async for chunk in stream_llm(text, current_frame):
                    # 流式TTS
                    audio_chunk = await stream_tts(chunk)
                    await websocket.send(json.dumps({
                        "type": "tts_audio",
                        "audio": audio_chunk
                    }))

async def stream_llm(text: str, frame_base64: str):
    """流式调用LLM"""
    response = await async_openai.chat.completions.create(
        model="gpt-4o",
        messages=[...],
        stream=True
    )
    async for chunk in response:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
```

**延迟优化要点：**

| 环节 | 优化策略 | 效果 |
|------|---------|------|
| ASR | 使用流式ASR（非批量） | 从3s→300ms |
| LLM | 使用流式输出 + 打断支持 | 首token < 200ms |
| TTS | 使用流式TTS（sentence-level streaming） | 从1.3s→300ms |
| 传输 | WebSocket / WebRTC | < 50ms |
| **总计** | 全链路流式 | **< 800ms** |

参考数据（来自 Deepgram 测试）：从离线ASR切换到流式ASR可**降低约9倍延迟**。sentence-level流式TTS是**最高ROI的延迟优化**。

---

## 三、成本控制策略（Hackathon核心考量）

### 3.1 视频帧成本控制

**核心问题：** 一帧1024×1024图像在VLM中可能产生256-1024个视觉token，视频token消耗极快。

#### 策略1：帧率控制（最有效）

```javascript
// 自适应帧率：画面变化大时提高帧率，静止时降低
let lastFrameHash = '';
let frameInterval = 3000; // 默认3秒一帧

function adaptiveFrameCapture() {
  const currentHash = hashFrame(currentFrame);

  if (currentHash !== lastFrameHash) {
    // 画面有变化，立即发送
    sendFrame(currentFrame);
    frameInterval = 1000; // 1秒一帧
    lastFrameHash = currentHash;
  } else {
    // 画面无变化，降低帧率
    frameInterval = Math.min(frameInterval * 1.5, 10000); // 最长10秒
  }

  setTimeout(adaptiveFrameCapture, frameInterval);
}
```

#### 策略2：分辨率和压缩

```javascript
// 分辨率：从1280x720降到640x360，token数减少4倍
canvas.width = 640;
canvas.height = 360;

// JPEG压缩：质量从95%降到60%，文件大小减少5-10倍
const base64 = canvas.toDataURL('image/jpeg', 0.6);

// 缩放后再发送
const MAX_SIZE = 320; // 进一步缩小到320px
const tempCanvas = document.createElement('canvas');
tempCanvas.width = MAX_SIZE;
tempCanvas.height = MAX_SIZE * (video.videoHeight / video.videoWidth);
tempCanvas.getContext('2d').drawImage(canvas, 0, 0, tempCanvas.width, tempCanvas.height);
```

#### 策略3：智能帧选择

```python
# 后端策略：只在用户说话时才分析画面
class SmartFrameAnalyzer:
    def __init__(self):
        self.last_analyzed_frame = None
        self.frame_similarity_threshold = 0.95

    async def should_analyze(self, frame_base64: str, user_speaking: bool) -> bool:
        # 用户说话时 + 画面有明显变化 = 分析
        if user_speaking and self.frame_changed(frame_base64):
            self.last_analyzed_frame = frame_base64
            return True
        return False

    def frame_changed(self, frame: str) -> bool:
        if not self.last_analyzed_frame:
            return True
        similarity = calculate_ssim(self.last_analyzed_frame, frame)
        return similarity < self.frame_similarity_threshold
```

#### 策略4：对话历史管理

```python
# 精简上下文：只保留关键帧和最近N轮对话
class ContextManager:
    MAX_TURNS = 5  # 最多保留5轮对话
    MAX_IMAGE_TOKENS = 4  # 上下文中最多4张图片

    def build_messages(self, history, current_frame, current_text):
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # 只保留最近的对话轮次
        recent_history = history[-self.MAX_TURNS:]
        for turn in recent_history:
            messages.append(turn)

        # 当前消息只包含最新一帧
        messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": current_text},
                {"type": "image_url", "image_url": {"url": current_frame}}
            ]
        })

        return messages
```

#### 策略5：模型分层策略

```
简单问题（"现在几点？"）──▶ 纯文本LLM（便宜10-100倍）
视觉问题（"这是什么？"）──▶ 轻量VLM（Qwen-VL-Plus / Gemini Flash）
复杂视觉任务 ──▶ 旗舰VLM（GPT-4o / Qwen-VL-Max）
```

### 3.2 成本估算（以GPT-4o为例）

| 操作 | 单价 | 估算用量 | 费用/小时 |
|------|------|---------|----------|
| 视频帧输入 | $2.5/1M token | ~120帧×~500token = 60K token | $0.15 |
| 文本输入 | $2.5/1M token | ~5K token | $0.0125 |
| 文本输出 | $10/1M token | ~2K token | $0.02 |
| TTS | $15/1M字符 | ~5K字符 | $0.075 |
| ASR | $0.006/min | ~10分钟有效语音 | $0.06 |
| **总计** | | | **~$0.32/小时** |

**使用Qwen-VL替代可降低至约 ¥0.2/小时。**
**使用本地MiniCPM-o + FunASR + Edge-TTS = 零API成本。**

### 3.3 七牛云成本控制（来自七牛云官方文章）

根据七牛云官方文章《大模型API调用成本优化与并发应对》：
- 精简Prompt模板是第一步
- 剔除无效的上下文历史记录
- 对复杂场景使用缓存策略
- 利用七牛云CDN分发静态资源
- 使用七牛云对象存储管理帧数据

---

## 四、类似产品参考

### 4.1 ChatGPT Voice with Live Video

| 项目 | 详情 |
|------|------|
| **发布时间** | 2024年5月（GPT-4o发布），2025年GA版本 |
| **技术架构** | OpenAI Realtime API + WebRTC |
| **视频传输** | H.264编码，无Simulcast，通过WebRTC发送 |
| **音频传输** | Opus编码，带in-band FEC |
| **连接方式** | 单PeerConnection + BUNDLE，纯Host ICE候选（无STUN/TURN） |
| **数据通道** | 标准SCTP over DTLS，用于JSON事件传递 |
| **延迟** | < 500ms（端到端语音） |
| **新特性** | GA版本新增 `/v1/realtime/calls` 端点，一次API调用同时建立WebRTC会话和LLM会话 |

**OpenAI Realtime API WebRTC 连接代码：**
```javascript
const fd = new FormData();
fd.set("sdp", pc.localDescription.sdp);
fd.set("session", JSON.stringify({
    model: "gpt-realtime",
    voice: "verse",
    modalities: ["text", "audio"]
}));

const response = await fetch("https://api.openai.com/v1/realtime/calls", {
    method: "POST",
    headers: { "Authorization": `Bearer ${apiKey}` },
    body: fd
});
```

参考：https://webrtchacks.com/how-openai-does-webrtc-in-the-new-gpt-realtime

### 4.2 Google Gemini Live

| 项目 | 详情 |
|------|------|
| **发布时间** | 2024年12月（Gemini 2.0 Live），2025年升级Gemini 3.1 Flash Live |
| **技术架构** | Gemini Multimodal Live API（WebSocket + WebRTC） |
| **核心特点** | 原生支持连续视频+音频流输入，双向实时交互 |
| **支持格式** | 文本、音频、视频流的连续处理 |
| **定价** | 有免费额度，生产使用按token计费 |
| **开源示例** | google-gemini/gemini-live-api-examples |

**Gemini Live API 特点：**
- 不需要将视频拆分为帧，原生支持视频流
- 支持双向流式（模型可以主动发起对话）
- 支持工具调用（Function Calling）
- Firebase集成支持

**参考：** Akka团队使用Akka框架+Gemini Live API构建了实时视频AI服务。Google Cloud Blog展示了在制造业中的实时AI应用案例。

### 4.3 Azure AI + GPT-4o

| 项目 | 详情 |
|------|------|
| **技术栈** | Azure OpenAI Service + Azure AI Vision |
| **特点** | 企业级安全，GPT-4o + Azure AI Vision组合 |
| **定价** | GPT-4o: $2.5/1M输入token, $10/1M输出token |
| **适用场景** | 企业级部署，合规要求高的场景 |

---

## 五、关键技术栈总结

### 5.1 推荐Hackathon技术选型

#### 方案A：全云端（最快实现，1-2天完成）

```
前端：React/Next.js + getUserMedia + Canvas + WebSocket
后端：Python FastAPI + WebSocket
ASR：  Web Speech API（免费）或 阿里云FunASR
VLM：  Qwen-VL-Max（阿里云百炼，性价比高）或 Gemini 2.0 Flash
TTS：  Edge-TTS（免费高质量）或 OpenAI TTS
```

#### 方案B：端云混合（亮点方案，2-3天完成）

```
前端：React/Next.js + getUserMedia + Canvas + WebSocket
后端：Python FastAPI + Ollama（本地MiniCPM-o）
ASR：  FunASR（本地部署，非自回归，延迟<100ms）
VLM：  MiniCPM-o 2.6（本地，Ollama一键启动）
TTS：  Fish Speech / CosyVoice（本地流式）
成本：  零API调用成本
```

#### 方案C：使用Pipecat框架（最专业，2天完成）

```python
# Pipecat框架方案
from pipecat.pipeline import Pipeline
from pipecat.services.openai import OpenAILLMService
from pipecat.services.whisper import WhisperSTTService
from pipecat.services.elevenlabs import ElevenLabsTTSService
from pipecat.transports.services.daily import DailyTransport

# 所有组件即插即用
transport = DailyTransport(room_url, token)
stt = WhisperSTTService(model="base")
llm = OpenAILLMService(model="gpt-4o")
tts = ElevenLabsTTSService(voice_id="...")

pipeline = Pipeline([stt, llm, tts])
runner = PipelineRunner(pipeline, transport)
await runner.run()
```

### 5.2 核心代码：完整的帧提取+发送

```javascript
// ========== 前端：完整的摄像头+麦克风采集 ==========
class VisionChatClient {
  constructor(wsUrl) {
    this.ws = null;
    this.video = document.createElement('video');
    this.canvas = document.createElement('canvas');
    this.canvas.width = 640;
    this.canvas.height = 480;
    this.ctx = this.canvas.getContext('2d');
    this.frameInterval = 2000; // 2秒一帧
    this.lastFrameHash = '';
  }

  async start() {
    // 1. 获取摄像头和麦克风
    const stream = await navigator.mediaDevices.getUserMedia({
      video: { width: 640, height: 480, frameRate: { ideal: 5 } },
      audio: true
    });

    this.video.srcObject = stream;
    await this.video.play();

    // 2. 建立WebSocket连接
    this.ws = new WebSocket(wsUrl);

    // 3. 发送音频流（使用Web Speech API或MediaRecorder）
    this.setupAudioCapture(stream);

    // 4. 定时发送视频帧
    this.startFrameCapture();

    // 5. 接收TTS音频
    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'tts_audio') {
        this.playAudio(data.audio);
      } else if (data.type === 'llm_text') {
        this.displayText(data.text);
      }
    };
  }

  startFrameCapture() {
    setInterval(() => {
      this.ctx.drawImage(this.video, 0, 0, this.canvas.width, this.canvas.height);
      const base64 = this.canvas.toDataURL('image/jpeg', 0.6);
      const hash = this.simpleHash(base64);

      // 只在画面变化时发送
      if (hash !== this.lastFrameHash) {
        this.ws.send(JSON.stringify({
          type: 'video_frame',
          frame: base64,
          timestamp: Date.now()
        }));
        this.lastFrameHash = hash;
      }
    }, this.frameInterval);
  }

  simpleHash(str) {
    let hash = 0;
    for (let i = 0; i < Math.min(str.length, 1000); i++) {
      hash = ((hash << 5) - hash) + str.charCodeAt(i);
      hash |= 0;
    }
    return hash;
  }
}
```

### 5.3 后端核心：多模态对话管理

```python
# ========== 后端：多模态对话管理 ==========
import asyncio
import websockets
import json
from openai import AsyncOpenAI

class MultimodalChatServer:
    def __init__(self):
        self.client = AsyncOpenAI()
        self.conversation_history = []
        self.current_frame = None
        self.max_history_turns = 5

    async def handle_connection(self, websocket):
        async for message in websocket:
            data = json.loads(message)

            if data["type"] == "video_frame":
                # 缓存最新帧
                self.current_frame = data["frame"]

            elif data["type"] == "user_speech":
                # 用户语音转文字后触发
                await self.process_user_input(data["text"], websocket)

    async def process_user_input(self, text: str, websocket):
        # 构建多模态消息
        user_message = {
            "role": "user",
            "content": [{"type": "text", "text": text}]
        }

        # 如果有当前帧，附加图片
        if self.current_frame:
            user_message["content"].append({
                "type": "image_url",
                "image_url": {"url": self.current_frame}
            })

        self.conversation_history.append(user_message)

        # 控制上下文长度
        if len(self.conversation_history) > self.max_history_turns * 2:
            self.conversation_history = self.conversation_history[-self.max_history_turns * 2:]

        # 流式调用VLM
        messages = [
            {"role": "system", "content": "你是一个友好的AI视觉助手。用户会向你展示摄像头中的画面并提问。请简短、准确地回答。"}
        ] + self.conversation_history

        response = await self.client.chat.completions.create(
            model="qwen-vl-max",  # 或 "gpt-4o"
            messages=messages,
            stream=True
        )

        full_response = ""
        async for chunk in response:
            delta = chunk.choices[0].delta.content
            if delta:
                full_response += delta
                # 发送文本到前端显示
                await websocket.send(json.dumps({
                    "type": "llm_text",
                    "text": delta
                }))

        # 保存AI回复到历史
        self.conversation_history.append({
            "role": "assistant",
            "content": full_response
        })

        # TTS合成（可选，Edge-TTS）
        audio = await self.text_to_speech(full_response)
        if audio:
            await websocket.send(json.dumps({
                "type": "tts_audio",
                "audio": audio
            }))

async def text_to_speech(self, text: str) -> bytes:
    import edge_tts
    communicate = edge_tts.Communicate(text, "zh-CN-YunxiNeural")
    audio_bytes = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_bytes += chunk["data"]
    return audio_bytes
```

---

## 六、用户故事建议

### 计划实现的核心用户故事

| # | 用户故事 | 优先级 | 复杂度 |
|---|---------|--------|--------|
| 1 | 作为用户，我打开网页后能自动看到摄像头画面 | P0 | 低 |
| 2 | 作为用户，我说话后AI能听到并理解我的意思 | P0 | 中 |
| 3 | 作为用户，AI能描述它通过摄像头看到的画面内容 | P0 | 中 |
| 4 | 作为用户，AI能根据看到的内容回答我的问题 | P0 | 中 |
| 5 | 作为用户，AI的回复能以语音形式播放 | P1 | 低 |
| 6 | 作为用户，对话界面能同时显示文字和语音 | P1 | 低 |
| 7 | 作为用户，我能看到AI正在"看"的画面（帧预览） | P1 | 低 |
| 8 | 作为用户，我可以用中文自然对话 | P0 | 低 |
| 9 | 作为用户，AI的回复延迟在2秒以内 | P1 | 高 |

### 加分用户故事

| # | 用户故事 | 优先级 |
|---|---------|--------|
| 10 | AI能主动描述画面中发生的变化（如"你好像在做饭"） | P2 |
| 11 | 支持多轮对话，AI记住之前看到的上下文 | P2 |
| 12 | 显示实时的token消耗和成本估算 | P2 |
| 13 | 支持多种VLM模型切换 | P2 |
| 14 | 移动端适配（手机浏览器可用） | P2 |

---

## 七、结论与建议

### 推荐方案（Hackathon最优解）

**方案：Pipecat框架 + Qwen-VL-Max + FunASR + Edge-TTS**

理由：
1. **Pipecat**提供了完整的语音+视觉多模态Pipeline，68+集成，2天内可出Demo
2. **Qwen-VL-Max**（阿里云百炼）视觉理解能力强，价格低（¥0.008/千token），中文场景最优
3. **FunASR**（阿里开源）中文语音识别精度最高，非自回归架构延迟极低
4. **Edge-TTS**免费且音质高，零成本TTS
5. 七牛云作为赞助方，阿里系技术栈可能有额外优势

**如果追求零API成本亮点：MiniCPM-o本地部署方案**

### 关键参考文献

1. [Pipecat官方文档](https://docs.pipecat.ai/overview/introduction)
2. [OpenAI Realtime API WebRTC文档](https://developers.openai.com/api/docs/guides/realtime-webrtc)
3. [Gemini Live API文档](https://ai.google.dev/gemini-api/docs/live-api)
4. [webrtcHacks: How OpenAI does WebRTC](https://webrtchacks.com/how-openai-does-webrtc-in-the-new-gpt-realtime)
5. [StreamingVLM: MIT & NVIDIA](https://arxiv.org/html/2510.09608v1) — KV缓存复用降低视频token消耗
6. [七牛云：大模型API调用成本优化](https://news.qiniu.com/archives/post-1779761299950-0)
7. [InfoQ：全帧率VLM、低成本与分层部署](https://www.infoq.cn/article/7J14Dd3UkwkYoHVjkM9P)
8. [Deepgram: Real-Time Speech-to-Speech Translation](https://deepgram.com/learn/real-time-speech-to-speech-translation) — 流式ASR/TTS延迟优化
9. [LiveKit Agents框架](https://docs.livekit.io/agents)
10. [Stream Vision Agents](https://visionagents.ai)

---

*本报告基于2025年7月的公开信息编写，技术栈和价格可能随时间变化。*