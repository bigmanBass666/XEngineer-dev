# XEngineer 模型清单（最终版）

> 优先级：Agnes 优先 → Agnes 做不到的用 NVIDIA NIM
> 更新时间: 2026-06-12

---

## 一、Agnes AI（优先使用）

### 1. Text — agnes-2.0-flash

| 项目 | 详情 |
|------|------|
| Endpoint | `https://apihub.agnes-ai.com/v1/chat/completions` |
| 认证 | `Authorization: Bearer <AGNES_API_KEY>` |
| 兼容 | OpenAI Chat Completions API |
| 上下文 | 256K tokens |
| 最大输出 | 65.5K tokens |
| 价格 | **免费** |

**核心能力：**
- ✅ 文本对话（多轮、system prompt、流式输出）
- ✅ 图片理解（支持 **公网URL** 和 **base64 data URI** 两种输入方式）
- ✅ 工具调用（function calling）
- ✅ Thinking模式（代码/推理任务）
- ✅ JSON结构化输出

**图片输入方式：**
- 公网URL：`{"type": "image_url", "image_url": {"url": "https://example.com/img.jpg"}}`
- Base64 Data URI：`{"type": "image_url", "image_url": {"url": "data:image/png;base64,..."}}`
- 两种方式均通过 `image_url` type 传入，区别在 `url` 字段的值

**局限：**
- ❌ 不支持视频流理解
- ❌ 不支持 ASR/TTS

**Hackathon用途：**
- 题目一：LLM对话核心 + 摄像头截图转base64做**实时视觉理解**（无需公网URL）
- 题目二：语音指令 → 文本后的指令解析 + Canvas绘图JSON生成

---

### 2. Image — agnes-image-2.1-flash

| 项目 | 详情 |
|------|------|
| Endpoint | `https://apihub.agnes-ai.com/v1/images/generations` |
| 认证 | `Authorization: Bearer <AGNES_API_KEY>` |
| 输出格式 | URL 或 Base64（通过 extra_body.response_format） |
| 价格 | **免费** |

**核心能力：**
- ✅ 文生图
- ✅ 图生图（image数组传入URL或Data URI Base64）
- ✅ 高信息密度图像优化
- ✅ 自定义尺寸

**注意点：**
- `response_format` 必须放在 `extra_body` 里，不能放顶层
- 图生图不需要 `tags: ["img2img"]`
- 超时建议 60-360s

**Hackathon用途：**
- 题目二：AI生图增强（语音描述 → prompt → 图片）

---

### 3. Video — agnes-video-v2.0

| 项目 | 详情 |
|------|------|
| Endpoint | `https://apihub.agnes-ai.com/v1/videos` (创建) |
| 查询 | `https://apihub.agnes-ai.com/agnesapi?video_id=<ID>` (推荐) |
| 模式 | 异步任务（创建 → 轮询 → 获取URL） |
| 最大帧数 | 441帧（8n+1） |
| 帧率 | 1-60 FPS |
| 价格 | **免费** |

**核心能力：**
- ✅ 文生视频
- ✅ 图生视频
- ✅ 多图视频生成
- ✅ 关键帧动画

**Hackathon用途：**
- 两道题核心功能都不涉及视频生成
- 可用于制作demo视频素材（非必须）

---

## 二、NVIDIA NIM（Agnes覆盖不到的补充）

### API通用信息

| 项目 | 详情 |
|------|------|
| Base URL | `https://integrate.api.nvidia.com/v1` |
| 认证 | `Authorization: Bearer <NVIDIA_API_KEY>` |
| 兼容 | OpenAI Chat Completions API |
| 费用 | **全部免费**，按调用次数限额 |

### 4. ASR（语音识别）— Agnes没有，必须用NVIDIA

| 模型 | 语言 | 实时？ | 用途 |
|------|------|--------|------|
| `nvidia/nemotron-asr-streaming` | 英语 | ✅ 流式 | 英文实时对话 |
| `nvidia/parakeet-ctc-0_6b-zh-cn` | 中文+英语 | ❌ 批量 | **中文首选**（需VAD分段） |
| `openai/whisper-large-v3` | 99+语言 | ❌ 批量 | 兜底备选 |

