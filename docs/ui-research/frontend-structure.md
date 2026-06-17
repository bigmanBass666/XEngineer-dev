# XEngineer 前端代码结构摘要

> 生成者: subagent-D (Task ID 10) | 分支: `feat/improve-ui` (基于 main `5f06fcb`)
> 范围: `xengineer-frontend/src/` 全部源码 + 配置文件，用于主代理编写 UI 改造计划

---

## 1. 技术栈

| 维度 | 选择 | 版本 |
|------|------|------|
| 构建工具 | Vite | ^6.0.3 |
| 框架 | React + ReactDOM | ^18.3.1 |
| 语言 | TypeScript (strict) | ^5.6.3 |
| JSX 运行时 | react-jsx (无需 import React) | — |
| 样式方案 | Tailwind CSS (utility-first) + 原生 CSS | ^3.4.16 |
| PostCSS | autoprefixer + tailwindcss | ^8.4.49 |
| 模块 | ESM (`"type": "module"`) | — |
| 路由 | **无** (单页应用，无 react-router) | — |
| 状态管理 | **无第三方库** (纯 React `useState` + `useRef`，AppState 全在 `App.tsx`) | — |
| HTTP 库 | **无** (仅 WebSocket) | — |
| 部署 | Netlify (`netlify.toml` 配置 SPA fallback) | — |

**关键依赖（devDeps 仅 7 个，零业务三方库）**:
- `react`, `react-dom` — 唯一运行时依赖
- `@vitejs/plugin-react` — Vite React 插件
- `tailwindcss`, `postcss`, `autoprefixer` — 样式工具链
- `typescript`, `@types/react`, `@types/react-dom` — 类型

> **观察**: 依赖极简（package.json 仅 1 个运行时 dep + 7 个 devDep），没有任何动画库、图标库、状态管理库、UI 组件库。所有 SVG 图标都是内联手写，所有动画用 Tailwind 的 `animate-pulse / animate-bounce / animate-spin`。改造时引入新库的阻力很小。

---

## 2. 目录结构

```
xengineer-frontend/
├── index.html                  # 入口 HTML (lang=zh-CN, body 直接用 Tailwind bg-gray-900)
├── netlify.toml                # Netlify 部署配置 (SPA fallback)
├── package.json                # 依赖 + scripts (dev/build/preview)
├── tsconfig.json               # TS strict, target ES2020, jsx: react-jsx
├── vite.config.ts              # Vite 配置: port 5173, host true, envPrefix VITE_
├── tailwind.config.js          # Tailwind 配置 (theme.extend 为空 — 完全使用默认调色板)
├── postcss.config.js           # PostCSS: tailwindcss + autoprefixer
├── agent-ctx/
│   └── T12-frontend-developer.md   # 历史任务记录 (聊天气泡 + 流式回复实现)
└── src/
    ├── main.tsx                # React 入口, StrictMode, createRoot
    ├── App.tsx                 # 唯一页面 (218 行, 顶部 header + 左右双栏 + StatusBar)
    ├── index.css               # 全局样式 (12 行, Tailwind 指令 + body 基础样式)
    ├── vite-env.d.ts           # Vite 类型声明 (空)
    ├── components/             # 6 个业务组件
    │   ├── Camera.tsx          # 摄像头预览 + 截图
    │   ├── AudioRecorder.tsx   # 录音按钮 + VAD 状态指示
    │   ├── AudioPlayer.tsx     # TTS 音频播放 (单例 AudioPlaybackManager + 波形可视化)
    │   ├── StreamingMessage.tsx # AI 流式回复气泡 (脉冲光标)
    │   ├── ChatBubble.tsx      # 用户/AI/系统消息气泡
    │   └── StatusBar.tsx       # 底部状态栏 (WS 状态 + VAD 状态 + AI 处理中 + 播放指示)
    ├── hooks/                  # 3 个自定义 Hook
    │   ├── useWebSocket.ts     # WS 连接 + 重连 + 消息分发
    │   ├── useCamera.ts        # getUserMedia + Canvas 截图 + 画面变化检测
    │   └── useVAD.ts           # getUserMedia + AudioContext + 能量 VAD + PCM base64 输出
    └── lib/                    # 2 个工具模块
        ├── protocol.ts         # 消息类型定义 (ClientMessage / ServerMessage / ChatMessage / 状态)
        └── vad.ts              # EnergyVAD 类 (RMS 能量阈值 + 帧计数去抖)
```

