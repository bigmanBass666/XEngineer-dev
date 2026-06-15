# 浏览器级端到端测试 Spec

## Why

现有 Pipeline E2E 测试（`test_pipeline_e2e.py`）在 WebSocket 协议层直接构造 JSON 消息发送给后端，完全绕过了前端。它与真人在 Netlify 网页上的交互存在 12 项严重差距（音频分片大小/速率 8192B/200ms vs 1024B/32ms、消息发送顺序不同、缺少 Barge-in 打断测试等），无法验证前端 VAD、AudioPlayer、UI 状态流转等核心用户体验。需要一套浏览器级 E2E 测试，在真实前端代码路径中注入预合成语音，使前端全部代码真实运行，逼近真人测试效果。

## What Changes

- 新增 `tests/prepare_test_audio.py` — 沙箱 TTS 合成测试语音 + ffmpeg 重采样，输出为 JSON fixture 文件
- 新增 `tests/fixtures/mock_getusermedia.js` — `navigator.mediaDevices.getUserMedia` Hook 脚本，通过 `AudioContext.createMediaStreamDestination()` + `ScriptProcessorNode` 返回虚拟音频流，替代真实麦克风
- 新增 `tests/test_browser_e2e.sh` — 主测试脚本，编排 agent-browser 打开 Netlify 页面、注入 Hook、操作 UI（点击录音/停止）、注入预合成音频、等待 pipeline 响应、截图 + console 验证
- 新增 `tests/fixtures/inject_audio.js` — 音频注入辅助 JS，设置 `window.__mockAudio.audioQueue` 并触发 feeding
- 修改 `tests/run_all_tests.sh` — 集成浏览器 E2E 为可选第 6 步（`--full` 参数启用）

## Impact

- Affected specs: 无已有 spec 受影响（新增功能）
- Affected code: `tests/` 目录扩展，不修改 `xengineer-frontend/` 或 `xengineer-backend/` 任何源码

## ADDED Requirements

### Requirement: 音频预合成 Fixture 生成

系统 SHALL 提供一个 Python 脚本 `tests/prepare_test_audio.py`，调用沙箱 TTS CLI 合成中文测试语音，经 ffmpeg 重采样至 16kHz mono PCM，base64 编码后输出为 `tests/fixtures/test_audio_set.json`。

#### Scenario: 正常合成
- **WHEN** 运行 `python3 tests/prepare_test_audio.py`
- **THEN** 生成 `tests/fixtures/test_audio_set.json`，包含 5 条测试语句的 PCM base64 数据、采样率、时长、关键词信息

#### Scenario: TTS 不可用时降级
- **WHEN** `z-ai tts` 或 `ffmpeg` 不可用
- **THEN** 脚本使用正弦波作为降级音频并标注 `is_real: false`，不中断执行

#### Scenario: 缓存复用
- **WHEN** fixture 文件已存在且 `--force` 未指定
- **THEN** 跳过 TTS 合成，直接使用已有文件

---

### Requirement: getUserMedia Hook 虚拟音频流

系统 SHALL 提供一个 JS 脚本 `tests/fixtures/mock_getusermedia.js`，通过 monkey-patch `navigator.mediaDevices.getUserMedia` 返回虚拟 MediaStream。虚拟流使用 `AudioContext.createMediaStreamDestination()` + `ScriptProcessorNode(512, 0, 1)` 构造，以 32ms/chunk（512 samples at 16kHz）的速率推送 Float32 PCM 数据。

#### Scenario: 拦截音频请求
- **WHEN** 前端调用 `navigator.mediaDevices.getUserMedia({audio: true})`
- **THEN** 返回包含一个音频轨道的虚拟 MediaStream，AudioContext sampleRate 匹配前端请求（默认 16000）

#### Scenario: 无音频数据时输出静音
- **WHEN** 虚拟流活跃但 `window.__mockAudio.feeding` 为 false
- **THEN** ScriptProcessorNode 输出全零 PCM，前端 VAD 保持 `silent` 状态

