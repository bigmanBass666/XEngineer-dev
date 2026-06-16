# 消除浏览器 E2E 测试 5 个 SKIP 项 Spec

## Why

浏览器 E2E 测试当前 19/24 通过，5 个 SKIP。SKIP 本质是检测逻辑不够健壮，不是功能缺失。根因分析：

1. **WebSocket 状态检查**（SKIP）：检查 `document.body.innerText.includes('已连接')`，但 StatusBar 组件确实渲染了"已连接"文本。可能是 3 秒等待不够，或 `innerText` 获取时机不对。
2. **ASR/TTS/LLM 消息检测**（3 个 SKIP）：测试脚本用 `agent-browser console` 获取浏览器日志，检查 `asr_final/asr_interim/tts_audio/llm_chunk` 关键词。但前端 App.tsx 的 `onMessage` handler 只在 `status` 和 `error` 类型才调用 `console.log`，`asr_final/llm_chunk/tts_audio` 均无日志输出。
3. **UI 对话元素检测**（SKIP）：snapshot 文本用英文正则 `chat|message|bubble|assistant|user`，但前端渲染的是中文内容（如"你好"、"AI"、聊天气泡），snapshot 文本不包含这些英文关键词。

## What Changes

- **修改 `tests/test_browser_e2e.sh`**：
  - WebSocket 检查：增加等待时间到 5 秒，并用 `eval document.body.innerText` 代替 `console`
  - ASR/TTS/LLM 验证：从依赖 console 日志改为 DOM 检测（检查 ChatBubble 是否出现、StreamingMessage 是否包含文本）
  - UI 对话元素检查：用中文关键词（"你好"/"AI"/用户消息内容）匹配 snapshot
- **不修改前端代码**：不为了测试而修改产品代码

## Impact

- Affected specs: `add-browser-e2e-test` checklist 项
- Affected code: `tests/test_browser_e2e.sh`

## ADDED Requirements

### Requirement: DOM-based message verification

测试脚本 SHALL 通过检查 DOM 元素（ChatBubble、StreamingMessage）来验证 ASR/TTS/LLM 链路，而非依赖 console.log。

#### Scenario: ASR 识别成功
- **WHEN** 后端返回 `asr_final` 消息
- **THEN** 前端渲染用户 ChatBubble，测试脚本通过 `wait --text` 或 snapshot 检测到用户消息内容

#### Scenario: LLM 回复成功
- **WHEN** 后端返回 `llm_chunk` 消息
- **THEN** 前端渲染 StreamingMessage，测试脚本通过 snapshot 检测到 AI 回复文本

#### Scenario: TTS 完成
- **WHEN** 后端返回 `tts_end` 消息
- **THEN** 前端将 StreamingMessage 转为 ChatBubble，测试脚本通过 snapshot 检测到最终 AI 消息

### Requirement: Robust WebSocket status check

测试脚本 SHALL 通过 `document.body.innerText` 检测 StatusBar 中的连接状态文本（"已连接"/"连接中"/"连接错误"），等待至少 5 秒。

### Requirement: UI element detection with Chinese keywords

测试脚本 SHALL 使用前端实际渲染的中文文本来检测对话元素（如 "AI"、"你好"、用户消息文本），而非英文关键词。

## MODIFIED Requirements

### Requirement: Console-based message verification (旧)
**修改为**: Console 检查作为辅助手段（信息性），DOM 检查作为主要验证手段。即使 console 无日志，DOM 验证通过即可 PASS。

## REMOVED Requirements

无。