**文件总数**: 14 个 TS/TSX/CSS 源文件 + 7 个配置文件
**代码总行数**: 1060 行（src/ 内）
- App.tsx 218 行（最大）
- AudioPlayer.tsx 154 行
- useVAD.ts 122 行
- useCamera.ts 101 行
- useWebSocket.ts 88 行
- 其余每个文件 < 90 行

---

## 3. 组件清单

| 文件 | 行数 | 主要导出 | 职责 |
|------|------|----------|------|
| `src/main.tsx` | 9 | (default mount) | ReactDOM.createRoot + StrictMode + 引入 index.css |
| `src/App.tsx` | 218 | `App` (default) | 唯一页面：组装 header + 左栏(Camera+录音+测试按钮) + 右栏(对话流) + StatusBar；持有全部状态 (messages / currentAIResponse / isAIProcessing / vadStatus / shouldCapture)；处理 7 种 ServerMessage |
| `src/components/Camera.tsx` | 86 | `Camera` | 4:3 视频预览 + 隐藏 Canvas；VAD 触发时闪光特效；开启/关闭按钮；镜像翻转 `scaleX(-1)` |
| `src/components/AudioRecorder.tsx` | 48 | `AudioRecorder` | "开始/停止录音" 按钮 + VAD 状态点 (emerald 脉冲) + 错误展示 |
| `src/components/AudioPlayer.tsx` | 154 | `AudioPlayer` (组件) + `audioPlayer` (单例) | `AudioPlaybackManager` 类管理 24kHz AudioContext + base64 mp3 解码 + 播放队列 + Barge-in `stop()`；React 组件显示 4 根波形动画 |
| `src/components/StreamingMessage.tsx` | 18 | `StreamingMessage` | AI 流式回复气泡 + 蓝色脉冲光标 |
| `src/components/ChatBubble.tsx` | 39 | `ChatBubble` | 三种消息样式：user (蓝右)、assistant (灰左)、system (居中卡片) |
| `src/components/StatusBar.tsx` | 58 | `StatusBar` | 底部状态栏：WS 连接状态点 + VAD 状态点 + AI 处理中 spinner + 音频播放指示位 + 版本号 |
| `src/hooks/useWebSocket.ts` | 88 | `useWebSocket` | WS 连接 (`wss://xengineer-dev-production.up.railway.app/ws`) + 3s 自动重连 + `onMessage` 订阅/退订 + `send` |
| `src/hooks/useCamera.ts` | 101 | `useCamera` | `getUserMedia({video})` + Canvas 截图 (JPEG q=0.6, 640×480) + 简单 hash 去重 + `start/stop/captureAndSend` |
| `src/hooks/useVAD.ts` | 122 | `useVAD` | `getUserMedia({audio 16kHz})` + AudioContext + ScriptProcessorNode(512) + EnergyVAD + Float32→Int16→base64 仅在 speaking 状态发送 |
| `src/lib/vad.ts` | 78 | `EnergyVAD` (class), `VADState`, `VADResult`, `VADController` | RMS 能量阈值 (默认 0.02) + 帧计数去抖 (speaking≥3 帧 / silence≥15 帧 ≈ 60ms/300ms) |
| `src/lib/protocol.ts` | 29 | `ClientMessage`, `ServerMessage`, `ChatMessage`, `ConnectionStatus`, `VADStatus` | WebSocket 消息协议类型 (4 种 Client / 7 种 Server) |
| `src/index.css` | 12 | (全局) | `@tailwind base/components/utilities` + body 基础样式 |
| `src/vite-env.d.ts` | 0 | (vite/client 引用) | 空 |

> **观察**: 没有任何 `pages/` `views/` `store/` `context/` `services/` `utils/` 目录。整个应用就是一个 `App.tsx` 顶层组件 + 6 个子组件 + 3 个 Hook + 2 个 lib 文件，结构极扁平。

