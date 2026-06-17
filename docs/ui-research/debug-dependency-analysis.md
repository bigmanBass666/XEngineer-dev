# XEngineer 调试依赖性研究报告

> 生成者: subagent-R1 (Task ID 21)
> 目的: 评估前端布局重设计（从"调试面板"到"视频通话"风格）是否会破坏现有调试能力
> 范围: `XEngineer/tests/` + `XEngineer/scripts/` + `xengineer-frontend/src/` + `xengineer-backend/app/`
> 基线: `feat/improve-ui` 分支（main `5f06fcb`）

---

## TL;DR

- **可以放心重做布局**：核心 pipeline 调试（WS → ASR → VLM → TTS）通过 Python 直连后端，**完全独立于前端 UI**。
- **需要同步调整** 5 个测试脚本中依赖 UI 文案/DOM 文本的检查点（如按钮文案 "录音"、"已连接" 字样、h1 标题等）。
- **需要保留** "发送测试消息"功能链路（但不一定保留按钮 UI），因为 `netlify_e2e_test.sh` 依赖它做连通性验证；建议改用 agent-browser `eval` 直接发 WS 消息替代。
- **强烈建议新增** 一个独立的 `tests/ws_debug_client.py`（基于 `test_pipeline_e2e.py` 提炼）作为日常调试入口，进一步降低对 UI 的依赖。

---

## 1. 现有调试方法清单

### 1.1 测试文件

仓库 `tests/` 目录共 7 个测试文件 + 2 个 fixture 目录，全部由 `run_all_tests.sh` 编排：

| 文件 | 测试目标 | 是否依赖 UI | 依赖详情 |
|------|----------|------------|----------|
| `tests/run_all_tests.sh` | 一键测试入口（编排 6 个步骤） | 部分 | 步骤 5/6 调用 UI 测试；步骤 1/2/3/4 不依赖 |
| `tests/test_pipeline_e2e.py` | WS → ASR → VLM+LLM → TTS 完整链路 | **❌ 不依赖** | Python `websockets` 直连 `wss://...railway.app/ws`，发 `{vad_status, image, audio}` 验证 `{asr_final, llm_chunk, tts_audio, tts_end}`。**这是核心 pipeline 调试工具，与前端 0 耦合** |
| `tests/test_frontend_visual.sh` | 前端页面加载/标题/JS 错误/UI 元素/console | ✅ 依赖 | agent-browser 打开 Netlify 页面，截图 + 检查 title 含 `xengineer\|XEngineer\|视觉\|对话\|AI`，检查 snapshot 含 `button/input/...`，检查 console 含 `connected\|连接成功` |
| `tests/test_browser_e2e.sh` | 浏览器级 VAD → ASR → VLM → TTS UI 渲染验证 | ✅ 强依赖 | agent-browser 打开 Netlify → 注入 `mock_getusermedia.js` → 点击"录音"按钮（snapshot 提取 `button.*录音.*[ref=...]`）→ 检查 DOM 含 "已连接" + ASR 关键词 + "AI" 标签 |
| `tests/netlify_e2e_test.sh` | Netlify 线上全真测试（含"发送测试消息"按钮） | ✅ 强依赖 | agent-browser → 找"发送测试消息"按钮（`button.*测试.*` 或 `button.*发送.*`）→ 点击 → 检查 DOM 含 "测试消息"/"hello from frontend"/"WS echo" → 找"录音"按钮 → 检查 DOM 含 "已连接" → 检查 `<video>` 元素 `transform: scaleX(-1)` |
| `tests/prepare_test_audio.py` | 预合成 5 条中文 TTS 音频 → `test_audio_set.json` | **❌ 不依赖** | 用 `z-ai tts` CLI 合成 + ffmpeg 重采样到 16kHz PCM，base64 编码 |
| `tests/fixtures/mock_getusermedia.js` | 浏览器注入脚本，monkey-patch `getUserMedia` 返回虚拟 MediaStream | **❌ 不依赖 UI 本身** | 注入到页面后通过 `window.__mockAudio.setAudio(Float32Array).startFeeding()` 触发音频流，与 UI 解耦；但需要 UI 有调用 `getUserMedia({audio})` 的入口（当前是"录音"按钮） |
| `tests/fixtures/video-frames/frame_0[1-5].jpg` | 测试图片素材 | **❌ 不依赖** | 静态 JPEG 文件 |
| `tests/fixtures/test_audio_set.json` | 测试音频数据（PCM base64） | **❌ 不依赖** | 由 `prepare_test_audio.py` 生成 |

