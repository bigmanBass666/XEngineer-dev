# XEngineer 文档索引

## 目录结构

```
docs/
├── README.md                          <- 你在这里
├── competition-rules.md               <- 比赛规则
├── topics.md                          <- 赛题详情
├── plans/                             <- 计划文档
│   ├── archive/                       <- 已完成的计划（归档）
│   │   ├── git-hardening-plan.md
│   │   ├── hooks-persistence-plan.md
│   │   ├── volcengine-docs-assessment.md
│   │   └── strategy-adjustment.md
│   ├── devplan.md
│   ├── model-selection.md
│   ├── research-topic1.md
│   └── research-topic2.md
└── api/                               <- API 参考文档
    ├── Text.md
    ├── Image.md
    ├── Video.md
    ├── Volcengine-ASR-File.md
    ├── Volcengine-ASR-Streaming.md
    └── volcengine/
        ├── seed-asr-streaming.md
        ├── asr-config.md
        ├── auth-guide.md
        ├── quickstart.md
        ├── tts-http-streaming.md
        ├── tts-websocket-streaming.md
        ├── tts-voices-params.md
        ├── tts-extra.md
        ├── speech-to-speech.md
        ├── podcast-interpreter.md
        ├── realtime-conversation.md
        ├── hotword-management.md
        ├── billing.md
        ├── api-key-guide.md
        ├── model-list.md
        ├── voice-list-summary.md
        ├── protocol-errors.md
        ├── misc.md
        └── misc-2.md
```

---

## 一、计划文档 (plans/)

### 活跃计划

| 文件 | 说明 | 优先级 |
|------|------|--------|
| [plans/devplan.md](plans/devplan.md) | 开发规划：选题决策、架构设计、任务拆分、进度跟踪 | 核心 |
| [plans/model-selection.md](plans/model-selection.md) | 可用模型清单（Agnes AI / NVIDIA NIM），含端点与认证方式 | 核心 |
| [plans/research-topic1.md](plans/research-topic1.md) | 题目一（AI视觉对话助手）：开源项目、技术方案、架构分析 | 核心 |
| [plans/research-topic2.md](plans/research-topic2.md) | 题目二（AI语音绘图工具）：开源项目、技术方案、架构分析 | 核心 |

### 归档计划

> 以下计划已完成，仅供历史参考。

| 文件 | 说明 |
|------|------|
| [plans/archive/git-hardening-plan.md](plans/archive/git-hardening-plan.md) | Git 稳定性根治方案 |
| [plans/archive/hooks-persistence-plan.md](plans/archive/hooks-persistence-plan.md) | Hook 持久化根治方案 |
| [plans/archive/volcengine-docs-assessment.md](plans/archive/volcengine-docs-assessment.md) | 火山引擎语音文档摸底评估与抓取计划 |
| [plans/archive/strategy-adjustment.md](plans/archive/strategy-adjustment.md) | 策略调整：直接在当前仓库进行全流程开发 |

---

## 二、根目录文件

| 文件 | 说明 | 优先级 |
|------|------|--------|
| [competition-rules.md](competition-rules.md) | 比赛规则、评审标准、提交规范、代码相似度红线 | 核心 |
| [topics.md](topics.md) | 第四批次赛题详情（AI视觉对话助手 / AI语音绘图工具） | 核心 |

---

## 三、API 参考 — Agnes AI

> 平台内置 SDK，沙箱内自动鉴权，优先使用。

| 文件 | 说明 | 优先级 |
|------|------|--------|
| [api/Text.md](api/Text.md) | 聊天补全接口（agnes-2.0-flash） | 核心 |
| [api/Image.md](api/Image.md) | 图片生成接口 | 核心 |
| [api/Video.md](api/Video.md) | 视频生成接口（提交 + 轮询） | 核心 |

## 四、API 参考 — 火山引擎语音

> 来源：volcengine.com/docs/6561（豆包语音产品线）

### ASR 语音识别