---

## 4. 样式系统现状

### 4.1 全局样式

**文件**: `src/index.css` (12 行)

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  margin: 0;
  padding: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background-color: #111827;   /* gray-900 */
  color: #f9fafb;              /* gray-50 */
  overflow: hidden;
  height: 100vh;
}
```

**CSS 变量 (design tokens)**: **完全没有定义**。零 `:root` 变量，零 `@theme`，零自定义颜色 token。所有颜色直接硬编码 Tailwind 调色板（`bg-gray-900`, `bg-blue-600`, `bg-emerald-600`, `bg-red-600` 等），或少数 hex 字面量（仅 body 的 `#111827` / `#f9fafb`）。

**Tailwind 配置** (`tailwind.config.js`): `theme.extend` 为空对象。完全使用 Tailwind 默认调色板，没有扩展任何自定义颜色、字体、间距、圆角、阴影、动画。

**字体选择**: 系统字体栈 `-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif` —— 即每个平台默认无衬线字体（macOS 上是 San Francisco，Windows 上是 Segoe UI）。无任何 Google Fonts、无中文字体声明（中文会 fallback 到系统默认中文字体）。

### 4.2 组件样式方式

**所有组件统一使用 Tailwind utility classes**（无 CSS Modules、无 styled-components、无 CSS-in-JS、无内联 style 对象，除少数动画延迟）：

| 组件 | 样式方式 | 关键 class |
|------|----------|------------|
| `App.tsx` | Tailwind className | `h-screen flex flex-col bg-gray-900`, header `h-12 bg-gray-800 border-b border-gray-700`, 左右栏 `w-1/2`, 边框 `border-r border-gray-700` |
| `Camera.tsx` | Tailwind + 1 处内联 style | `aspect-[4/3] bg-gray-800 rounded-lg`, video `style={{ transform: 'scaleX(-1)' }}` (镜像) |
| `AudioRecorder.tsx` | Tailwind 动态拼接 | 按钮颜色根据 `isActive` 切换 `bg-red-600`/`bg-emerald-600`，状态点 `animate-pulse` |
| `AudioPlayer.tsx` | Tailwind + 内联 style | 4 根波形条 `style={{ height, animationDelay }}` |
| `StreamingMessage.tsx` | Tailwind | AI 头像 `bg-blue-600 rounded-full`, 气泡 `rounded-2xl rounded-bl-sm bg-gray-700`, 光标 `bg-blue-400 animate-pulse` |
| `ChatBubble.tsx` | Tailwind 动态拼接 | user 气泡 `bg-blue-600 rounded-br-sm`, AI 气泡 `bg-gray-700 rounded-bl-sm`, system 居中卡片 `bg-gray-800 border border-gray-700` |
| `StatusBar.tsx` | Tailwind | footer `h-10 bg-gray-800 border-t`, 状态点用 `Record<ConnectionStatus, string>` 映射颜色 |

### 4.3 设计语言观察

- **主色调**: **蓝色 (blue-600 `#2563eb`)** — 出现在 logo 方块、用户气泡、AI 头像、按钮、流式光标、播放波形。唯一强调色。
- **辅助色**:
  - 翡翠绿 (emerald-600/400) — 录音按钮 + VAD 正在说话状态
  - 红色 (red-600) — 停止录音按钮 + 错误提示
  - 黄色 (yellow-500) — WS connecting 状态
  - 灰色梯度 (gray-900/800/700/600/500/400/300/100) — 背景、边框、文字、按钮 hover
- **字体风格**: 系统默认无衬线 + 中文 fallback。**没有展示字体 (display font)**，标题与正文同字体。字号梯度靠 Tailwind `text-xs/sm/base`。
- **间距风格**: 紧凑型。`p-4` (16px) / `p-3` (12px) / `gap-3` (12px) / `gap-2` (8px) 为主。header h-12, footer h-10。
- **圆角风格**: 中等圆角混用。按钮 `rounded-lg` (8px)，气泡 `rounded-2xl` (16px) 单角 `rounded-bl-sm/br-sm` 制造对话方向感，头像 `rounded-full`，logo 方块 `rounded-lg`。
- **动效使用**: 极简，仅 4 处。
  - `animate-pulse` — VAD speaking 状态点、Camera 截图闪光、StreamingMessage 光标
  - `animate-bounce` — AudioPlayer 4 根波形条 (错开 0/150/300/450ms)
  - `animate-spin` — StatusBar AI 处理中 spinner
  - `transition-colors` — 所有按钮 hover 颜色过渡
  - `scrollIntoView({ behavior: 'smooth' })` — 对话流自动滚动