#### Scenario: 注入音频数据
- **WHEN** 设置 `window.__mockAudio.audioQueue = Float32Array` 并 `window.__mockAudio.feeding = true`
- **THEN** ScriptProcessorNode 按真实速率推送音频数据，前端 VAD 检测到语音（RMS > 0.02 持续 3 帧 ≈ 96ms）后切换为 `speaking` 状态

#### Scenario: 音频数据耗尽自动停止
- **WHEN** audioQueue 数据推送完毕
- **THEN** 自动设置 `feeding = false`，offset 重置为 0，输出恢复静音

---

### Requirement: 浏览器级 E2E 主测试脚本

系统 SHALL 提供一个 Shell 脚本 `tests/test_browser_e2e.sh`，使用 `agent-browser` CLI 编排完整的浏览器级 E2E 测试流程。

#### Scenario: 完整单轮对话测试
- **WHEN** 运行 `bash tests/test_browser_e2e.sh`（无参数）
- **THEN** 执行以下流程并输出通过/失败结果：
  1. `agent-browser open` 打开 Netlify 线上前端 URL
  2. `--init-script` 加载 mock_getusermedia.js
  3. 等待页面加载完成（networkidle）
  4. 截图保存到 `download/browser-e2e/01-page-loaded.png`
  5. 检查 WS 连接状态（console 中 `[WS] Connected`）
  6. 通过 `eval --stdin` 加载预合成音频数据
  7. `snapshot -i` 找到按钮，`click` 开始录音
  8. `eval` 触发音频注入（`window.__mockAudio.feeding = true`）
  9. 等待 VAD 检测语音 → 截图 `02-vad-speaking.png`
  10. 等待 ASR 识别 + LLM 回复（最长 35s）
  11. `eval` 注入静音（`feeding = false`）触发 VAD silent → pipeline 完成
  12. 等待 TTS 播放 → 截图 `03-response-received.png`
  13. 检查 chat 区域出现用户气泡 + AI 气泡
  14. `errors` 检查无 JS 错误
  15. 输出结构化 JSON 结果到 `download/browser-e2e/result.json`

#### Scenario: Barge-in 打断测试
- **WHEN** 运行 `bash tests/test_browser_e2e.sh --barge-in`
- **THEN** 在 TTS 播放期间注入新音频，验证：
  1. 前端 VAD 切换为 speaking（StatusBar 显示 "正在说话"）
  2. 上一轮 TTS 被中断（AudioPlayer.stop() 生效）
  3. 截图 `04-barge-in.png` 显示 UI 状态正确

#### Scenario: 多轮对话测试
- **WHEN** 运行 `bash tests/test_browser_e2e.sh --multi`
- **THEN** 依次注入 3 条不同测试语句，每轮等待 pipeline 完成后截图，验证：
  1. Chat 区域累计多条消息
  2. 每轮 ASR 识别正确
  3. 每轮 LLM 回复不同

#### Scenario: 前置条件不满足时优雅跳过
- **WHEN** `tests/fixtures/test_audio_set.json` 不存在
- **THEN** 输出 SKIP 并提示运行 `prepare_test_audio.py`，退出码 0

---

### Requirement: 一键测试脚本集成

系统 SHALL 修改 `tests/run_all_tests.sh`，在现有 5 步基础上增加可选的第 6 步浏览器 E2E。

#### Scenario: 快速模式（默认）
- **WHEN** 运行 `bash tests/run_all_tests.sh`
- **THEN** 仅执行原有 5 步测试，跳过浏览器 E2E

#### Scenario: 完整模式
- **WHEN** 运行 `bash tests/run_all_tests.sh --full`
- **THEN** 在第 6 步执行 `bash tests/test_browser_e2e.sh --multi`

## MODIFIED Requirements

### Requirement: run_all_tests.sh 测试编排

在现有 5 步测试基础上，增加 `--full` 参数支持。当传入 `--full` 时，在第 6 步执行浏览器级 E2E 测试。浏览器 E2E 测试的失败不阻塞整体脚本退出码（记为 WARNING），因为浏览器 E2E 依赖沙箱 TTS 可用性和网络条件。

## REMOVED Requirements

无移除的需求。