### 1.2 测试脚本（非 tests/ 目录）

| 脚本 | 用途 | 是否依赖 UI |
|------|------|------------|
| `scripts/setup.sh` | 环境初始化（git/python/node/npm/gh/railway/netlify/agent-browser 安装 + Python 依赖 + 前端 build 验证 + .env 模板 + git hooks + remote 同步） | **❌ 不依赖** | 仅做工具链准备，最后跑一次 `npm run build` 验证 TS 编译通过 |

> 注：`XEngineer/` 根目录还散落着 `Procfile` / `nixpacks.toml` / `runtime.txt` 等部署配置，与调试无关。

### 1.3 前端 package.json scripts

```json
"scripts": {
  "dev": "vite",
  "build": "tsc && vite build",
  "preview": "vite preview"
}
```

- **无 `test` 脚本** — 前端没有单元测试 / 集成测试 / e2e 测试框架（无 vitest/jest/playwright/cypress）。
- 前端唯一"测试"方式是通过 agent-browser 直接打开 Netlify 部署后的页面做黑盒验证。

### 1.4 前端内嵌调试元素

| 调试元素 | 位置 | 作用 | 是否可移除 |
|---------|------|------|-----------|
| **"发送测试消息"按钮** | `App.tsx:151-156` | 触发 `send({ type:'test', data:'hello from frontend' })`，后端回 `{type:'status', message:'WS echo: ...'}`，前端在对话区追加 system 气泡 | ⚠️ **可移除 UI，但需保留协议** — `netlify_e2e_test.sh` 第 2 节依赖此按钮验证 WS 连通性；建议改用 `agent-browser eval` 直接 `JSON.stringify({type:'test',data:'...'})` 通过 ws 发送 |
| **`console.log` 调用** | 11 处：`useWebSocket.ts`（4 处 WS 状态）+ `useVAD.ts`（1 处启动失败）+ `useCamera.ts`（1 处启动失败）+ `AudioPlayer.tsx`（1 处解码错误）+ `App.tsx`（2 处 Status/Error 消息） | 全部是运行时日志，非交互式调试面板 | ✅ 可全部保留 / 升级为统一 logger；`test_frontend_visual.sh` 依赖 console 含 "connected\|连接成功" 字样，所以 `[WS] Connected` 日志需保留 |
| **`<canvas className="hidden">`** | `Camera.tsx:34` | 隐藏的截图 canvas，非调试元素 | ❌ 不可移除（Camera 截图功能依赖） |
| **隐藏的 `<details>` 调试面板** | — | — | — **不存在**（grep 全代码无 `<details>` / `display:none` 的调试面板） |
| **隐藏的 `debug` / `dev` 模式开关** | — | — | — **不存在** |

### 1.5 后端独立调试入口

| 入口 | 状态 | 详情 |
|------|------|------|
| **健康检查端点** | ✅ 有 | `GET /health` → `{"status":"ok","service":"xengineer-backend"}`（`main.py:110-113`） |
| **CLI 测试入口** | ❌ 无 | 没有 `python main.py --test` 之类的命令行测试参数；`main.py` 仅作为 uvicorn app 入口 |
| **Stub 模式** | ✅ 有 | 环境变量 `USE_REAL_NODES=false`（默认）→ 后端用 `StubNode` 返回 `[ASR stub] / [VLM stub] / [TTS stub]`，无需真实火山引擎凭证即可启动 |
| **启动配置 print** | ✅ 有 | `main.py:33-43` 启动时打印 `USE_REAL_NODES` + 4 个 API Key（脱敏 `xxxx****xxxx`） |
| **Python `logging`** | ✅ 有 | 4 处 `logging.getLogger`：`main` / `orchestrator` / `vlm_node` / `agnes_client`；级别默认 INFO（`orchestrator.handle_image` 用 `logger.debug`，默认不输出） |
| **`print` 调用** | ⚠️ 12 处 | `main.py` 启动配置（8 处）+ `volcengine_asr.py` ASR 错误（1 处）+ `volcengine_tts.py` TTS 错误（5 处，含 403 Forbidden 提示）。这些 `print` 输出到 stdout，**Railway 日志可直接看到** |
| **独立的 WS 测试客户端** | ✅ 有（间接） | `tests/test_pipeline_e2e.py` 本质就是一个独立 WS 客户端，可单独运行 `python3 tests/test_pipeline_e2e.py` 调试后端 |