- **整体观感**: 典型的"开发者工具默认暗色主题" —— gray-900 背景 + blue-600 强调 + Tailwind 默认调色板。**视觉识别度低**，与任何 Vite + Tailwind 模板的初始外观几乎无法区分。**没有任何 signature 元素**：无 logo 字体、无品牌色组合、无特色动效、无装饰图形。

---

## 5. 用户交互流程

应用是单页双栏布局，用户进入后看到的是：

```
┌────────────────────────────────────────────────────────────┐
│ [logo] XEngineer - AI 视觉对话助手              (header)   │
├──────────────────────────┬─────────────────────────────────┤
│                          │                                 │
│      [摄像头预览]         │     💬 暂无对话                  │
│      (4:3 镜像)          │     (灰色占位 + 提示文案)        │
│                          │                                 │
│   [发送测试消息]          │                                 │
│                          │                                 │
│   [开始录音] ● 静音       │                                 │
│                          │                                 │
├──────────────────────────┴─────────────────────────────────┤
│ ● 已连接  ● 静音            AI 处理中  [播放指示]  v0.1.0   │
└────────────────────────────────────────────────────────────┘
```

**主要交互流程**:

1. **页面加载** → `useWebSocket` 立即连接 `wss://...railway.app/ws`，StatusBar 显示 "连接中..." → "已连接"
2. **点击"开启摄像头"** → `useCamera.start()` 请求 `getUserMedia({video})` → 视频流渲染到 `<video>`，"关闭"按钮出现
3. **点击"开始录音"** → `useVAD.start()` 请求 `getUserMedia({audio})` → AudioContext 16kHz + ScriptProcessorNode(512) 持续采样
4. **用户说话** → EnergyVAD 检测到 RMS 超过 0.02 持续 ≥3 帧 → 状态切换为 `speaking`：
   - AudioRecorder 状态点变绿 + 脉冲
   - App 触发 `audioPlayer.stop()` (**Barge-in** 打断 AI 播放)
   - App 发送 `{type:'vad_status', speaking:true}` 给后端
   - App 设置 `shouldCapture=true` 持续 100ms → Camera 截图 + 发送 `{type:'image', data}`
   - useVAD 持续将 PCM Int16 base64 通过 `{type:'audio', data}` 发送给后端
5. **用户停止说话** → RMS 低于 0.01 持续 ≥15 帧 → 状态切回 `silent`，发送 `vad_status false`
6. **后端处理** → 后端 ASR → LLM → TTS 流式返回：
   - `asr_final` → 在对话区追加 user 气泡
   - `llm_chunk` → 累积到 `currentAIResponse`，StreamingMessage 实时显示 + 蓝色脉冲光标
   - `tts_audio` → base64 mp3 入队 AudioPlayer，自动顺序播放 + 显示 4 根波形
   - `tts_end` → 流式内容固化为 assistant 气泡，AI 处理中状态结束
7. **点击"发送测试消息"** → 本地追加 user 气泡 "测试消息: hello from frontend" + 发送 `{type:'test', data:'hello from frontend'}`，后端回 `{type:'status', message:'WS echo: hello from frontend'}` → 显示 system 气泡

**关键状态切换**:
- 连接状态: `disconnected` → `connecting` → `connected` (失败时 `error` + 3s 重连)
- VAD 状态: `silent` ⇄ `speaking`
- AI 处理状态: `idle` → `processing` (收到首个 llm_chunk) → `idle` (收到 tts_end 或 error)
- 录音状态: `inactive` ⇄ `active`

---

## 6. 与外部的交互

### 6.1 WebSocket

