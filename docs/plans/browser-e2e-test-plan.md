# 浏览器级端到端测试计划 — 逼近真人体验

> 状态：**待审核**
> 创建：2026-06-15
> 作者：AI Agent
> 目标：在 Netlify 线上前端中模拟真人用户交互，验证完整链路

---

## 一、背景

### 1.1 现有测试与真人体验的差距

已完成的测试体系（Phase 0-3）:

| 阶段 | 测试 | 已验证 |
|------|------|--------|
| Phase 0 | Git/PR 规范 | PR #1-#18 |
| Phase 1 | 图片链路修复 | VLM 多模态对话 |
| Phase 2 | WS Pipeline E2E (test_pipeline_e2e.py) | 5/5 全绿 |
| Phase 3 | agent-browser 前端视觉验证 | 页面加载 + WS 连接 |

但 `test_pipeline_e2e.py` 是一个**裸 WebSocket 协议测试**，直接构造 JSON 消息发送给后端，绕过了整个前端。它无法验证以下真实用户场景：

### 1.2 12 项差距清单

#### 严重差距 — 直接影响功能正确性

| # | 差距 | E2E 测试 | 真人前端 | 影响 |
|---|------|---------|---------|------|
| G1 | **音频分片大小/速率** | 8192 bytes/200ms 大块，最多 20 片 | 1024 bytes/32ms 实时流，不限数量 | 后端 ASR 收到的音频模式完全不同，缓冲和识别行为可能不同 |
| G2 | **消息发送顺序** | image → wait 0.5s → vad_status(speaking) → wait 2s → audio | vad_status(speaking) + image 同时发出 → audio 立即跟随 | 顺序不同可能导致后端竞态或不同分支逻辑 |
| G3 | **Barge-in（打断）** | 完全没有测试 | 用户说话立即停止 TTS 播放，发 vad_status(speaking: true) | 打断是核心交互，后端必须正确处理中途中断 |

#### 中等差距 — 影响体验质量

| # | 差距 | 说明 |
|---|------|------|
| G4 | 前端只发语音帧，不发静音帧 | 测试全发，真实情况只有 VAD 检测到语音时才发 |
| G5 | 摄像头事件驱动 + 帧去重 | 测试每轮都发图，真实前端基于 VAD 事件 + 哈希去重 |
| G6 | 无断线重连测试 | 前端 3s 自动重连，测试连接一次不测试恢复 |
| G7 | 浏览器自动播放策略 | AudioContext suspended 状态处理，测试无法触发 |

#### 轻微差距

| # | 差距 | 说明 |
|---|------|------|
| G8 | asr_interim 前端直接丢弃 | 测试收集但前端 `break` 不处理 |
| G9 | ScriptProcessorNode 废弃 API | 未来浏览器兼容性风险 |
| G10 | 麦克风音频连接到扬声器 | 有回声风险 |
| G11 | isAIProcessing 闭包 bug | 快速状态切换时潜在问题 |

### 1.3 本计划目标

创建一个**浏览器级 E2E 测试**，通过 `agent-browser` 操作真实 Netlify 页面，同时用 JS 注入 hook 替换麦克风音频为 TTS 合成语音，使前端代码按真实路径运行：

- 前端 VAD 真实运行（32ms 分片、能量检测）
- 消息发送顺序完全真实（vad_status → image → audio chunks）
- AudioPlayer 真实解码播放 TTS 音频
- Barge-in 可以测试（AI 回复时注入新语音触发打断）
- UI 状态变化可通过截图 + DOM 检查验证

---

## 二、技术方案 — L2: agent-browser + JS 音频 Hook

### 2.1 方案选型

| 方案 | 覆盖度 | 可行性 | 复杂度 | 选择 |
|------|--------|--------|--------|------|
| L1: agent-browser 操作 UI + 后台 WS 发音频 | 70% | 高 | 低 | 作为 fallback |
| **L2: agent-browser + JS 注入 Hook** | **85%** | **高** | **中** | **主方案** |
| L3: Chromium --use-file-for-fake-audio-capture | 95% | 待验证 | 高 | 备选升级 |

