# XEngineer 浏览器级 E2E 测试计划 v2

## 1. 背景与目标

### 1.1 现状

XEngineer 的现有端到端测试 (`tests/test_pipeline_e2e.py`) 使用 Python `websockets` 库**直接连接后端 WebSocket**，完全绕过了前端 React 应用。测试流程为：

```
Python 脚本 → WebSocket → 后端 (ASR → VLM+LLM → TTS)
```

这意味着**整个前端链路未被测试**：getUserMedia、AudioContext、ScriptProcessorNode、EnergyVAD、消息路由、UI 渲染、AudioPlayer 播放等。

### 1.2 目标

通过 `agent-browser`（headless Chromium）打开**真实的 Netlify 部署页面**，注入 `getUserMedia` Hook 替代真实麦克风，让音频数据经过完整的前端处理链路：

```
agent-browser → 真实 Netlify 页面 → getUserMedia(被Hook)
  → AudioContext(16kHz) → ScriptProcessorNode(512) → EnergyVAD
  → WebSocket → 后端 (ASR → VLM+LLM → TTS)
  → WebSocket → AudioPlaybackManager → 播放
  → UI (ChatBubble / StreamingMessage / StatusBar)
```

### 1.3 成功标准

- 测试覆盖从前端 UI 到后端处理再到前端播放的**完整闭环**
- 能验证 VAD 触发、ASR 识别、VLM 视觉理解、LLM 对话、TTS 播放
- 能验证 Barge-in（打断）场景
- 能验证多轮对话的上下文保持
- 能收集截图和结构化结果（result.json）

---

## 2. 差距分析：现有测试 vs 真人测试

### 2.1 高严重度（会导致测试结果与真人行为根本不同）

| 编号 | 差距 | 真人行为 | 现有测试 | 影响 |
|------|------|---------|---------|------|
| G1 | 音频分片尺寸/频率失真 | 1024B/32ms（512 samples × 2B Int16，ScriptProcessorNode 自动回调） | 8192B/200ms（手动分片 + asyncio.sleep） | ASR 对时序特征敏感，chunk 差 8 倍、频率差 6 倍，识别准确率可能不同 |
| G2 | 消息顺序与时机不模拟真实前端 | `vad_status(true) → image → audio×N(32ms间隔) → vad_status(false)` | `image → sleep(0.5) → vad_status(true) → sleep(2) → audio×N(200ms间隔) → sleep(1) → vad_status(false)` | 顺序反了（真人是 VAD 触发截图，测试是先截图再 VAD）；多余 sleep 可能导致 ASR 会话异常 |
| G3 | 完全没有 Barge-in 测试 | AI 播报时用户开口 → 前端 `audioPlayer.stop()` → 清空 TTS 队列 → `vad_status(true)` 通知后端 | 无此场景 | 核心交互模式未覆盖，无法发现前端打断逻辑的 bug |
| G4 | 完全绕过浏览器前端 | getUserMedia → AudioContext → ScriptProcessorNode → EnergyVAD → 消息路由 → UI 渲染 → AudioPlayer | Python websockets 直连后端 | 前端所有 bug 永远无法被发现（VAD 阈值错误、UI 状态异常、TTS 播放问题等） |

### 2.2 中严重度（影响测试覆盖面但不影响基本链路）

| 编号 | 差距 | 真人行为 | 现有测试 | 影响 |
|------|------|---------|---------|------|
| G5 | 无多轮对话上下文验证 | 同一 WebSocket 连接上连续对话，LLM 记得前文 | 每条 utterance 独立会话 (`run_single_utterance`)，不验证上下文 | 无法发现上下文丢失、会话状态污染等问题 |
| G6 | 无前端 UI 验证 | 聊天气泡、流式文字、VAD 状态指示器、连接状态 | 不检查 UI | 前端渲染 bug 不被发现 |
| G7 | 无错误恢复测试 | 网络断开重连、后端超时、ASR 返回空结果、TTS 合成失败 | 仅覆盖 happy path | 错误处理逻辑未验证 |
| G8 | 测试图片不经过真实摄像头 | getUserMedia(video) → Canvas 640×480 → JPEG quality 0.6 | PIL 生成纯色图 640×480 | 图片质量/特征差异可能影响 VLM 识别 |

### 2.3 低严重度（可改进但不紧急）