- **URL**: `import.meta.env.VITE_WS_URL || 'wss://xengineer-dev-production.up.railway.app/ws'`
  - 默认指向 Railway 生产后端
  - 可通过 `.env` 的 `VITE_WS_URL` 覆盖（如本地开发指向 `ws://localhost:8000/ws`）
- **协议** (定义在 `src/lib/protocol.ts`):
  - **Client → Server** (`ClientMessage`): 4 种
    - `{type:'audio', data: base64-pcm-int16}` — 用户说话时的 PCM 音频
    - `{type:'image', data: base64-jpeg}` — VAD 触发时的摄像头截图
    - `{type:'vad_status', speaking: boolean}` — VAD 状态变化（**后端依赖此消息启动/停止 ASR 会话**）
    - `{type:'test', data: string}` — 测试消息
  - **Server → Client** (`ServerMessage`): 7 种
    - `asr_interim` / `asr_final` — ASR 识别结果
    - `llm_chunk` — LLM 流式回复片段
    - `tts_audio` — base64 mp3 音频片段
    - `tts_end` — TTS 流结束信号
    - `status` / `error` — 状态/错误
- **重连机制**: `ws.onclose` 触发后 3 秒自动重连；构造失败也 3 秒重连。用 `connectRef` 避免闭包过期。
- **消息分发**: `onMessage(handler)` 返回 unsubscribe 函数，多个 handler 通过 Set 管理。
- **发送保护**: `send` 检查 `readyState === OPEN`，否则 `console.warn`（**注意：未连接时消息直接丢弃，无队列缓冲**）。

### 6.2 HTTP API

- **无**。前端不发起任何 fetch/XHR，所有数据走 WebSocket。
- 部署到 Netlify 时通过 `netlify.toml` 的 `[[redirects]]` 把所有路径 fallback 到 `/index.html`（SPA 标准）。

### 6.3 浏览器 API 使用

| API | 用于 | 文件 | 备注 |
|-----|------|------|------|
| `WebSocket` | 实时双向通信 | `useWebSocket.ts` | 全局单连接 |
| `navigator.mediaDevices.getUserMedia({video})` | 摄像头预览 + 截图 | `useCamera.ts` | 640×480, facingMode 'user'；用户点击"开启摄像头"时调用 |
| `navigator.mediaDevices.getUserMedia({audio})` | 麦克风采集 | `useVAD.ts` | 16kHz, 单声道, echoCancellation, noiseSuppression；用户点击"开始录音"时调用 |
| `AudioContext` (24kHz) | TTS mp3 解码 + 播放 | `AudioPlayer.tsx` | 全局单例 `audioPlayer`；构造时立即 `new AudioContext()`；`enqueue` 时若 suspended 则 `resume()` |
| `AudioContext` (16kHz) | 麦克风采样 | `useVAD.ts` | 录音时创建，停止时 `close()` |
| `ScriptProcessorNode(512, 1, 1)` | 实时音频帧处理 | `useVAD.ts` | **已废弃 API**，未来应迁移到 AudioWorklet，但当前能用 |
| `AudioContext.decodeAudioData` | base64 mp3 → AudioBuffer | `AudioPlayer.tsx` | 异步解码 |
| `AudioBufferSourceNode` | 单次播放 | `AudioPlayer.tsx` | `source.start()` + `onended` 触发下一段 |
| `HTMLCanvasElement.toDataURL('image/jpeg', 0.6)` | 摄像头截图 → base64 | `useCamera.ts` | JPEG q=0.6 ≈ 30-50KB |
| `canvas.getContext('2d').drawImage` | video → canvas | `useCamera.ts` | — |
| `crypto.randomUUID()` | 消息 ID 生成 | `App.tsx` | 现代浏览器原生 |
| `atob` / `btoa` | base64 编解码 | `AudioPlayer.tsx`, `useVAD.ts` | — |
| `scrollIntoView({behavior:'smooth'})` | 对话流自动滚到底 | `App.tsx` | — |

### 6.4 权限流程注意点（改造时务必保留）