**选择 L2 的理由**：
- 前端代码真实运行（非 mock），验证面最广
- `agent-browser eval` 可以注入 JS，hook `WebSocket.send`
- 沙箱 TTS CLI 可预合成音频，注入到浏览器内存中
- 不依赖 Chromium 实验性 flag，兼容性好

### 2.2 核心原理

```
                         agent-browser 沙箱
┌────────────────────────────────────────────────────────┐
│                                                        │
│  预合成阶段（测试前完成）:                                │
│    z-ai tts → WAV(24kHz) → ffmpeg → PCM(16kHz)         │
│    ↓                                                    │
│    保存为 base64 JSON 文件: test_audio_utterance_1.json  │
│                                                        │
│  浏览器注入阶段:                                         │
│    agent-browser eval → 注入 hook 脚本                    │
│    ↓                                                    │
│    hook 拦截 MediaStream (getUserMedia)                  │
│    → 返回虚拟 AudioStream，数据源 = 预合成的 PCM          │
│    ↓                                                    │
│    前端 ScriptProcessorNode 正常读取虚拟流               │
│    → VAD 检测到语音 → 发送 32ms 分片                      │
│    → 后端 ASR 真实处理                                   │
│    ↓                                                    │
│    验证:                                                 │
│    agent-browser snapshot → 检查 UI 状态                  │
│    agent-browser console → 检查 WS 消息日志               │
│    agent-browser screenshot → 保存截图                    │
│                                                        │
└────────────────────────────────────────────────────────┘
```

### 2.3 关键技术点：如何 Hook getUserMedia

前端代码路径（`useVAD.ts`）：

```ts
const stream = await navigator.mediaDevices.getUserMedia({
  audio: { sampleRate: 16000, channelCount: 1, echoCancellation: true, noiseSuppression: true }
});
const audioContext = new AudioContext({ sampleRate: 16000 });
const source = audioContext.createMediaStreamSource(stream);
const processor = audioContext.createScriptProcessorNode(512, 1, 1);
source.connect(processor);
processor.connect(audioContext.destination);
processor.onaudioprocess = (e) => {
  // Float32 → Int16 → base64 → send
};
```

**Hook 策略**：在页面加载后、用户点击"开始录音"之前，通过 `agent-browser eval` 注入 JS 覆盖 `navigator.mediaDevices.getUserMedia`，返回一个使用预合成 PCM 数据的虚拟 MediaStream。

```js
// 注入到浏览器中的 hook（简化示意）
const originalGetUserMedia = navigator.mediaDevices.getUserMedia.bind(navigator.mediaDevices);
navigator.mediaDevices.getUserMedia = async function(constraints) {
  if (constraints.audio) {
    return createVirtualAudioStream(preloadedPCM, 16000);
  }
  return originalGetUserMedia(constraints);
};

function createVirtualAudioStream(pcmData, sampleRate) {
  // 创建一个 ScriptProcessorNode 作为数据源
  // 将 pcmData 以 512 samples/chunk 的速率喂入
  // 返回包装后的 MediaStream
}
```

**关键挑战**：`ScriptProcessorNode` 是 push 模式（浏览器回调），但虚拟流需要 pull 模式（我们主动推数据）。解决方案是使用 `AudioWorkletNode` 或定时器驱动的虚拟 `MediaStreamTrack`。

---

## 三、PR 拆分（每个 PR 只做一件事）

### PR #19: `chore: 添加浏览器 E2E 测试音频预合成工具脚本`

**功能描述**：一个独立的 Python 脚本，用沙箱 TTS 合成测试语音、ffmpeg 重采样，输出为 JSON 文件供浏览器 hook 使用。

**实现思路**：
- 读取测试语句数据集（与 test_pipeline_e2e.py 共享同一组语句）
- 逐条调用 `z-ai tts` 合成 WAV → ffmpeg 重采样到 16kHz PCM → base64 编码
- 输出 `tests/fixtures/test_audio_set.json`，格式：
  ```json
  {
    "utterances": [
      {
        "id": 1,
        "text": "你好，请介绍一下你自己",
        "pcm_base64": "/2JAAABk...",
        "sample_rate": 16000,
        "duration_ms": 1200,
        "keywords": ["你好", "介绍"]
      }
    ]
  }
  ```