### 1.6 WebSocket 协议调试

#### 协议定义（`src/lib/protocol.ts`）

```
ClientMessage (前端 → 后端，4 种):
  - {type:'audio', data: base64-pcm-int16}     — 用户说话 PCM 音频
  - {type:'image', data: base64-jpeg}          — VAD 触发的摄像头截图
  - {type:'vad_status', speaking: boolean}     — VAD 状态（后端依赖此启动/停止 ASR 会话）
  - {type:'test', data: string}                — 测试消息（后端回 status echo）

ServerMessage (后端 → 前端，7 种):
  - {type:'asr_interim', text}                 — ASR 中间结果
  - {type:'asr_final', text}                   — ASR 最终结果
  - {type:'llm_chunk', text}                   — LLM 流式回复片段
  - {type:'tts_audio', data: base64-mp3}       — TTS 音频片段
  - {type:'tts_end'}                           — TTS 流结束
  - {type:'status', message}                   — 状态消息（含 `asr_session_started/stopped`、`WS echo: ...`）
  - {type:'error', message}                    — 错误消息
```

#### 独立 WS 客户端

- ✅ **`tests/test_pipeline_e2e.py` 就是独立 WS 客户端**：用 `websockets` 库直连 `wss://xengineer-dev-production.up.railway.app/ws`，发送 4 种 ClientMessage，接收并解析 7 种 ServerMessage，5 条测试语句覆盖完整 VAD → ASR → VLM → TTS 链路。**这是后端调试的黄金标准，与前端 UI 完全解耦**。

#### 可用工具

| 工具 | 用途 | 是否已用 |
|------|------|---------|
| Python `websockets` 库 | 编程式 WS 客户端 | ✅ `test_pipeline_e2e.py` |
| `wscat` | 命令行交互式 WS 客户端 | ❌ 未用，但可即时引入 `npm i -g wscat && wscat -c wss://.../ws` |
| `curl --include --http1.1 --upgrade` | HTTP upgrade 握手验证 | ❌ 未用 |
| `agent-browser eval` | 在浏览器内通过页面已建立的 WS 连接发消息 | ❌ 未用，但 `netlify_e2e_test.sh` 可改为用此方式替代"发送测试消息"按钮 |

#### 评估结论

**完全能不依赖前端 UI 调试 WS 协议**。后端 CORS 配置 `allow_origins=["*"]`（`main.py:103`），接受任意来源的 WebSocket 连接；`/ws` 端点协议简单（JSON 文本帧），任何 WS 客户端均可连接测试。

---

## 2. 调试能力对 UI 的依赖度评估

### 2.1 强依赖（UI 改动会破坏）

> 这些检查点如果 UI 改造时未同步调整，对应测试会失败。