1. **getUserMedia 必须由用户手势触发** — 浏览器自动播放策略要求。当前流程是用户点击"开启摄像头"和"开始录音"按钮，**不能改成页面加载即自动开启**。
2. **AudioContext 必须由用户手势 resume** — `AudioPlaybackManager` 在 `enqueue` 时会检查 suspended 并 resume，但如果用户从未点击任何按钮，AudioContext 创建后可能保持 suspended 状态导致 TTS 无声。当前依赖"用户先点录音按钮"来间接解锁。
3. **WS 未连接时消息丢弃** — `useWebSocket.send` 在非 OPEN 状态只 warn 不缓存。如果用户在 WS 重连期间说话，音频/图片数据会丢失。改造时若要加历史消息或重发逻辑需注意这点。
4. **Barge-in 依赖 VAD → audioPlayer.stop()** — 用户说话时立即打断 AI TTS 播放。这是核心交互，改造时不能破坏 `handleVADStateChange` 中的 `audioPlayer.stop()` 调用。

---

## 7. UI 改造的入手点建议（给主代理参考）

### 7.1 当前 UI 的明显问题

1. **零设计 tokens** — 没有任何 CSS 变量或 Tailwind theme.extend，所有颜色硬编码。改造时无法集中改色，必须逐文件替换。**建议第一步先建立 design tokens 层**（在 `tailwind.config.js` 的 `theme.extend` 或 `:root` CSS 变量），把 blue-600 / gray-900/800/700 / emerald / red 提炼成 `brand-primary / surface-1/2/3 / accent-success / accent-danger` 等语义 token。
2. **零视觉识别度** — 当前界面与任何 Vite + Tailwind 模板无法区分。没有展示字体、没有 logo 字体、没有特色装饰图形、没有品牌色组合。需要至少一个"signature 元素"（如：定制 logo 字体、独特配色、特色背景纹理、动效签名）。
3. **header 过于单薄** — 仅 48px 高，左侧只有一个 28px 蓝色方块 + 16px SVG + 标题文字。**这是做 signature 元素的最佳位置**（放大 logo、加副标题、加状态指示器、加品牌字体）。
4. **空状态太朴素** — 对话区空状态只有一个灰色对话框 SVG + "暂无对话" + 提示文字。**这是首屏第一印象**，应该做成有冲击力的 hero（如：渐变背景 + 大字标题 + 引导动画 + 能力卡片）。
5. **StatusBar 信息密度低** — 仅一行小字 + 几个状态点。可以扩展成更丰富的状态面板（如：延迟显示、音频码率、模型名称、会话时长）。
6. **左栏布局拥挤** — 摄像头预览 + 测试按钮 + 录音按钮垂直堆叠，视觉重心不明确。摄像头是核心信号源，应该更突出，测试按钮可以移到次要位置或删除。
7. **系统中文显示无字体优化** — 当前依赖平台默认中文字体，在 macOS 上是 PingFang，Windows 上是微软雅黑，跨平台不一致。建议引入思源黑体 / 阿里巴巴普惠体 / 霞鹜文楷等开源中文字体（或至少声明 `font-family` 中文 fallback 链）。
8. **没有暗/亮主题切换** — 当前硬编码暗色。如果改造要支持亮色，所有 `bg-gray-900` 都需要替换为语义 token。

### 7.2 适合做"signature 元素"的位置

1. **Header logo 区** — 当前是 28px 蓝方块 + 通用 SVG 摄像机图标。**最强候选**：可换成定制字体 logo（如 "XENGINEER" 间距拉宽 + 一个独特的几何图形）、或动态 logo（呼吸光效、随 WS 状态变色）。
2. **空状态 hero** — 对话区未开始时的占位。**第二强候选**：可做成大字标题 "开始和 AI 视觉对话" + 副标题 + 引导箭头指向左侧录音按钮 + 背景粒子或网格动效。
3. **Camera 边框** — 4:3 视频预览周围。可加扫描线动效（科幻感）、四角取景框装饰、AI 识别中边框发光等。
4. **VAD 状态可视化** — 当前只是一个小绿点 + "正在说话" 文字。可做成环形音量电平表、波形可视化、声纹粒子等。
5. **AI 头像** — 当前是蓝底 "AI" 两字。可换成定制 SVG 头像、根据 AI 状态变化的图形（思考中/说话中/空闲）。
6. **背景层** — 当前是纯 `bg-gray-900`。可加微妙的网格、噪点、渐变光晕等增加层次感。