| 文件 | 说明 | 优先级 |
|------|------|--------|
| [api/volcengine/seed-asr-streaming.md](api/volcengine/seed-asr-streaming.md) | ASR 大模型流式 WebSocket API（双向流式 / 流式输入 / 优化版本） | 核心 |
| [api/volcengine/asr-config.md](api/volcengine/asr-config.md) | ASR 录音文件识别 API（提交 + 查询） | 核心 |
| [api/Volcengine-ASR-File.md](api/Volcengine-ASR-File.md) | ASR 文件识别原始文档（备份） | 参考 |
| [api/Volcengine-ASR-Streaming.md](api/Volcengine-ASR-Streaming.md) | ASR 流式识别原始文档（备份） | 参考 |

### TTS 语音合成

| 文件 | 说明 | 优先级 |
|------|------|--------|
| [api/volcengine/tts-http-streaming.md](api/volcengine/tts-http-streaming.md) | TTS HTTP Chunked 单向流式接口 | 核心 |
| [api/volcengine/tts-websocket-streaming.md](api/volcengine/tts-websocket-streaming.md) | TTS WebSocket 双向流式接口（9 种事件类型） | 核心 |
| [api/volcengine/tts-voices-params.md](api/volcengine/tts-voices-params.md) | TTS 模型对比 + 50+ 音色 voice_type 映射表 | 核心 |
| [api/volcengine/tts-extra.md](api/volcengine/tts-extra.md) | TTS 补充文档 | 参考 |

### S2S 端到端语音大模型

| 文件 | 说明 | 优先级 |
|------|------|--------|
| [api/volcengine/speech-to-speech.md](api/volcengine/speech-to-speech.md) | 端到端实时语音大模型 WebSocket RealtimeAPI 协议 | 核心 |
| [api/volcengine/podcast-interpreter.md](api/volcengine/podcast-interpreter.md) | 语音播客 API + 同声传译 2.0 API（WebSocket V3 协议） | 核心 |
| [api/volcengine/realtime-conversation.md](api/volcengine/realtime-conversation.md) | 实时音视频场景接入 S2S 模型的配置说明 | 参考 |

### 鉴权与平台操作

| 文件 | 说明 | 优先级 |
|------|------|--------|
| [api/volcengine/auth-guide.md](api/volcengine/auth-guide.md) | API Key 鉴权方式（x-api-key header） | 核心 |
| [api/volcengine/quickstart.md](api/volcengine/quickstart.md) | 控制台快速入门：API Key 获取、项目/服务管理、资源包购买 | 核心 |
| [api/volcengine/api-key-guide.md](api/volcengine/api-key-guide.md) | API Key 管理（列表/更新/删除） | 参考 |
| [api/volcengine/billing.md](api/volcengine/billing.md) | 计费说明：预付费 / 后付费 / 免费额度 / 价格阶梯 | 参考 |

### 模型与音色

| 文件 | 说明 | 优先级 |
|------|------|--------|
| [api/volcengine/model-list.md](api/volcengine/model-list.md) | 全产品线模型列表（TTS 2.0 / ASR / S2S 功能对比） | 核心 |
| [api/volcengine/voice-list-summary.md](api/volcengine/voice-list-summary.md) | 全量音色列表（203 种 voice_type，覆盖 2.0 / S2S / 1.0） | 核心 |

### 协议、配置与杂项

| 文件 | 说明 | 优先级 |
|------|------|--------|
| [api/volcengine/protocol-errors.md](api/volcengine/protocol-errors.md) | WebSocket 双向/V3 单向流式协议定义 + 完整错误码表 | 核心 |
| [api/volcengine/hotword-management.md](api/volcengine/hotword-management.md) | 热词管理 API（创建 / 查询 / 应用热词表） | 参考 |
| [api/volcengine/misc.md](api/volcengine/misc.md) | 产品动态（变更日志）+ 控制台 FAQ + 声音复刻最佳实践 | 参考 |
| [api/volcengine/misc-2.md](api/volcengine/misc-2.md) | 杂项补充文档 | 参考 |