- 支持 `--dry-run` 跳过 TTS 合成（使用已有缓存）

**测试方式**：
```bash
python3 tests/prepare_test_audio.py
# 验证 tests/fixtures/test_audio_set.json 存在且包含有效 PCM 数据
```

**涉及文件**：
- `tests/prepare_test_audio.py`（新建）
- `tests/fixtures/`（新建目录）
- `tests/fixtures/.gitkeep`

---

### PR #20: `test: 添加浏览器 getUserMedia Hook 注入脚本`

**功能描述**：一个 JS 脚本，通过 `navigator.mediaDevices.getUserMedia` hook 注入虚拟音频流，使前端 VAD 能处理预合成的 TTS 语音。

**实现思路**：
- 实现 `createFakeAudioStream(pcmBase64, sampleRate)` 函数
- 覆盖 `navigator.mediaDevices.getUserMedia`，当请求 `audio` 时返回虚拟流
- 虚拟流以正确的速率（512 samples / 32ms per chunk）推送 PCM 数据
- 支持 `window.__injectTestAudio(utteranceIndex)` 动态切换测试语句
- 支持 `window.__injectSilence(durationMs)` 注入静音（测试 VAD 静音检测和打断时序）
- 支持 `window.__injectTestAudioStatus()` 查询当前注入状态

**技术细节**：
- 使用 `MediaStreamTrackGenerator` API（Chrome 94+）创建可编程的音频轨道
- 以 `setInterval(32ms)` 的速率向轨道推送 PCM 数据块
- Float32 PCM 格式（匹配 ScriptProcessorNode 的输入格式）

**测试方式**：
```bash
# 手动验证：在浏览器 console 中加载脚本后检查
# 1. navigator.mediaDevices.getUserMedia 应返回虚拟流
# 2. 虚拟流产生正确的音频数据
# 3. 静音注入后流无数据输出
```

**涉及文件**：
- `tests/fixtures/getUserMedia_hook.js`（新建）

---

### PR #21: `test: 添加浏览器级 E2E 主测试脚本`

**功能描述**：一个 Shell 脚本，编排完整的浏览器级 E2E 测试流程：打开页面 → 注入 hook → 操作 UI → 验证结果。

**实现思路**：
- 使用 `agent-browser` 命令行完成所有操作
- 流程编排：
  ```bash
  # 1. 打开 Netlify 页面
  agent-browser open https://xengineer-dev.netlify.app
  agent-browser wait --load networkidle
  agent-browser screenshot download/browser-e2e/01-page-loaded.png

  # 2. 检查初始状态（WS 已连接）
  agent-browser snapshot -i
  agent-browser console

  # 3. 注入 getUserMedia hook + 加载预合成音频
  AUDIO_JSON=$(cat tests/fixtures/test_audio_set.json)
  agent-browser eval "window.__testAudioSet = $AUDIO_JSON"
  HOOK_SCRIPT=$(cat tests/fixtures/getUserMedia_hook.js)
  agent-browser eval "$HOOK_SCRIPT"

  # 4. 开启摄像头（虚拟 — headless 无真实摄像头，测试错误处理或跳过）
  agent-browser snapshot -i  # 找摄像头按钮 ref
  agent-browser click @e_camera
  agent-browser wait 1000

  # 5. 开始录音
  agent-browser click @e_mic
  agent-browser wait 1000

  # 6. 触发第一条测试语句
  agent-browser eval "window.__injectTestAudio(0)"
  agent-browser wait 5000  # 等待 VAD 检测 + ASR 识别 + LLM 回复

  # 7. 截图验证 UI 状态
  agent-browser screenshot download/browser-e2e/02-after-utterance1.png

  # 8. 检查 console 日志（WS 消息）
  agent-browser console

  # 9. 注入静音 → 触发 VAD 停止 → pipeline 完成
  agent-browser eval "window.__injectSilence(1000)"
  agent-browser wait 10000  # 等待 TTS 播放完成

  # 10. 截图验证最终状态
  agent-browser screenshot download/browser-e2e/03-after-response.png

  # 11. Barge-in 测试：在 AI 回复时注入新语音
  agent-browser eval "window.__injectTestAudio(1)"  # "你看到了什么？"
  agent-browser wait 2000  # VAD 检测到新语音
  agent-browser screenshot download/browser-e2e/04-barge-in.png

  # 12. 收集结果
  agent-browser console
  agent-browser errors
  agent-browser close
  ```