| 编号 | 差距 | 说明 |
|------|------|------|
| G9 | 缺少 echoCancellation/noiseSuppression 模拟 | 浏览器 getUserMedia 默认启用这两个约束，测试音频未经这些处理 |
| G10 | WebSocket 连接路径差异 | 测试直连 Railway，前端通过 Netlify proxy 或 VITE_WS_URL 连接 |
| G11 | 接收消息实时性差异 | 测试用 timeout 等所有消息，前端是流式处理每条消息 |
| G12 | 无性能/延迟度量 | 真人体验核心指标"开口到听到回复"延迟未测量 |

---

## 3. 技术方案：L2 agent-browser + getUserMedia Hook

### 3.1 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                    agent-browser (headless Chromium)          │
│                                                              │
│  ┌─ --init-script: mock_getusermedia.js ─────────────────┐ │
│  │  monkey-patch navigator.mediaDevices.getUserMedia      │ │
│  │  返回虚拟 MediaStream (createMediaStreamDestination)    │ │
│  └────────────────────────────────────────────────────────┘ │
│                         │                                    │
│                         ▼                                    │
│  ┌─ open: https://optalk.netlify.app ───────────────────────┐ │
│  │  React App 加载 → WebSocket 连接后端                    │ │
│  └────────────────────────────────────────────────────────┘ │
│                         │                                    │
│                         ▼                                    │
│  ┌─ eval --stdin: 注入预合成音频 (Float32 PCM base64) ────┐ │
│  │  window.__mockAudio.setAudio(float32Base64, sampleRate)│ │
│  └────────────────────────────────────────────────────────┘ │
│                         │                                    │
│                         ▼                                    │
│  ┌─ click: "开始录音" 按钮 ───────────────────────────────┐ │
│  │  前端调用 getUserMedia → 被 Hook 拦截 → 虚拟流        │ │
│  │  ScriptProcessorNode(512) 开始按 32ms 回调            │ │
│  └────────────────────────────────────────────────────────┘ │
│                         │                                    │
│                         ▼                                    │
│  ┌─ eval: startFeeding() ────────────────────────────────┐ │
│  │  ScriptProcessorNode.onaudioprocess 开始喂 Float32 数据│ │
│  │  → EnergyVAD 检测到语音 → vad_status(true) → 截图     │ │
│  │  → audio chunks 以 32ms 间隔经 WebSocket 发到后端    │ │
│  └────────────────────────────────────────────────────────┘ │
│                         │                                    │
│                         ▼                                    │
│  ┌─ wait --text: 等待 AI 回复文本 ──────────────────────┐ │
│  │  等待 ChatBubble 或 StreamingMessage 出现期望文本      │ │
│  └────────────────────────────────────────────────────────┘ │
│                         │                                    │
│                         ▼                                    │
│  ┌─ eval: stopFeeding() + 结果收集 ─────────────────────┐ │
│  │  停止喂音频 → VAD 检测静默 → vad_status(false)        │ │
│  │  等待 pipeline 完成 → 收集 result.json                │ │
│  └────────────────────────────────────────────────────────┘ │
│                         │                                    │
│                         ▼                                    │
│  ┌─ screenshot + console errors ──────────────────────────┐ │
│  │  截图保存到 tests/screenshots/                         │ │
│  │  收集 console.error 日志                               │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                     结果输出: result.json
                     {
                       "mode": "single|barge-in|multi",
                       "utterances": [
                         {
                           "text": "你好",
                           "asr_result": "...",
                           "llm_response": "...",
                           "tts_received": true,
                           "screenshot": "path.png",
                           "duration_ms": 3200
                         }
                       ],
                       "console_errors": [],
                       "status": "pass|fail|partial"
                     }