### 7.3 改造时需要特别注意的点

1. **WebSocket 状态依赖** — 大量 UI 元素颜色/文案依赖 `connectionStatus`（StatusBar 状态点、可能影响发送按钮 disabled 状态）。改造时若引入新组件，需要从 `useWebSocket()` 取 `status` 透传，不要破坏当前链路。
2. **getUserMedia 权限流程不可自动触发** — 任何"页面加载即开启摄像头/麦克风"的改造都会被浏览器拦截。必须保留用户手势触发点（当前是按钮 click）。如果改造成语音热词唤醒等，仍需首次用户交互解锁权限。
3. **AudioContext 24kHz 单例不能复制** — `audioPlayer` 是模块级单例，整个应用共享一个 24kHz AudioContext（匹配后端 TTS 输出采样率）。改造时若要新增音频可视化组件，应该订阅 `audioPlayer.setCallback` 而不是新建 AudioContext。
4. **VAD 触发链路不可断** — `useVAD.onStateChange` → `App.handleVADStateChange` → `audioPlayer.stop()` + `send({vad_status})` + `setShouldCapture(true)` → `Camera.useEffect` → `captureAndSend` → `send({image})`。这条链路涉及 barge-in、后端 ASR 会话启停、摄像头截图三件事，**任何一环改造失败都会导致功能崩坏**。改造时建议先把这条链路抽成一个独立 hook（如 `useConversationOrchestrator`），再加 UI 层。
5. **ScriptProcessorNode 已废弃** — `useVAD` 用的 `createScriptProcessor` 在主线程跑音频处理，性能差且已被 W3C 标记废弃。如果改造涉及音频可视化或性能优化，可考虑迁移到 AudioWorklet（但这是后端逻辑改动，不是纯 UI 改造，需主代理评估优先级）。
6. **`dist/` 被 git 追踪** — worklog Task 1+2+3 提到 `xengineer-frontend/dist/` 既被 git 追踪又被 .gitignore 忽略。每次 `npm run build` 都会污染 working tree。改造时跑 build 验证后记得 `git checkout -- xengineer-frontend/dist/`，或主代理先把 dist/ 加入 .gitignore。
7. **当前依赖零三方 UI/动画库** — 引入 framer-motion / @radix-ui / lucide-react / shadcn 等都很轻量（package.json 仅 1 个运行时 dep），改造时阻力极小。建议至少引入一个图标库（lucide-react）替换内联 SVG，一个动画库（framer-motion）做 signature 动效。

### 7.4 推荐的改造顺序（给主代理排期参考）

1. **基础层** — 建 design tokens (`tailwind.config.js` theme.extend + `:root` CSS 变量) + 引入中文字体 + 引入图标库
2. **signature 元素** — Header logo 重设计 + 空状态 hero
3. **布局层** — 左右栏比例 + Camera 边框装饰 + 录音按钮重设计
4. **细节层** — ChatBubble / StreamingMessage / StatusBar 视觉升级
5. **动效层** — VAD 音量可视化 + AI 头像状态动效 + 页面过渡
6. **验证** — `npm run build` 通过 + agent-browser 截图对比 + WebSocket/VAD/getUserMedia 功能不回归

---

## 附录：关键代码片段索引

- WebSocket URL 与重连: `src/hooks/useWebSocket.ts:4, 22, 35`
- VAD 触发链路: `src/App.tsx:115-128`
- Barge-in 实现: `src/components/AudioPlayer.tsx:88-100` + `src/App.tsx:119`
- 7 种 ServerMessage 处理: `src/App.tsx:35-87`
- 消息协议定义: `src/lib/protocol.ts:1-30`
- AudioContext 24kHz 单例: `src/components/AudioPlayer.tsx:28, 108`
- 摄像头截图 JPEG q=0.6: `src/hooks/useCamera.ts:30`
- VAD 能量阈值 0.02 / 帧计数 3/15: `src/lib/vad.ts:27-39, 52-66`