**验证检查项**：

| # | 检查项 | 方法 | 预期 |
|---|--------|------|------|
| C1 | 页面正常加载 | screenshot | UI 元素完整无白屏 |
| C2 | WS 连接成功 | console | 连接日志正常 |
| C3 | 开始录音后 VAD 检测语音 | console | vad_status(speaking: true) |
| C4 | ASR 识别结果 | console + DOM | asr_final 消息，用户气泡出现 |
| C5 | LLM 回复 | DOM | 流式文本气泡出现 |
| C6 | TTS 音频播放 | console | tts_audio 消息，无播放错误 |
| C7 | Barge-in 生效 | screenshot + console | TTS 被中断，新一轮对话开始 |
| C8 | 无 JS 错误 | errors | 空输出 |

**测试方式**：
```bash
bash tests/test_browser_e2e.sh
# 检查 download/browser-e2e/ 目录中的截图和日志
```

**涉及文件**：
- `tests/test_browser_e2e.sh`（新建）

---

### PR #22: `chore: 更新一键测试脚本，集成浏览器 E2E`

**功能描述**：将浏览器级 E2E 测试集成到 `tests/run_all_tests.sh` 一键测试流程中。

**实现思路**：
- 在现有 5 步测试基础上增加第 6 步：浏览器级 E2E
- 浏览器 E2E 设为可选步骤（默认跳过，`--full` 参数启用）
- 原因：浏览器 E2E 耗时较长（~60s），且需要预合成音频文件

**测试方式**：
```bash
# 快速测试（不含浏览器 E2E）
bash tests/run_all_tests.sh

# 完整测试（含浏览器 E2E）
bash tests/run_all_tests.sh --full
```

**涉及文件**：
- `tests/run_all_tests.sh`（修改）

---

### PR #23: `test: 添加浏览器 E2E 结果自动分析脚本`

**功能描述**：一个 Python 脚本，分析浏览器 E2E 测试产出的截图和日志，生成结构化报告。

**实现思路**：
- 读取 `download/browser-e2e/` 目录的截图和 agent-browser 输出
- 解析 console 日志，提取 WS 消息流
- 对比每条测试语句的 ASR 识别结果与预期关键词
- 生成 JSON 报告 + 可选的 Markdown 摘要
- 输出：
  ```json
  {
    "timestamp": "2026-06-15 14:00:00",
    "tests": [
      {
        "utterance_id": 1,
        "expected_text": "你好，请介绍一下你自己",
        "asr_result": "你好，请介绍一下你自己",
        "asr_matched": true,
        "llm_response_length": 120,
        "tts_audio_received": true,
        "barge_in_tested": false,
        "screenshot": "02-after-utterance1.png"
      }
    ],
    "summary": { "passed": 5, "failed": 0, "skipped": 0 }
  }
  ```

**测试方式**：
```bash
python3 tests/analyze_browser_e2e.py
# 验证 JSON 报告输出正确
```

**涉及文件**：
- `tests/analyze_browser_e2e.py`（新建）

---

### PR #24: `docs: 浏览器级 E2E 测试计划文档`

**功能描述**：本计划文件本身。记录浏览器级 E2E 测试的差距分析、技术方案、PR 拆分和验收标准。

**实现思路**：无代码改动，仅文档。

**涉及文件**：
- `docs/plans/browser-e2e-test-plan.md`（新建，即本文件）

---

## 四、执行顺序与依赖