```

### 3.2 getUserMedia Hook 方案

用 `--init-script` 在页面 JS 执行前注入，monkey-patch `navigator.mediaDevices.getUserMedia`。

核心思路：不返回真实麦克风流，而是用 `AudioContext.createMediaStreamDestination()` 创建一个虚拟的 `MediaStream`，其底层是一个 `ScriptProcessorNode`，由测试脚本控制喂入预合成音频。

```javascript
// mock_getusermedia.js — 伪代码结构
(function() {
  const mockState = {
    audioQueue: [],    // Float32Array[] 待喂入的音频帧队列
    offset: 0,         // 当前帧偏移量
    feeding: false,    // 是否正在喂入
    sampleRate: 16000,
    bufferSize: 512,   // ScriptProcessorNode buffer 大小（匹配前端）
  };

  // 拦截 getUserMedia
  const originalGetUserMedia = navigator.mediaDevices.getUserMedia.bind(navigator.mediaDevices);
  navigator.mediaDevices.getUserMedia = async function(constraints) {
    if (constraints && constraints.audio) {
      // 返回虚拟 MediaStream
      const ctx = new AudioContext({ sampleRate: mockState.sampleRate });
      const dest = ctx.createMediaStreamDestination();
      const processor = ctx.createScriptProcessor(mockState.bufferSize, 0, 1);

      processor.onaudioprocess = function(e) {
        const output = e.outputBuffer.getChannelData(0);
        if (mockState.feeding && mockState.audioQueue.length > 0) {
          // 从队列取出数据填入 output
          // ...
          mockState.offset += mockState.bufferSize;
        } else {
          // 静默（零填充）
        }
      };

      processor.connect(dest);
      return { getTracks: () => [dest.stream.getAudioTracks()[0]] };
    }
    return originalGetUserMedia(constraints);
  };

  // 暴露控制接口
  window.__mockAudio = {
    setAudio: (float32Base64, sr) => { ... },
    startFeeding: () => { mockState.feeding = true; },
    stopFeeding: () => { mockState.feeding = false; },
    getState: () => ({ ...mockState }),
  };
})();
```

**关键技术点**：
- `ScriptProcessorNode(512, 0, 1)` — 0 个输入通道、1 个输出通道，我们往 outputBuffer 写数据
- 回调间隔 = 512 / 16000 = 32ms，与真实前端完全一致
- 前端代码拿到的是真实的 `MediaStream`，后续 AudioContext/ScriptProcessor/VAD 处理完全正常
- `createMediaStreamDestination` 经子代理实测验证在 headless Chromium 中可用

### 3.3 音频预合成

`tests/prepare_test_audio.py` 负责预合成测试音频：

```
z-ai tts -i "你好" -o output.wav --format wav -v tongtong
  → ffmpeg -i output.wav -ar 16000 -ac 1 -f s16le output.pcm
  → PCM bytes → base64 编码
  → 同时生成 Float32 base64（用于 ScriptProcessorNode 直接喂入）
  → 输出 JSON fixture
```

**输出格式** (`tests/fixtures/test_audio_set.json`)：
```json
[
  {
    "text": "你好，请介绍一下你自己",
    "keywords": ["你好", "介绍"],
    "pcm_base64": "AQAAAAAA...",
    "pcm_float32_base64": "AACAPwAAgD8...",
    "sample_rate": 16000,
    "duration_ms": 2100,
    "is_real": true
  }
]
```

**降级策略**：如果 `z-ai` 或 `ffmpeg` 不可用，使用正弦波生成（ASR 无法识别，仅验证连通性）。

### 3.4 测试模式

#### 单轮模式（默认）
```bash
bash tests/test_browser_e2e.sh
```
1. 加载 init-script → 打开页面
2. 注入第 1 条音频数据
3. 点击"开始录音" → startFeeding
4. 等待 VAD speaking → 等待 pipeline 完成（ASR → VLM → TTS）
5. 截图 + 收集结果 → stopFeeding
6. 输出 result.json

#### Barge-in 模式
```bash
bash tests/test_browser_e2e.sh --barge-in
```
1. 执行单轮模式的步骤 1-4
2. 等待 TTS 开始播放（检测 `tts_audio` 消息或 UI 变化）
3. 立即注入第 2 条音频 → startFeeding（模拟用户打断）
4. 验证：前端停止播放、清空队列、发送新的 vad_status(true)
5. 等待第二轮 pipeline 完成
6. 截图 + 收集结果

#### 多轮模式
```bash
bash tests/test_browser_e2e.sh --multi
```
1. 加载 init-script → 打开页面
2. 循环 3-5 轮：
   a. 注入新音频 → 点击录音（如已停止则重新点击）→ startFeeding
   b. 等待 pipeline 完成
   c. 验证 ASR 结果包含关键词
   d. 验证 LLM 回复与上下文一致
3. 每轮截图
4. 输出 result.json（含所有轮次结果）

### 3.5 agent-browser 关键能力

| 命令 | 用途 | 在本方案中的使用 |
|------|------|----------------|
| `--init-script path.js` | 页面 JS 执行前注入 | 加载 mock_getusermedia.js |
| `eval --stdin` | 通过 stdin 注入 JS | 注入大量 base64 音频数据（已验证 213KB+） |
| `snapshot -i` | 获取 DOM 快照含 interactive refs | 定位"开始录音"按钮的 ref |
| `wait --text "xxx"` | 等待文本出现 | 等待 AI 回复出现在聊天界面 |
| `screenshot path.png` | 截图保存 | 保存每轮测试的 UI 状态 |
| `click ref` | 通过 ref 点击元素 | 点击"开始录音"按钮 |
| `wait --timeout N` | 等待指定秒数 | 等待 pipeline 处理完成 |

---

## 4. 文件结构

```
tests/
├── prepare_test_audio.py          # 音频预合成工具（TTS → PCM → base64 JSON）
├── test_browser_e2e.sh            # agent-browser 编排脚本（主入口）
├── run_all_tests.sh               # 一键测试（修改：新增 --full 参数）
├── fixtures/
│   ├── .gitkeep                   # 占位文件确保目录被 git 跟踪
│   ├── mock_getusermedia.js       # getUserMedia Hook 注入脚本
│   └── test_audio_set.json        # 预合成音频数据（~1MB, 已 gitignore）
└── screenshots/                   # 测试截图输出（已 gitignore）
    └── .gitkeep
