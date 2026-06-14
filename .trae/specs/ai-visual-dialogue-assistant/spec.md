# AI 视觉对话助手 Spec

## Why
构建一个 AI 视觉对话助手，用户通过摄像头展示画面并用语音与 AI 交流，AI 能同时理解视觉内容和语音问题并给出语音回复。这是一个端到端的语音+视觉多模态对话系统。

## What Changes
- 新建完整的前后端项目：前端（Vite + React + TypeScript + TailwindCSS）+ 后端（Python FastAPI + WebSocket）
- 实现 Pipeline 架构的 AI 服务编排（ASR → VLM+LLM → TTS）
- 集成三个外部 API：火山 Seed-ASR 2.0、Agnes Text (VLM+LLM)、火山 TTS 2.0
- 前端实现摄像头截图、麦克风采集 + VAD 语音活动检测、TTS 音频播放 + Barge-in 打断
- 实现前后端 WebSocket JSON 消息协议通信
- 实现多轮对话上下文管理（最近 5 轮）和自适应帧选择策略

## Impact
- Affected specs: 无（全新项目）
- Affected code: 全新项目 `xengineer-frontend/` 和 `xengineer-backend/`

## ADDED Requirements

### Requirement: 项目初始化与基础架构
系统 SHALL 提供前端项目骨架（Vite + React + TypeScript + TailwindCSS）和后端项目骨架（Python FastAPI），支持 WebSocket 端到端通信。

#### Scenario: 前后端 WebSocket 连通
- **WHEN** 前端连接后端 WebSocket 端点
- **THEN** 双方能收发 JSON 消息，连接状态正确显示

### Requirement: 外部 API 连通性验证
系统 SHALL 能够连通火山 Seed-ASR 2.0（二进制 WebSocket 协议）、Agnes Text API（SSE 流式）、火山 TTS 2.0 HTTP 接口。

#### Scenario: ASR API 连通
- **WHEN** 后端发送 PCM 音频数据给火山 ASR
- **THEN** 返回正确的文字识别结果（中间结果 + 最终结果）

#### Scenario: Agnes API 连通
- **WHEN** 后端发送文本 + base64 图片给 Agnes Text
- **THEN** 返回流式多模态对话响应

#### Scenario: TTS API 连通
- **WHEN** 后端发送文本给火山 TTS
- **THEN** 返回 MP3 音频流数据

### Requirement: 前端音频采集与 VAD 检测
系统 SHALL 提供浏览器端麦克风采集能力（16kHz mono PCM），并通过能量阈值算法实现 VAD 语音活动检测（检测说话开始/结束）。

#### Scenario: 音频采集
- **WHEN** 用户授权麦克风访问
- **THEN** 通过 AudioWorklet 采集 16kHz mono PCM 音频数据

#### Scenario: VAD 检测说话开始
- **WHEN** 用户开始说话且音频能量超过阈值
- **THEN** 触发 speaking 状态，通知后端开始接收音频

#### Scenario: VAD 检测说话结束
- **WHEN** 用户停止说话且静音持续超过阈值时间
- **THEN** 触发 silence 状态，停止发送音频，等待 AI 回复

### Requirement: 前端摄像头与帧提取
系统 SHALL 提供摄像头预览功能，并在 VAD 触发时通过 Canvas 截图获取 base64 JPEG 帧数据（640×480, quality 0.6），支持画面变化检测避免重复发送相同帧。

#### Scenario: 摄像头预览
- **WHEN** 用户打开页面并授权摄像头
- **THEN** 显示实时摄像头画面预览

#### Scenario: VAD 触发截图
- **WHEN** VAD 检测到用户开始说话
- **THEN** 对当前视频帧进行 Canvas 截图，生成 base64 JPEG 数据

#### Scenario: 画面去重
- **WHEN** 连续截图中画面内容未发生变化
- **THEN** 不重复发送相同帧数据给后端

### Requirement: 后端 ASR 节点（Pipeline Node 1）
系统 SHALL 实现 ASR Pipeline 节点，接收前端 base64 PCM 数据，解码后按火山 ASR 二进制协议转发，返回识别的文本结果。