| 测试脚本 | 检查点 | UI 元素/文本 | 改造时必须保留或同步更新 |
|---------|--------|-------------|----------------------|
| `test_frontend_visual.sh:128` | 页面标题 | `<title>` 含 `xengineer\|XEngineer\|视觉\|对话\|AI` | 保留 `<title>XEngineer - AI 视觉对话助手</title>` 或同步更新脚本的 grep 模式 |
| `test_frontend_visual.sh:178` | UI 元素存在 | snapshot 含 `button/input/textarea/chat/send/message/camera/video/canvas/div` 之一 | 改造后页面必须有 `button` + `video` + `canvas`（建议都保留） |
| `test_frontend_visual.sh:215` | WS 连接日志 | console 含 `websocket.*open\|ws.*open\|connected\|连接成功` | 保留 `useWebSocket.ts` 的 `console.log('[WS] Connected')` |
| `test_browser_e2e.sh:234-241` | WS 连接状态 | DOM 文本含 "已连接" 或 "Connected" | StatusBar 中保留 "已连接" 文案（或同步更新脚本） |
| `test_browser_e2e.sh:347-351` | 录音按钮定位 | snapshot 含 `button.*录音.*[ref=...]` 或 `button.*(mic\|audio).*[ref=...]` | 录音按钮文案必须含 "录音" 或 "mic"/"audio" |
| `test_browser_e2e.sh:412` | ASR 结果 UI 渲染 | DOM 含 ASR 关键词（如 "你好"） | 用户消息气泡必须渲染 `asr_final` 的文本到 DOM |
| `test_browser_e2e.sh:418` | LLM 响应 UI 渲染 | DOM 含 "AI" 字样 | AI 回复气泡必须包含 "AI" 文本（当前是头像 `bg-blue-600` + "AI" 两字） |
| `netlify_e2e_test.sh:102` | 页面标题 | `<h1>` 文本含 "XEngineer" | 保留 `<h1>` 且文本含 "XEngineer" |
| `netlify_e2e_test.sh:116-118` | 测试消息按钮定位 | snapshot 含 `button.*测试.*[ref=...]` 或 `button.*发送.*[ref=...]` | **保留"发送测试消息"按钮**，或脚本改为用 `agent-browser eval` 直接发 WS 消息 |
| `netlify_e2e_test.sh:136-140` | 用户消息 UI 渲染 | DOM 含 "测试消息" 或 "hello from frontend" | 用户消息气泡渲染逻辑保留 |
| `netlify_e2e_test.sh:144` | 系统回显 UI 渲染 | DOM 含 "回显" 或 "WS echo" | system 消息气泡渲染 `WS echo:` 消息的逻辑保留（`App.tsx:73-81`） |
| `netlify_e2e_test.sh:233` | 录音按钮定位 | snapshot 含 `button.*录音.*[ref=...]` | 同 `test_browser_e2e.sh` |
| `netlify_e2e_test.sh:275-294` | 视频镜像 | `<video>` 元素 `transform` 含 `-1` 或 `scaleX(-1)` | 视频镜像 `scaleX(-1)` 必须保留 |

### 2.2 弱依赖（UI 改动需要同步调整调试方法）

| 调试方法 | 当前依赖 | 调整建议 |
|---------|---------|---------|
| `mock_getusermedia.js` 注入 | UI 必须有调用 `getUserMedia({audio})` 的入口（当前是"录音"按钮点击触发 `useVAD.start()`） | 改造后只要保留"开始通话/麦克风"按钮即可；如果改成"页面加载即自动开启"，需在 agent-browser 注入 hook 后再触发，否则 hook 注入时机晚于 getUserMedia 调用 |
| agent-browser snapshot 按钮定位 | 按钮文案（"录音"/"测试"/"发送"）作为正则匹配 | 建议给关键按钮加 `data-testid="mic-btn"` / `data-testid="test-btn"`，脚本改为按 `data-testid` 定位，文案改动后零成本 |
| `console.log` 日志格式 | `test_frontend_visual.sh` 搜索 `connected\|连接成功` | 建议统一为 `console.log('[WS] Connected')` 格式，所有 WS 状态日志保留 `[WS]` 前缀 |
| 前端 dev server 启动 | `npm run dev` 监听 5173 端口 | 改造时不要改 `vite.config.ts` 的 port 配置；如果改了需同步更新 baseline 截图脚本 |

### 2.3 不依赖（UI 改动完全无影响）