```
PR #24 (本计划文档) ← 无依赖，先合并让评委看到规划
    ↓
PR #19 (音频预合成脚本) ← 无依赖，独立可用
    ↓
PR #20 (getUserMedia Hook JS) ← 依赖 #19 的输出格式
    ↓
PR #21 (浏览器 E2E 主脚本) ← 依赖 #19 + #20
    ↓
PR #22 (集成到一键脚本) ← 依赖 #21
    ↓
PR #23 (结果分析脚本) ← 依赖 #21 的输出格式
```

## 五、已知风险与缓解

| 风险 | 概率 | 影响 | 缓解方案 |
|------|------|------|---------|
| `MediaStreamTrackGenerator` API 在 headless Chromium 中不可用 | 中 | 高 | 回退到 L1 方案：agent-browser 操作 UI，后台 Python WS 脚本发音频 |
| 虚拟音频流时序不精确，VAD 检测失败 | 中 | 中 | 放大 PCM 音量（乘以系数），提高 VAD 触发率；降低 VAD 阈值（仅测试模式） |
| agent-browser `eval` 注入 JS 有 CSP 限制 | 低 | 高 | Netlify 部署无 CSP header（已确认）；如有，用 `--disable-web-security` flag |
| TTS 合成语音音质导致 ASR 识别率低 | 中 | 中 | 沙箱 TTS 已在 Phase 2 验证可用（5/5 ASR 识别正确）；可调语速减慢提高识别率 |
| headless 无摄像头导致前端报错 | 中 | 低 | 前端 Camera 组件有错误处理（显示红字），不影响核心链路；可在 hook 中同时 mock 摄像头 |

## 六、与现有测试的关系

```
                    测试金字塔

        ┌─────────────────────────┐
        │  浏览器级 E2E (本计划)    │  ← 最慢、最真实、覆盖 G1-G7
        │  agent-browser + JS Hook │     ~60s/轮
        ├─────────────────────────┤
        │  WS Pipeline E2E         │  ← 快速回归
        │  test_pipeline_e2e.py   │     ~30s/轮
        ├─────────────────────────┤
        │  前端视觉验证             │  ← 最快
        │  test_frontend_visual.sh │     ~10s
        ├─────────────────────────┤
        │  Health Check             │  ← 基础
        │  curl health endpoint    │     ~2s
        └─────────────────────────┘
```

浏览器级 E2E 不替代现有测试，而是**补充最上层**。快速迭代时跑 Pipeline E2E（30s），完整验证时跑浏览器级 E2E（60s）。

## 七、验收标准

| # | 标准 | 验证方式 |
|---|------|---------|
| A1 | 预合成音频脚本产出有效 JSON | `python3 tests/prepare_test_audio.py` → `tests/fixtures/test_audio_set.json` 存在 |
| A2 | getUserMedia Hook 可拦截虚拟流 | 在浏览器 console 加载 hook 后，`getUserMedia` 返回虚拟流 |
| A3 | 浏览器 E2E 跑完一轮无 JS 错误 | `agent-browser errors` 空输出 |
| A4 | ASR 识别到合成语音（>3/5 语句关键词匹配） | 分析报告中 `asr_matched: true` |
| A5 | LLM 回复出现在 UI（DOM 中有对应气泡） | 截图中可见聊天气泡 |
| A6 | TTS 音频被前端接收（console 有 tts_audio 消息） | console 日志 |
| A7 | Barge-in 测试通过（TTS 被打断，新一轮对话开始） | 截图 + console |
| A8 | 所有 PR 遵循规范（单一功能、清晰描述、合并后主分支可运行） | GitHub PR 列表 |

## 八、时间估算

| PR | 预计耗时 | 备注 |
|----|---------|------|
| #24 文档 | 10min | 已完成 |
| #19 音频预合成 | 15min | 基于 test_pipeline_e2e.py 的 TTS 逻辑 |
| #20 Hook JS | 30min | 需要调试虚拟流时序 |
| #21 主测试脚本 | 30min | agent-browser 命令编排 + 调试 |
| #22 一键脚本集成 | 10min | 小改动 |
| #23 结果分析 | 20min | 日志解析 |
| **合计** | **~2h** | 含调试时间 |