```

`.gitignore` 新增：
```
tests/fixtures/test_audio_set.json
tests/screenshots/
```

---

## 5. 实施任务分解

### Task 1: 音频预合成工具 (`prepare_test_audio.py`)

| SubTask | 描述 | 预估时间 |
|---------|------|---------|
| 1.1 | TTS 合成函数：`z-ai tts` → ffmpeg 重采样 16kHz mono PCM → raw bytes | 10min |
| 1.2 | 正弦波降级函数：生成 sine wave PCM（TTS 不可用时） | 5min |
| 1.3 | Float32 base64 编码：Int16 PCM → Float32 转换 → base64 输出 | 5min |
| 1.4 | JSON fixture 输出 + 缓存机制（避免重复合成） | 10min |
| 1.5 | CLI 参数：`--force` 强制重生成、`--output` 自定义路径、错误处理 | 5min |

### Task 2: getUserMedia Hook (`mock_getusermedia.js`)

| SubTask | 描述 | 预估时间 |
|---------|------|---------|
| 2.1 | IIFE 包裹 + getUserMedia monkey-patch | 5min |
| 2.2 | AudioContext + createMediaStreamDestination + ScriptProcessorNode(512, 0, 1) | 15min |
| 2.3 | window.__mockAudio 状态对象 + setAudio/startFeeding/stopFeeding/getState 方法 | 10min |
| 2.4 | 多次调用兼容：stopFeeding → startFeeding 循环、offset 重置 | 10min |

### Task 3: 主测试脚本 (`test_browser_e2e.sh`)

| SubTask | 描述 | 预估时间 |
|---------|------|---------|
| 3.1 | 前置条件检查：agent-browser 是否安装、fixture JSON 是否存在（不存在 SKIP） | 10min |
| 3.2 | 单轮测试流程编排（init-script → open → eval → click → wait → screenshot） | 30min |
| 3.3 | Barge-in 模式流程（等待 TTS → 喂新音频 → 验证打断） | 20min |
| 3.4 | 多轮模式流程（循环 N 轮 → 上下文验证） | 20min |
| 3.5 | 结果收集：result.json 结构化输出 + 截图 + console.errors | 15min |

### Task 4: 一键集成 (`run_all_tests.sh` 修改)

| SubTask | 描述 | 预估时间 |
|---------|------|---------|
| 4.1 | 新增 `--full` 参数解析 | 5min |
| 4.2 | `--full` 时第 6 步执行 `bash tests/test_browser_e2e.sh --multi` | 5min |
| 4.3 | 失败记 WARNING 不阻塞退出码（浏览器测试可能因环境原因失败） | 5min |

---

## 6. PR 规范

每个 Task 一个 PR，按依赖顺序合并：

| PR | 分支名 | 标题 | 文件 | 描述 |
|----|--------|------|------|------|
| A | `chore/browser-e2e-audio-prep` | `chore: 添加浏览器 E2E 测试音频预合成工具脚本` | `prepare_test_audio.py` + `fixtures/.gitkeep` + `.gitignore` | 功能描述: 预合成 TTS 语音为 base64 JSON fixture |
| B | `test/browser-e2e-getusermedia-hook` | `test: 添加浏览器 getUserMedia Hook 注入脚本` | `fixtures/mock_getusermedia.js` | 功能描述: monkey-patch getUserMedia 提供虚拟音频流 |
| C | `test/browser-e2e-main-script` | `test: 添加浏览器级 E2E 主测试脚本` | `test_browser_e2e.sh` + `screenshots/.gitkeep` | 功能描述: agent-browser 编排单轮/barge-in/多轮测试 |
| D | `chore/browser-e2e-integration` | `chore: 更新一键测试脚本，集成浏览器 E2E` | `run_all_tests.sh` | 功能描述: --full 参数集成浏览器测试 |

**合并顺序**: A → B → C → D（C 依赖 A 和 B，D 依赖 C）

每个 PR 描述须包含：
```
## 功能描述
...

