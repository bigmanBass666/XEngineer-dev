# Checklist

## 静态检查

- [ ] `tests/test_browser_e2e.sh` 语法正确（`bash -n`）
- [ ] WebSocket 检查使用 `document.body.innerText` 而非 console.log
- [ ] WebSocket 检查等待时间 ≥ 5 秒，含重试逻辑
- [ ] ASR 验证使用 DOM 检测（关键词匹配）而非 console 日志
- [ ] LLM 验证使用 DOM 检测（ChatBubble/StreamingMessage）而非 console 日志
- [ ] TTS 验证降级为信息性检查（console 日志 SKIP 不影响测试结果）
- [ ] UI 对话元素检测使用中文关键词匹配

## 运行时检查

- [ ] WebSocket 状态检查：PASS（检测到"已连接"）
- [ ] ASR 消息检测：PASS 或信息性 SKIP（DOM 中出现用户消息内容）
- [ ] LLM/VLM 响应检测：PASS（DOM 中出现 AI 回复文本）
- [ ] TTS 音频检测：信息性检查（console 日志，SKIP 不计入失败）
- [ ] UI 对话元素检测：PASS（snapshot 中检测到对话相关文本）
- [ ] 总计 FAIL = 0，SKIP ≤ 1（仅 TTS 信息性）

## PR 规范检查

- [ ] PR 单一功能：修改浏览器 E2E 检测逻辑
- [ ] PR 标题格式 `type: 描述`
- [ ] PR 描述含功能描述/实现思路/测试方式