| 调试方法 | 说明 |
|---------|------|
| `tests/test_pipeline_e2e.py` | Python `websockets` 直连后端，与前端 0 耦合。**核心 pipeline 调试 100% 不受 UI 改动影响** |
| `tests/prepare_test_audio.py` | TTS 合成音频，纯 CLI |
| `tests/fixtures/mock_getusermedia.js` | 浏览器注入脚本，与 UI 解耦 |
| `tests/fixtures/test_audio_set.json` | 预合成音频数据 |
| `tests/fixtures/video-frames/*.jpg` | 静态测试图片 |
| 后端 `/health` 端点 | 与前端无关 |
| 后端 `USE_REAL_NODES=false` Stub 模式 | 与前端无关 |
| 后端 `print` 启动配置 + `logging` | 与前端无关 |
| 后端 WS 协议（4 Client / 7 Server 消息） | 协议定义在 `protocol.ts`，但只要后端 `main.py:116-183` 的消息处理不变，前端 UI 改造不影响后端 |
| `scripts/setup.sh` | 环境初始化，与前端 UI 无关 |
| `run_all_tests.sh` 步骤 1/2/3/4 | 健康检查 + 前端 HTTP 200 + TTS→ASR 沙箱 + Pipeline E2E，全部不依赖 UI 渲染 |

### 2.4 前端状态管理对 UI 的依赖分析

| 状态 | 当前用途 | UI 不显示后是否还有意义 | 改造建议 |
|------|---------|----------------------|---------|
| `messages: ChatMessage[]` | 渲染到 `<ChatBubble>` 列表 | ❌ 无其他用途，纯 UI 显示 | 改造时可保留为内部状态供浮动字幕使用；也可改为只保留最近 N 条用于浮动 UI |
| `currentAIResponse: string` | 渲染到 `<StreamingMessage>` 流式气泡 | ❌ 无其他用途，纯 UI 显示 | 改造为浮动 AI 字幕的核心数据源 |
| `isAIProcessing: boolean` | StatusBar 显示 "AI 处理中" spinner | ⚠️ 由 `llm_chunk`/`tts_end` 触发，无副作用 | 状态本身不驱动行为，可改为驱动浮动控制条的 spinner 动效 |
| `vadStatus: VADStatus` | StatusBar 显示 "正在说话/静音" | ⚠️ 仅在 StatusBar 中显示；VAD 状态变化的实际逻辑在 `handleVADStateChange` 中直接处理（`audioPlayer.stop()` + `send vad_status` + `setShouldCapture`），**不依赖 vadStatus state** | 改造为浮动控制条的麦克风状态指示；即使不显示，VAD 触发链路也能工作 |
| `shouldCapture: boolean` | 触发 `Camera.useEffect` 截图 | ✅ 与 UI 显示无关，纯逻辑触发器 | 保留即可，与 UI 改造无关 |
| `connectionStatus` (来自 `useWebSocket`) | StatusBar 显示 "已连接/未连接/连接中/连接错误" | ⚠️ 仅在 StatusBar 显示；不影响 WS 收发逻辑 | 改造为浮动控制条的状态指示；`test_browser_e2e.sh` / `netlify_e2e_test.sh` 依赖 DOM 含 "已连接"，所以状态文案需保留或同步更新测试 |

> **关键发现**：所有 React state 都不驱动核心逻辑，核心 VAD → barge-in → ASR → VLM → TTS 链路全部在 `handleVADStateChange` 中通过副作用直接执行。**这意味着 UI 改造可以完全重做布局，只要保留 `handleVADStateChange` 中的 3 个副作用调用即可**：
> 1. `audioPlayer.stop()` — barge-in 打断 TTS
> 2. `send({ type:'vad_status', speaking })` — 通知后端启停 ASR 会话
> 3. `setShouldCapture(true)` + 100ms 后 `setShouldCapture(false)` — 触发摄像头截图

---

## 3. 重做布局的可行性结论

### 3.1 结论

✅ **可以放心重做布局**，但有 5 个测试脚本依赖 UI 文案/DOM 文本，需同步调整或保留关键 UI 元素。

