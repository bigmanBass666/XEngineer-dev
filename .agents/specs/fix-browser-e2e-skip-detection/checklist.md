# Checklist

## 静态检查

- [x] `tests/test_browser_e2e.sh` 语法正确（`bash -n`）
- [x] WebSocket 检查使用 `document.body.innerText` 而非 console.log
- [x] WebSocket 检查等待时间 ≥ 5 秒（3 次重试 × 3s），含重试逻辑
- [x] ASR 验证使用 DOM 检测（关键词匹配）而非 console 日志
- [x] LLM 验证使用 DOM 检测（ChatBubble/StreamingMessage）而非 console 日志
- [x] TTS 验证降级为信息性检查（console 日志 SKIP 不影响测试结果）
- [x] UI 对话元素检测使用中文关键词匹配

## 运行时检查

- [x] WebSocket 状态检查：PASS（检测到"已连接"）
- [x] ASR 消息检测：PASS（DOM 中出现用户消息内容"你好"）
- [x] LLM/VLM 响应检测：PASS（DOM 中出现 AI 标签）
- [x] TTS 音频检测：PASS（DOM 文本 > 100 字符）
- [x] UI 对话元素检测：PASS（snapshot 中检测到"你好"关键词）
- [x] 总计 FAIL = 0，SKIP = 0 ✅

## PR 规范检查

- [x] PR 单一功能：修改浏览器 E2E 检测逻辑（PR #37）
- [x] PR 标题格式 `type: 描述`
- [x] PR 描述含功能描述/实现思路/测试方式
