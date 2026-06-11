# XEngineer 可用模型筛选结果

> 来源: nvidia-models-overview.md (NVIDIA NIM)
> 筛选时间: 2026-06-12
> API Base URL: https://integrate.api.nvidia.com/v1
> 认证: Authorization: Bearer <NVIDIA_API_KEY>
> 兼容: OpenAI Chat Completions API 格式
> 费用: 全部 Free，按调用次数限额

---

## 一、LLM（文本对话）

### 主力推荐
| 模型 | 免费额度 | 用途 |
|------|----------|------|
| `nvidia/nemotron-3-super-120b-a12b` | 60.41M | 主力对话（额度最高，120B级能力） |
| `deepseek-ai/deepseek-v4-flash` | 15.16M | 推理任务（速度快） |
| `meta/llama-3.3-70b-instruct` | 18.79M | 通用对话（生态成熟） |

### 轻量/路由
| 模型 | 免费额度 | 用途 |
|------|----------|------|
| `meta/llama-3_1-8b-instruct` | 25.09M | 低延迟分类/预处理 |
| `nvidia/nemotron-3-nano-30b-a3b` | 11.91M | 极速场景 |

### 特殊
| 模型 | 免费额度 | 用途 |
|------|----------|------|
| `nvidia/nemotron-voicechat` | - | **语音对话专用**（实时语音交互） |

---

## 二、ASR（语音识别）

### 首选
| 模型 | 语言 | 特性 | 适合实时？ |
|------|------|------|-----------|
| `nvidia/nemotron-asr-streaming` | 英语 | **唯一流式模型**，WebSocket逐帧 | ✅ 实时首选 |
| `nvidia/parakeet-ctc-0_6b-zh-cn` | 中文+英语 | 0.6B轻量，record-setting准确率 | ⚠️ 非流式，需VAD分段 |
| `openai/whisper-large-v3` | 99+语言 | 鲁棒性最强，抗噪 | ❌ 延迟高，仅离线 |

### 中文实时方案
中文无流式ASR，需用 parakeet-ctc-0_6b-zh-cn + VAD分段 + 批量送入。

---

## 三、TTS（语音合成）

### 首选
| 模型 | 特性 | 免费额度 | 适合实时？ |
|------|------|----------|-----------|
| `nvidia/magpie-tts-multilingual` | 多语言，自然音色，支持Download | 117K | ✅ **综合首选** |
| `nvidia/magpie-tts-zeroshot` | 零样本音色克隆（几秒音频克隆） | - | ✅ 个性化场景 |
| `resembleai/chatterbox-multilingual-tts` | 23语言，自然有表现力 | 7.21K | ✅ 备选 |

---

## 四、VLM（视觉理解）

### 可用模型
| 模型 | 厂商 | 参数量 | 特性 |
|------|------|--------|------|
| `meta/llama-3.2-90b-vision-instruct` | Meta | 90B | **旗舰VLM**，视觉对话首选 |
| `meta/llama-3.2-11b-vision-instruct` | Meta | 11B | 轻量VLM，延迟低 |
| `nvidia/nemotron-nano-12b-v2-vl` | NVIDIA | 12B | Nemotron视觉版 |
| `nvidia/llama-3.1-nemotron-nano-vl-8b-v1` | NVIDIA | 8B | 纳米VLM |
| `microsoft/phi-4-multimodal-instruct` | Microsoft | - | Phi-4多模态 |
| `google/google-paligemma` | Google | - | 专用视觉理解 |
| `nvidia/nemotron-parse` | NVIDIA | - | 文档解析VLM（非通用） |

> ⚠️ Qwen在NIM上无VLM模型。OpenAI在NIM上无GPT-4V。

---

## 五、图像生成

### 首选
| 模型 | 特性 | 适合实时？ | 免费额度 |
|------|------|-----------|----------|
| `black-forest-labs/flux_1-schnell` | 速度+质量平衡 | ✅ | 253K |
| `black-forest-labs/flux_1-dev` | SOTA画质 | ❌ | 246K |
| `black-forest-labs/flux_2-klein-4b` | 4B轻量，极速生成+编辑 | ✅ | 271K |
| `qwen/qwen-image` | 多语言文字渲染 | ⚠️ | - |

---

## 六、语音翻译（可选）

| 模型 | 语言 | 免费额度 | 用途 |
|------|------|----------|------|
| `nvidia/riva-translate-4b-instruct-v1_1` | 12语言 | 282K | 跨语言对话中间环节 |
| `nvidia/riva-translate-1_6b` | 36语言 | - | 轻量备选 |

---

## 七、关键发现

### 对题目一（AI视觉对话助手）的覆盖度
| 环节 | 方案 | 覆盖度 |
|------|------|--------|
| 语音识别 | parakeet-ctc-0_6b-zh-cn（中文） / nemotron-asr-streaming（英文） | ✅ |
| 视觉理解 | llama-3.2-90b-vision-instruct / nemotron-nano-12b-v2-vl | ✅ |
| 文本对话 | nemotron-3-super-120b-a12b / deepseek-v4-flash | ✅ |
| 语音合成 | magpie-tts-multilingual | ✅ |
| **结论** | NVIDIA NIM 全链路覆盖 | ✅✅✅ |

### 对题目二（AI语音绘图工具）的覆盖度
| 环节 | 方案 | 覆盖度 |
|------|------|--------|
| 语音识别 | parakeet-ctc-0_6b-zh-cn / nemotron-asr-streaming | ✅ |
| 指令解析 | nemotron-3-super-120b-a12b（LLM解析语音→绘图指令） | ✅ |
| Canvas绘图 | 纯前端实现，不需要模型 | ✅ |
| AI生图（可选增强） | flux_1-schnell / flux_2-klein-4b | ✅ |
| **结论** | 全链路覆盖，且依赖更少 | ✅✅✅ |

### 特别关注
- `nvidia/nemotron-voicechat`：**语音对话专用模型**，可能直接覆盖题目一的核心需求，需进一步调研
- 中文ASR无流式支持，这是题目一最大的技术挑战