**理由**：
1. **核心 pipeline 调试 100% 独立于 UI** — `test_pipeline_e2e.py` 用 Python 直连后端 WS，覆盖完整 VAD → ASR → VLM → TTS 链路，5 条测试语句 + 关键词匹配验证。这是后端调试的"黄金标准"，完全不受前端布局改造影响。
2. **后端独立可调试** — `/health` 端点 + `USE_REAL_NODES=false` Stub 模式 + `print` 启动配置 + Python `logging` + 12 处 `print` 错误输出，后端可独立启动、独立验证、独立排查问题。
3. **WS 协议简单且开放** — 4 Client / 7 Server 消息类型，CORS `allow_origins=["*"]`，任何 WS 客户端均可连接测试。
4. **前端状态管理与核心逻辑解耦** — 所有 React state 都是纯 UI 显示，核心 VAD 触发链路在 `handleVADStateChange` 副作用中执行，UI 改造只要保留这 3 个副作用调用即可。
5. **没有隐藏的调试面板** — 前端代码 grep 无 `<details>` / `display:none` 调试面板，无 `debugger` 语句，无 `dev` 模式开关。

### 3.2 重做布局时必须保留的调试入口

> 这些是 UI 改造后必须保留的元素/逻辑，否则会破坏现有测试或核心功能。

| 必须保留项 | 原因 | 改造建议 |
|-----------|------|---------|
| **`<h1>` 标题含 "XEngineer"** | `netlify_e2e_test.sh:102` 检查 | 保留 header 中的 `<h1>XEngineer ...</h1>`，可改样式但文本要含 "XEngineer" |
| **`<title>` 标签含 `XEngineer\|视觉\|对话\|AI`** | `test_frontend_visual.sh:128` 检查 | 保留 `<title>XEngineer - AI 视觉对话助手</title>` |
| **"已连接" 状态文案** | `test_browser_e2e.sh` + `netlify_e2e_test.sh` 检查 DOM 含 "已连接" | 浮动控制条/状态指示器中保留 "已连接" 文本（或同步更新 2 个脚本） |
| **录音按钮文案含 "录音" 或 "mic"/"audio"** | `test_browser_e2e.sh:347` + `netlify_e2e_test.sh:233` 用 snapshot 正则定位 | 浮动控制条的麦克风按钮保留 "录音" 文案或 aria-label，**强烈建议改用 `data-testid="mic-btn"` 后同步更新脚本** |
| **`<video>` 元素 `transform: scaleX(-1)` 镜像** | `netlify_e2e_test.sh:275-294` 检查 | 全屏视频保留镜像 |
| **`handleVADStateChange` 中的 3 个副作用** | 核心功能（barge-in + ASR 会话 + 摄像头截图） | 改造时不要破坏 `App.tsx:115-128` 的逻辑，可抽成 `useConversationOrchestrator` hook |
| **`audioPlayer` 单例（24kHz AudioContext）** | TTS 播放 + barge-in 依赖 | 不要新建 AudioContext，订阅 `audioPlayer.setCallback` |
| **getUserMedia 用户手势触发** | 浏览器自动播放策略 | 浮动控制条的"开始通话"按钮触发 `useVAD.start()` + `useCamera.start()`，不能改自动触发 |
| **WS 状态 `console.log('[WS] Connected')`** | `test_frontend_visual.sh:215` 搜索 console | 保留 `useWebSocket.ts` 的 WS 状态日志 |
| **"发送测试消息" 功能链路** | `netlify_e2e_test.sh:113-160` 依赖此按钮 + WS echo 回显 | **可移除按钮 UI，但保留 `sendTest` 函数**；或脚本改为用 `agent-browser eval` 直接发 WS 消息（见 §3.4 建议） |
| **system 气泡渲染 `WS echo:` 消息** | `netlify_e2e_test.sh:144` 检查 DOM 含 "回显" / "WS echo" | 保留 `App.tsx:73-81` 的 `WS echo:` 消息渲染逻辑，可改为浮动通知 |
| **用户/AI 消息气泡渲染到 DOM** | `test_browser_e2e.sh:412-418` 检查 DOM 含 ASR 关键词 + "AI" 字样 | 浮动字幕必须将 `asr_final.text` 和 LLM 回复渲染到 DOM（不能只在 console） |

### 3.3 重做布局时可以删除的调试元素

