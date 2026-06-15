# Browser E2E Test Plan v1 (ARCHIVED)

> **归档说明**: 此文件为 v1 浏览器 E2E 测试计划的归档占位。原始内容在会话上下文切换中丢失。
> 请参阅 v2 计划: [browser-e2e-test-plan-v2.md](../browser-e2e-test-plan-v2.md)

## v1 摘要（凭记忆恢复）

- 早期探索性规划，基于对 `test_pipeline_e2e.py` 的初步分析
- 提出了 L1（改进 Python 测试）和 L2（agent-browser + getUserMedia Hook）两种方案
- 技术选型最初考虑 `MediaStreamTrackGenerator`，后经子代理实测验证修正为 `createMediaStreamDestination`
- v1 计划作为 PR #19 合并，后精化为 v2

## v2 改进点

1. 新增完整的 12 项差距分析（G1-G12，按严重度分级）
2. 技术方案从 `MediaStreamTrackGenerator` 修正为 `createMediaStreamDestination`（实测验证）
3. 新增 Barge-in 和多轮对话测试模式
4. 新增详细的 PR 规范和验证清单
5. 新增风险评估与缓解措施
