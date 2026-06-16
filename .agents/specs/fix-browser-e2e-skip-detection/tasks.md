# Tasks

- [ ] Task 1: 修改 test_browser_e2e.sh — WebSocket 状态检查增强
  - [ ] SubTask 1.1: 将 WS 检查等待时间从 3s 增加到 5s
  - [ ] SubTask 1.2: 使用 eval + document.body.innerText 检测"已连接"，移除对 console.log 的依赖
  - [ ] SubTask 1.3: 增加重试逻辑：最多 3 次，每次间隔 3s

- [ ] Task 2: 修改 test_browser_e2e.sh — ASR/TTS/LLM 验证改为 DOM 检测
  - [ ] SubTask 2.1: 在 `run_conversation_round` 函数中，替换 console 日志检查为 DOM 检查
  - [ ] SubTask 2.2: 新增 `check_dom_messages()` 辅助函数：通过 snapshot 或 eval 检查 DOM 中是否存在 ChatBubble（用户消息）和 AI 回复
  - [ ] SubTask 2.3: ASR 验证：检查 DOM 中是否出现 utterance 的关键词文本（如"你好"/"介绍"）
  - [ ] SubTask 2.4: LLM 验证：检查 DOM 中是否出现 StreamingMessage 或 AI ChatBubble（非空文本内容）
  - [ ] SubTask 2.5: TTS 验证：作为辅助检查保留 console（因为 TTS 只调 enqueue，无 DOM 变化），但标记为信息性而非必须通过
  - [ ] SubTask 2.6: console 检查降级为信息性日志（SKIP 不再计入失败统计）

- [ ] Task 3: 修改 test_browser_e2e.sh — UI 对话元素检测修复
  - [ ] SubTask 3.1: 最终 snapshot 检查使用中文关键词匹配（"AI"、"你好"、"介绍"、utterance text）
  - [ ] SubTask 3.2: 移除英文关键词正则 `chat|message|bubble|assistant|user`，改用前端实际渲染的文本

- [ ] Task 4: 运行时验证
  - [ ] SubTask 4.1: 语法检查 `bash -n tests/test_browser_e2e.sh`
  - [ ] SubTask 4.2: 实际运行 `bash tests/test_browser_e2e.sh`，目标 0 FAIL，SKIP 降至 ≤ 1（仅 TTS console 信息性）
  - [ ] SubTask 4.3: 如果仍有 SKIP > 1，分析根因并迭代修复

# Task Dependencies
- Task 2 depends on Task 1（WS 检查是后续验证的前提）
- Task 3 depends on Task 2（DOM 检查逻辑统一）
- Task 4 depends on Task 1, 2, 3