### 5. TTS（语音合成）— Agnes没有，必须用NVIDIA

| 模型 | 语言 | 实时？ | 用途 |
|------|------|--------|------|
| `nvidia/magpie-tts-multilingual` | 多语言 | ✅ | **综合首选**（117K免费额度） |
| `nvidia/magpie-tts-zeroshot` | 多语言 | ✅ | 零样本音色克隆 |
| `resembleai/chatterbox-multilingual-tts` | 23语言 | ✅ | 备选 |

### 6. VLM（视觉理解）— Agnes的图片理解仅限URL，视频流需NVIDIA

| 模型 | 厂商 | 用途 |
|------|------|------|
| `meta/llama-3.2-90b-vision-instruct` | Meta | **旗舰VLM**，视频帧理解首选 |
| `nvidia/nemotron-nano-12b-v2-vl` | NVIDIA | 轻量VLM备选 |

> 注意：Agnes Text 的 image_url 能力可以覆盖静态图片理解场景。
> 只有需要理解视频帧流时才需要NVIDIA VLM。

### 7. VoiceChat（全双工语音对话）— 一体化备选方案

| 模型 | 参数量 | 免费额度 | 说明 |
|------|--------|----------|------|
| `nvidia/nemotron-voicechat` | 12B | 1.77K calls | 端到端全双工 speech-to-speech |

**核心能力：**
- ✅ 端到端：一次API调用完成 ASR → LLM推理 → TTS
- ✅ 全双工：可同时听和说，支持打断
- ✅ 流式：低延迟实时对话体验
- ✅ 内置语音模型，无需单独搭配 ASR + TTS

**局限：**
- ❌ 免费额度极少（仅 1770 calls），Demo可用但不适合持续使用
- ❌ 不支持视觉输入（无法做题目一的摄像头理解）
- ❌ 无法替代 Agnes Text 的 function calling / JSON输出等高级能力
- 官方 Blueprint: [NVIDIA-AI-Blueprints/nemotron-voice-agent](https://github.com/NVIDIA-AI-Blueprints/nemotron-voice-agent)

**Hackathon用途：**
- 可作为题目一的**快速原型方案**，验证全双工语音体验
- 正式方案仍建议 Agnes Text + NVIDIA ASR/TTS 组合，额度更充足且功能更灵活

### 8. LLM（额外补充）— Agnes Text已够用，以下为备选

| 模型 | 免费额度 | 用途 |
|------|----------|------|
| `nvidia/nemotron-3-super-120b-a12b` | 60.41M | 备用主力（额度最高） |
| `deepseek-ai/deepseek-v4-flash` | 15.16M | 推理任务备用 |

---

## 三、按题目映射

### 题目一：AI 视觉对话助手

| 环节 | 首选方案 | 备选方案 | 来源 |
|------|---------|---------|------|
| 语音→文字(中文) | parakeet-ctc-0_6b-zh-cn | whisper-large-v3 | NVIDIA |
| 语音→文字(英文) | nemotron-asr-streaming | parakeet-ctc-0_6b-zh-cn | NVIDIA |
| 视觉理解(图片) | **agnes-2.0-flash (URL+base64)** | llama-3.2-90b-vision | Agnes → NVIDIA |
| 视觉理解(视频帧) | llama-3.2-90b-vision | nemotron-nano-12b-v2-vl | NVIDIA |
| 文本对话 | **agnes-2.0-flash** | nemotron-3-super-120b | Agnes → NVIDIA |
| 文字→语音 | magpie-tts-multilingual | magpie-tts-zeroshot | NVIDIA |
| 全双工语音(快速原型) | nemotron-voicechat (1770次) | — | NVIDIA（可选） |

### 题目二：AI 语音绘图工具

| 环节 | 首选方案 | 备选方案 | 来源 |
|------|---------|---------|------|
| 语音→文字(中文) | parakeet-ctc-0_6b-zh-cn | whisper-large-v3 | NVIDIA |
| 指令解析 | **agnes-2.0-flash** | nemotron-3-super-120b | Agnes → NVIDIA |
| Canvas绘图 | 纯前端 | — | 无需模型 |
| AI生图增强 | **agnes-image-2.1-flash** | flux_1-schnell | Agnes → NVIDIA |