| 可删除项 | 原因 | 替代方案 |
|---------|------|---------|
| **左右双栏布局** | 仅是视觉布局，不影响功能 | 改为全屏视频 + 浮动控制条 + 浮动 AI 字幕 |
| **"暂无对话"空状态 SVG** | 仅是 UI 占位 | 改为全屏视频背景 + 引导提示 |
| **底部提示 "语音输入已就绪..."** | 仅是 UI 文案 | 改为浮动控制条的 tooltip |
| **StatusBar 的固定底部栏布局** | 仅是 UI 布局 | 改为浮动控制条上的状态指示 |
| **"发送测试消息"按钮 UI**（可选） | 仅是测试入口 | 移除按钮，保留 `sendTest` 函数；或改用 `agent-browser eval` 直接发 WS |
| **AI 头像 "AI" 文字**（可保留） | 仅是 UI 装饰 | 改为定制 SVG 头像；但需注意 `test_browser_e2e.sh:418` 检查 DOM 含 "AI"，**如果删除 "AI" 文字需同步更新脚本** |

### 3.4 建议新增的调试能力（替代被删除的）

| 建议新增 | 用途 | 优先级 |
|---------|------|-------|
| **`tests/ws_debug_client.py`** | 提炼自 `test_pipeline_e2e.py`，作为日常调试入口（交互式 REPL 或单条消息发送），进一步降低对 UI 的依赖 | 🔴 高 |
| **关键按钮 `data-testid`** | 给录音按钮、发送测试按钮、摄像头开关按钮加 `data-testid="mic-btn"` / `data-testid="test-btn"` / `data-testid="camera-btn"`，让 agent-browser 脚本按 testid 定位而非文案，文案改动后零成本 | 🔴 高 |
| **`tests/test_browser_e2e.sh` 改为按 testid 定位** | 配合上一项，将 `button.*录音.*[ref=...]` 改为 `[data-testid="mic-btn"]` | 🟡 中 |
| **`netlify_e2e_test.sh` 第 2 节改为 `eval` 直接发 WS** | 移除对"发送测试消息"按钮的依赖，改用 `agent-browser eval` 执行 `ws.send(JSON.stringify({type:'test',data:'...'}))` | 🟡 中 |
| **前端 dev 模式调试面板（可选）** | 用 `import.meta.env.DEV` 条件渲染一个浮动调试面板，显示 WS 消息计数、VAD 状态、AudioContext 状态等，生产环境隐藏 | 🟢 低（如果团队觉得需要） |
| **后端 `/debug/state` 端点（可选）** | 暴露 orchestrator 内部状态（`_session_active` / `_latest_image` 是否存在 / ASR client 是否连接），方便调试时 curl 查看 | 🟢 低 |

---

## 4. 给主代理的建议

1. **可以放心推进"视频通话"风格布局重设计** — 核心 pipeline 调试（`test_pipeline_e2e.py`）100% 独立于 UI，后端可独立启动验证，WS 协议开放可调试。UI 改造不会破坏后端调试能力。

2. **改造前先做一个"测试脚本同步更新" PR** — 给关键按钮加 `data-testid`，同步更新 `test_browser_e2e.sh` / `netlify_e2e_test.sh` 的按钮定位逻辑（从文案正则改为 testid）。这样后续 UI 改造时按钮文案可自由调整，测试脚本零修改。**这是一个低风险高收益的前置 PR**。

3. **保留 `handleVADStateChange` 中的 3 个副作用调用** — `audioPlayer.stop()` + `send vad_status` + `setShouldCapture(true)`。这是核心功能链路（barge-in + ASR 会话 + 摄像头截图），UI 改造时建议先抽成 `useConversationOrchestrator` hook 再加 UI 层，避免改造过程中链路断裂。

4. **"发送测试消息"按钮可以移除 UI，但保留协议** — `netlify_e2e_test.sh` 依赖它做 WS 连通性验证。建议两个方案二选一：
   - **方案 A（推荐）**：移除按钮 UI，同步将 `netlify_e2e_test.sh` 第 2 节改为 `agent-browser eval` 直接发 WS 消息（页面已建立 WS 连接，可通过 `window.__ws` 或类似方式访问，需在 `useWebSocket.ts` 中暴露 ws 实例到 window）。
   - **方案 B（保守）**：保留按钮 UI 但移到次要位置（如浮动控制条的"更多"菜单中），文案保留 "发送测试消息"。

