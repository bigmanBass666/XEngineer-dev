# Checklist

## 静态检查

- [x] `tests/test_browser_e2e.sh` 使用 `eval --stdin` 加载 mock_getusermedia.js（--init-script 在 open 子命令后无效，改为 eval --stdin 注入）
- [x] `tests/test_browser_e2e.sh` 的 `inject_pcm()` 使用 `pcm_float32_base64` 直接解码（无 s16le 转换）
- [x] `tests/test_browser_e2e.sh` 在注入音频前检查 WebSocket 连接状态
- [x] `tests/test_pipeline_e2e.py` 音频分片为 1024B/32ms（非 8192B/200ms）
- [x] `tests/test_pipeline_e2e.py` 消息顺序为 `vad_status(true) → image → audio → vad_status(false)`
- [x] `tests/test_pipeline_e2e.py` 去掉了 vad_status(true) 后的多余 sleep(2) 和 audio 后的 sleep(1)
- [x] 所有修改文件语法正确（`bash -n` / `python3 -m py_compile`）

## 运行时检查

- [x] `prepare_test_audio.py` 成功生成 `test_audio_set.json`（含 pcm_float32_base64，5/5 真实语音）
- [x] 浏览器 E2E 单轮模式：页面加载 → Hook 注入生效 → 音频注入 31680 samples → 录音按钮点击 → 截图生成
- [x] `download/browser-e2e/` 目录产出截图文件（01_page_loaded.png, 02_round1_speaking.png, 02_round1_response.png, 07_final_state.png）
- [x] `download/browser-e2e/result.json` 结构完整且 `all_passed` 为 true
- [x] 浏览器 E2E 无 JS 运行时错误

## PR 规范检查

- [x] 每个 PR 单一功能（PR #32 init-script+Float32+WS+G1/G2, PR #33-#35 PCM注入修复迭代）
- [x] PR 标题格式 `type: 描述`
- [x] PR 描述含功能描述/实现思路/测试方式三段
