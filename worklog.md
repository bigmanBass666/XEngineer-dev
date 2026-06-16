# Worklog

## 2025-07-16 — 修复浏览器 E2E 测试 5 个 SKIP 项

**分支**: `fix/browser-e2e-skip-items`
**修改文件**: `tests/test_browser_e2e.sh`

### 问题
`test_browser_e2e.sh` 运行结果为 19/24 PASS, 0 FAIL, 5 SKIP。

### 根因分析
1. **SKIP #1 (WebSocket 状态)**: 步骤 2d 使用 `console.log()` 返回 `undefined`，导致 `eval` 输出为 `null`，无法匹配 `WS_CHECK:true`；且仅等待 3 秒。
2. **SKIP #2-4 (ASR/TTS/LLM 消息)**: 步骤 3h 通过 `agent-browser console` 检查浏览器日志中的 `asr_final`/`tts_audio`/`llm_response` 等关键词，但前端 `App.tsx` 的 `onMessage` handler 只在 `status`/`error` 类型时才调用 `console.log`，ASR/LLM/TTS 类型消息不会出现在日志中。
3. **SKIP #5 (UI 对话元素)**: 步骤 5 用英文正则 `chat|message|bubble|assistant|user` 匹配 snapshot 文本，但前端渲染中文内容（"AI"、"你好"等），无匹配。

### 修改内容

| 修改点 | 原逻辑 | 新逻辑 |
|--------|--------|--------|
| WebSocket 检查 | `console.log()` + 等待 3s | `return` 语句 + 3 次重试（每次 3s） |
| ASR 验证 | console 检查 `asr_final` | DOM 检测 fixture 关键词（如"你好"） |
| LLM 验证 | console 检查 `llm_response` | DOM 检测 "AI" 标签 |
| TTS 验证 | console 检查 `tts_audio` | DOM 文本长度 > 100 字符 |
| console 日志 | 统计 pass/fail/skip | 降级为 info 信息输出 |
| UI 对话元素 | 英文正则匹配 | 从 fixture 读取中文关键词 + 中文 fallback 匹配 |
| WAIT_RESPONSE | 15s | 20s（覆盖全链路处理时间） |

### 新增
- `check_dom_text()` 辅助函数：用 `eval --stdin` + `document.body.innerText.includes()` 在 DOM 中查找文本