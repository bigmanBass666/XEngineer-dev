# 火山引擎豆包语音 API 文档索引

> **来源**：[火山引擎豆包语音文档中心](https://www.volcengine.com/docs/6561)
> **抓取时间**：2025-07-10 ~ 2025-07-12
> **用途**：Hackathon 参赛参考 — 提供离线可用的 API 协议文档

## 技术备注

火山引擎文档站为 **JS SPA 架构**，页面内容通过前端渲染，常规爬虫无法直接获取。实际通过逆向发现其内部 API：

```
https://www.volcengine.com/api/doc/getDocDetail?LibraryID=6561&DocumentID=xxx
```

该接口返回原始 Markdown（`MDContent` 字段），经 Python 脚本清洗（去除 span/anchor 标签、HTML 实体修复、空行压缩）后保存为本目录下的 `.md` 文件。

---

## 文档索引

### 🔴 核心必读（⭐⭐⭐⭐⭐）

| 文件名 | 大小 | 说明 |
|--------|------|------|
| `seed-asr-streaming.md` | 33K | ASR 大模型流式 API（WebSocket 双向流式/流式输入），含完整协议、鉴权、Demo 代码 |
| `speech-to-speech.md` | 46K | 端到端实时语音大模型（S2S）产品简介 + API 接入文档，含 RealtimeAPI WebSocket 协议 |
| `tts-http-streaming.md` | 8.0K | TTS HTTP Chunked 单向流式语音合成接口，含请求/响应参数、音频格式、高级参数 |
| `tts-websocket-streaming.md` | 9.2K | TTS WebSocket 双向流式语音合成接口，含 9 种事件协议类型 |
| `api-key-guide.md` | 3.2K | API Key 获取/使用/禁用完整指南，含 ListAPIKeys/UpdateAPIKey/DeleteAPIKey 接口 |

### 🟡 重要参考（⭐⭐⭐⭐）

| 文件名 | 大小 | 说明 |
|--------|------|------|
| `quickstart.md` | 9.4K | 控制台快速入门：API Key 获取、项目管理、模型开通、资源包购买 |
| `asr-config.md` | 21K | ASR 录音文件识别 API（非流式），含提交任务/查询结果两阶段接口及参数配置 |
| `tts-voices-params.md` | 66K | TTS 模型列表 + 音色列表合集，含 TTS 2.0/ICL 2.0 功能对比、50+ 种音色 voice_type 映射表 |
| `model-list.md` | 6.9K | 火山语音全产品线模型列表，含 ASR/TTS/S2S 各模型版本功能对比表 |
| `realtime-conversation.md` | 12K | 实时音视频场景下接入 S2S 模型的配置说明与最佳实践 |
| `voice-list-summary.md` | 49K | TTS 可用音色完整列表，203 种 voice_type 映射，覆盖 TTS 2.0/S2S/1.0 三个版本 |
| `protocol-errors.md` | 63K | WebSocket 双向/单向流式协议说明 + 错误码定义，含二进制帧格式和 protobuf schema |

### 🟢 补充材料（⭐⭐ ~ ⭐⭐⭐）

| 文件名 | 大小 | 说明 |
|--------|------|------|
| `auth-guide.md` | 835B | API Key 鉴权简要说明（`x-api-key` header 用法），内容较薄 |
| `billing.md` | 28K | 计费说明，含预付费/后付费模式、免费额度、各产品价格阶梯表 |
| `hotword-management.md` | 18K | 热词管理 API，含 ListApplications/CreateBoostingTable 等 7 个接口及请求示例 |
| `podcast-interpreter.md` | 57K | 语音播客大模型 + 同声传译 2.0 产品简介与 WebSocket API 协议文档 |
| `misc.md` | 49K | 产品动态变更日志（2025年）+ 控制台使用 FAQ + 声音复刻 2.0 最佳实践 |
| `misc-2.md` | 50K | 端到端实时语音大模型 API 接入文档详细版（与 speech-to-speech.md 内容互补） |
| `tts-extra.md` | 43K | WebSocket V3 单向流式概览 + 异步长文本语音合成接口文档合集 |

---

## 文件总量

- **文件数**：19 个 `.md` 文件
- **总大小**：约 595K
- **涵盖产品**：ASR 语音识别、TTS 语音合成、S2S 端到端语音、语音播客、同声传译