## 实现思路
...

## 测试方式
...
```

---

## 7. 验证清单

### 静态检查（代码提交后可立即验证）

- [ ] `prepare_test_audio.py` 语法正确（`python3 -m py_compile`）
- [ ] `mock_getusermedia.js` 语法正确（`node --check`）
- [ ] `test_browser_e2e.sh` 可执行（`bash -n`）
- [ ] `test_audio_set.json` 可由 prepare_test_audio.py 生成
- [ ] `run_all_tests.sh --full` 参数解析正确
- [ ] `.gitignore` 正确忽略 fixture JSON 和 screenshots

### 运行时检查（需要实际运行浏览器测试）

- [ ] init-script 成功 Hook 浏览器 getUserMedia
- [ ] VAD 在喂入音频后被触发（speaking 状态）
- [ ] 完整对话截图正确（ChatBubble 显示用户文本和 AI 回复）
- [ ] Barge-in 模式：AI 播放被正确打断
- [ ] result.json 结构完整、status 字段正确

---

## 8. 风险与缓解

| 风险 | 严重度 | 概率 | 缓解措施 |
|------|--------|------|---------|
| agent-browser headless 模式下 getUserMedia 不可用 | 高 | 确定 | 通过 --init-script hook 解决（核心方案） |
| `createMediaStreamDestination` 在 headless 中不可用 | 高 | 低 | 已由子代理实测验证可用 |
| TTS 合成依赖 z-ai CLI | 中 | 低 | 正弦波降级方案，is_real 标记区分 |
| 音频注入时序精度不足 | 中 | 低 | ScriptProcessorNode 按 bufferSize=512 自动 32ms 回调，与真实前端一致 |
| eval --stdin 数据量限制 | 中 | 低 | 已验证可注入 213KB+ 数据；可拆分为多次 eval |
| Railway 后端缺少 .env（火山引擎 token） | 高 | 中 | Pipeline E2E 跳过；浏览器测试同样依赖后端 ASR 可用 |
| Netlify 页面加载缓慢或超时 | 中 | 中 | agent-browser wait --timeout 调整；重试机制 |
| 多轮测试状态污染 | 低 | 中 | 每轮之间 stopFeeding + 等待 VAD silent |

---

## 附录 A: L1 vs L2 方案对比

| 维度 | L1: 改进 Python 测试 | L2: agent-browser + Hook |
|------|---------------------|--------------------------|
| 改动范围 | 修改 `test_pipeline_e2e.py` 一个文件 | 新增 3-4 个文件 |
| G1 音频分片 | ✅ 可修复（改 chunk 大小/间隔） | ✅ 自动一致（ScriptProcessorNode 32ms） |
| G2 消息顺序 | ✅ 可修复（调整发送顺序） | ✅ 自动正确（前端原生行为） |
| G3 Barge-in | ⚠️ 可模拟（发送打断消息） | ✅ 真实模拟（前端 audioPlayer.stop） |
| G4 前端链路 | ❌ 仍然绕过 | ✅ 完整经过前端 |
| G5 多轮上下文 | ✅ 可修复（不改连接） | ✅ 天然支持 |
| G6 UI 验证 | ❌ 无法验证 | ✅ 可截图验证 |
| 开发成本 | 低 | 中 |
| 维护成本 | 中（需跟踪前端消息格式变化） | 低（测试的是真实前端） |
| **推荐** | 快速修复 + L2 的补充 | **主要方案** |

## 附录 B: 前端关键代码参考

| 文件 | 作用 | 与测试相关 |
|------|------|-----------|
| `xengineer-frontend/src/hooks/useVAD.ts` | getUserMedia + AudioContext + ScriptProcessorNode(512,1,1) + VAD | Hook 要兼容此文件的 getUserMedia 调用 |
| `xengineer-frontend/src/lib/vad.ts` | EnergyVAD — RMS 能量阈值 VAD | 音频需足够"响亮"才能触发 speaking |
| `xengineer-frontend/src/App.tsx` | 消息路由 / barge-in 逻辑 / 聊天状态 | 验证 UI 状态变化的依据 |
| `xengineer-frontend/src/components/AudioPlayer.tsx` | AudioPlaybackManager 单例 | Barge-in 测试需验证 stop() 行为 |
| `xengineer-frontend/src/hooks/useWebSocket.ts` | WebSocket 连接管理 | 不需要 Hook（测试用的是真实连接） |
| `xengineer-frontend/src/lib/protocol.ts` | 消息类型定义 | 测试结果验证的参考 |