5. **提炼 `tests/ws_debug_client.py` 作为日常调试入口** — 当前 `test_pipeline_e2e.py` 是完整测试套件（5 条语句 + 关键词匹配），日常调试时太重。建议提炼一个轻量版：单条语句发送 + 实时打印所有 ServerMessage，方便开发时快速验证后端改动。这进一步降低未来对 UI 调试的依赖。

6. **改造时注意 `test_browser_e2e.sh:418` 的 "AI" 字样检查** — 如果新布局删除了 AI 头像的 "AI" 文字（改为定制 SVG），需同步更新此检查点（改为检查 `<div data-role="assistant">` 或类似 testid）。

---

## 附录：调试方法与 UI 依赖关系图

```
┌─────────────────────────────────────────────────────────────────────┐
│                      XEngineer 调试方法全景                          │
└─────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────── 不依赖 UI（100% 独立）─────────────────┐
  │                                                                  │
  │  后端独立调试                                                     │
  │  ├── curl /health                              ← main.py:110     │
  │  ├── USE_REAL_NODES=false Stub 模式            ← config.py:24    │
  │  ├── print 启动配置 + 12 处错误 print           ← main.py + svc   │
  │  └── logging (INFO 级别)                       ← 4 处            │
  │                                                                  │
  │  WS 协议独立调试                                                  │
  │  ├── tests/test_pipeline_e2e.py (Python websockets)              │
  │  │   └── 5 条测试语句 + 完整 VAD→ASR→VLM→TTS 链路                │
  │  ├── wscat -c wss://.../ws                     ← 可即时引入      │
  │  └── curl --include --http1.1 --upgrade        ← 可即时引入      │
  │                                                                  │
  │  测试数据生成                                                     │
  │  ├── tests/prepare_test_audio.py (z-ai tts + ffmpeg)             │
  │  └── tests/fixtures/{test_audio_set.json, video-frames/}         │
  │                                                                  │
  └──────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────── 弱依赖 UI（需同步调整）─────────────────┐
  │                                                                  │
  │  tests/fixtures/mock_getusermedia.js                             │
  │  └── 需要页面有 getUserMedia({audio}) 调用入口（按钮触发）        │
  │                                                                  │
  │  agent-browser snapshot 按钮定位                                  │
  │  └── 依赖按钮文案（"录音"/"测试"/"发送"）→ 建议改 data-testid    │
  │                                                                  │
  │  console.log WS 状态日志                                          │
  │  └── test_frontend_visual.sh 搜索 "connected|连接成功"            │
  │                                                                  │
  └──────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────── 强依赖 UI（必须保留元素）──────────────┐
  │                                                                  │
  │  test_frontend_visual.sh                                          │
  │  ├── <title> 含 "XEngineer|视觉|对话|AI"                          │
  │  ├── snapshot 含 button/video/canvas                             │
  │  └── console 含 "connected|连接成功"                              │
  │                                                                  │
  │  test_browser_e2e.sh                                              │
  │  ├── DOM 含 "已连接" / "Connected"                                │
  │  ├── 录音按钮文案含 "录音" 或 "mic"/"audio"                       │
  │  ├── DOM 含 ASR 关键词（如 "你好"）                               │
  │  └── DOM 含 "AI" 字样                                            │
  │                                                                  │
  │  netlify_e2e_test.sh                                              │
  │  ├── <h1> 含 "XEngineer"                                         │
  │  ├── "发送测试消息" 按钮文案含 "测试" 或 "发送"                   │
  │  ├── DOM 含 "测试消息" / "hello from frontend"                    │
  │  ├── DOM 含 "回显" / "WS echo"                                   │
  │  ├── 录音按钮文案含 "录音"                                        │
  │  ├── DOM 含 "已连接"                                              │
  │  └── <video> transform 含 "scaleX(-1)"                           │
  │                                                                  │
  └──────────────────────────────────────────────────────────────────┘
```

---

**报告结束。** 如有疑问请参考 `frontend-structure.md`（前端代码结构摘要）和 `worklog.md`（项目历史）。
