# Tasks

- [ ] Task 1: 后端项目初始化：创建 Python FastAPI 项目骨架，包含配置管理（.env）、WebSocket 端点、Pipeline 基础架构（base.py Node 基类、orchestrator.py 编排器）
  - [ ] 创建 xengineer-backend/ 目录结构
  - [ ] 实现 config.py（从 .env 读取 API Key 等配置）
  - [ ] 实现 main.py（FastAPI 入口 + WebSocket 端点 `/ws`）
  - [ ] 实现 pipeline/base.py（Node 抽象基类，统一接口）
  - [ ] 实现 pipeline/orchestrator.py（Pipeline 编排器骨架）
  - [ ] 创建 requirements.txt 和 .env.example

- [ ] Task 2: 前端项目初始化：创建 Vite + React + TypeScript + TailwindCSS 项目，实现基础页面布局和 WebSocket 连接
  - [ ] 初始化 Vite + React + TS 项目（xengineer-frontend/）
  - [ ] 配置 TailwindCSS
  - [ ] 实现 App.tsx 基础布局（摄像头区域 + 对话区域 + 状态栏）
  - [ ] 实现 hooks/useWebSocket.ts（WebSocket 连接管理、消息收发、重连）
  - [ ] 实现 lib/protocol.ts（前后端消息协议类型定义）

- [ ] Task 3: 前后端 WebSocket 连通测试：确保前后端能通过 WebSocket 收发 JSON 消息
  - [ ] 前端连接后端 WS 端点成功
  - [ ] 前端发送测试消息，后端正确接收并回复
  - [ ] 连接状态在 UI 上正确显示

- [ ] Task 4: 火山 ASR API 连通性验证：实现火山 Seed-ASR 2.0 二进制 WebSocket 协议客户端，能正确识别音频并返回文本
  - [ ] 实现 services/volcengine_asr.py（二进制协议客户端：PCM 解码、Gzip 压缩、4字节 header 构造、WebSocket 通信）
  - [ ] 实现 pipeline/asr_node.py（ASR Pipeline 节点，接收前端音频 → 调用 ASR 服务 → 返回文本结果）
  - [ ] 用测试音频验证 ASR 能返回 interim + final 结果

- [ ] Task 5: Agnes Text API 连通性验证：实现 Agnes API 客户端，支持多模态（文本+图片）流式调用
  - [ ] 实现 services/agnes_client.py（Agnes API 客户端：SSE 流式请求、多模态消息构建）
  - [ ] 验证能发送文本+base64图片并获取流式响应

- [ ] Task 6: 火山 TTS API 连通性验证：实现火山 TTS 2.0 HTTP 客户端，能将文本转为 MP3 音频流
  - [ ] 实现 services/volcengine_tts.py（TTS HTTP 客户端：X-Api-Key 鉴权、Chunked 音频流接收）
  - [ ] 验证能输入文本并获得 MP3 音频数据

- [ ] Task 7: 前端麦克风采集与 VAD 检测：实现浏览器端麦克风 PCM 采集和能量阈值 VAD 算法
  - [ ] 实现 hooks/useVAD.ts（AudioWorklet PCM 采集逻辑）
  - [ ] 实现 lib/vad.ts（能量阈值 VAD 算法：检测 speaking/silence 状态切换）
  - [ ] 实现 components/AudioRecorder.tsx（麦克风采集 UI 组件）
  - [ ] VAD 检测到说话开始/结束时通过 WS 发送 vad_status 消息

- [ ] Task 8: 前端摄像头与 Canvas 截图：实现摄像头预览和 VAD 触发式截图 + 画面变化检测
  - [ ] 实现 hooks/useCamera.ts（getUserMedia 摄像头管理）
  - [ ] 实现 components/Camera.tsx（摄像头预览 + Canvas 截图，640×480 JPEG quality 0.6）
  - [ ] VAD 触发时自动截图并通过 WS 发送 image 消息
  - [ ] 实现画面 hash 变化检测，静止画面不重复发送

- [ ] Task 9: 后端 VLM+LLM 节点完整实现：接收 ASR 文本 + 图片帧，调用 Agnes API，实现句子级 TTS 触发
  - [ ] 实现 pipeline/vlm_node.py（VLM+LLM 节点：多模态 prompt 构建、流式调用 Agnes、句子积累逻辑）
  - [ ] System Prompt 设计：AI 视觉对话助手角色设定
  - [ ] 流式输出同时推送 llm_chunk 给前端显示

- [ ] Task 10: 后端 TTS 节点完整实现：接收文本调用火山 TTS，音频 chunk 通过 WS 推送前端
  - [ ] 实现 pipeline/tts_node.py（TTS 节点：接收文本 → 调用 TTS 服务 → 音频 chunk 推送）

- [ ] Task 11: Pipeline 编排器串联全链路：实现 ASR → VLM+LLM → TTS 完整数据流编排
  - [ ] 完善 orchestrator.py（节点间数据传递、状态管理、错误处理）
  - [ ] 端到端联调：用户说话 → ASR → VLM → LLM → TTS → 播放

- [ ] Task 12: 对话 UI 界面：实现聊天气泡、流式文字显示、状态指示器
  - [ ] 实现 components/ChatBubble.tsx（用户消息/AI 消息气泡组件）
  - [ ] AI 回复使用流式逐字显示效果
  - [ ] 实现 components/StatusBar.tsx（连接状态、VAD 状态、处理中指示）

- [ ] Task 13: 前端 TTS 音频播放器与 Barge-in 打断：Web Audio API 播放 + 用户插话打断机制
  - [ ] 实现 components/AudioPlayer.tsx（接收 tts_audio chunk → base64 解码 → AudioBuffer → 队列播放）
  - [ ] Barge-in 逻辑：VAD 检测到说话时停止播放 + 清空队列 + 通知后端取消 TTS

- [ ] Task 14: 多轮对话上下文管理：实现 ContextManager，保留最近 5 轮对话历史
  - [ ] 实现 managers/context.py（上下文存储、轮次管理、prompt 构建）
  - [ ] 图片只保留最新一帧
  - [ ] 与 VLM 节点集成

- [ ] Task 15: 自适应帧选择策略完善：整合 VAD 触发截图 + 画面变化检测
  - [ ] 实现 managers/frame.py（帧选择策略：VAD 触发 + hash 去重 + 时间窗口控制）
  - [ ] 与前端 Camera 组件集成

# Task Dependencies
- [Task 2] depends on [Task 1]
- [Task 3] depends on [Task 1, Task 2]
- [Task 4] depends on [Task 1]
- [Task 5] depends on [Task 1]
- [Task 6] depends on [Task 1]
- [Task 7] depends on [Task 2, Task 3]
- [Task 8] depends on [Task 2, Task 3, Task 7]
- [Task 9] depends on [Task 4, Task 5]
- [Task 10] depends on [Task 6]
- [Task 11] depends on [Task 4, Task 5, Task 6, Task 9, Task 10]
- [Task 12] depends on [Task 2, Task 3]
- [Task 13] depends on [Task 3, Task 7, Task 12]
- [Task 14] depends on [Task 9]
- [Task 15] depends on [Task 8, Task 14]