#### Scenario: 音频流转文字
- **WHEN** 前端发送音频 chunk 给后端
- **THEN** ASR 节点解码、压缩、构造二进制 header 发送给火山 ASR，返回 interim/final 文本结果

### Requirement: 后端 VLM+LLM 节点（Pipeline Node 2）
系统 SHALL 实现 VLM+LLM Pipeline 节点，接收 ASR 最终文本 + 最新截图，构建多模态消息（system prompt + 最近 5 轮对话 + 当前图文），流式调用 Agnes Text API 并积累句子级文本触发 TTS。

#### Scenario: 多模态对话
- **WHEN** ASR 返回最终识别文本且有可用图片帧
- **THEN** VLM 节点将文本 + 图片发送给 Agnes，返回流式文本响应

#### Scenario: 句子级 TTS 触发
- **WHEN** LLM 流式输出积累到一个完整句子（以句号/问号/感叹号结尾）
- **THEN** 立即将该句子传给 TTS 节点进行语音合成

### Requirement: 后端 TTS 节点（Pipeline Node 3）
系统 SHALL 实现 TTS Pipeline 节点，接收文本调用火山 TTS 2.0 HTTP 接口，获取 Chunked MP3 音频流并通过 WebSocket 推送给前端。

#### Scenario: 文本转音频流
- **WHEN** Pipeline 传入一句话文本
- **THEN** TTS 节点调用火山 TTS API，将音频 chunk 实时推送给前端

### Requirement: Pipeline 编排器
系统 SHALL 实现 Pipeline 编排器，串联 ASR → VLM+LLM → TTS 三个节点，实现端到端数据流：用户说话 → 语音识别 → 视觉理解 → 文本生成 → 语音播放。

#### Scenario: 端到端对话流程
- **WHEN** 用户对着摄像头说话
- **THEN** 完整链路运行：音频采集 → ASR 识别 → VLM 理解（含画面）→ LLM 生成回复 → TTS 语音合成 → 前端播放

### Requirement: 前后端 WebSocket 消息协议
系统 SHALL 定义并实现标准化的前后端 JSON 消息协议，支持音频、图像、VAD 状态、ASR 结果、LLM 文本、TTS 音频等消息类型。

#### Scenario: 前端发送消息
- **WHEN** 前端需要发送数据
- **THEN** 支持 audio/image/vad_status 三种消息类型

#### Scenario: 后端推送消息
- **WHEN** 后端需要推送数据给前端
- **THEN** 支持 asr_interim/asr_final/llm_chunk/tts_audio/tts_end 五种消息类型

### Requirement: 对话 UI 界面
系统 SHALL 提供对话界面，包含聊天气泡（用户/AI 消息）、LLM 流式文字显示、连接状态/VAD 状态指示器。

#### Scenario: 显示对话内容
- **WHEN** 用户说话或 AI 回复
- **THEN** 界面以气泡形式显示对话历史，AI 回复使用流式逐字显示

### Requirement: 前端 TTS 音频播放与 Barge-in
系统 SHALL 使用 Web Audio API 播放后端推送的 TTS 音频 chunk，支持 Barge-in 打断机制（用户插话时立即停止播放并清空队列）。

#### Scenario: TTS 音频播放
- **WHEN** 后端推送 tts_audio 消息
- **THEN** 解码并顺序播放音频，保证流畅性

#### Scenario: Barge-in 打断
- **WHEN** TTS 播放期间 VAD 检测到用户说话
- **THEN** 立即停止当前播放，清空播放队列，切换回监听模式

### Requirement: 多轮对话上下文管理
系统 SHALL 实现上下文管理器，保留最近 5 轮对话历史用于构建 LLM prompt，图片只保留最新一帧。

#### Scenario: 上下文构建
- **WHEN** 发起一轮新的 VLM 请求
- **THEN** 自动拼接 system prompt + 最近 5 轮对话 + 当前图文

### Requirement: 自适应帧选择策略
系统 SHALL 实现智能帧选择器，结合 VAD 触发和画面变化检测（hash 对比），减少无效帧传输。

#### Scenario: VAD 触发截图
- **WHEN** VAD 检测到语音活动开始
- **THEN** 立即截取当前帧

#### Scenario: 静止画面跳过
- **WHEN** 截图与上一帧 hash 相同
- **THEN** 跳过该帧不发送
