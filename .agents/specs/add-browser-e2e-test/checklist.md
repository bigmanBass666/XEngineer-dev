# Checklist

- [x] `tests/prepare_test_audio.py` 可运行，产出 `tests/fixtures/test_audio_set.json` 包含 5 条语句的 PCM base64
- [x] `tests/fixtures/test_audio_set.json` 中的 PCM 数据格式正确（16kHz mono s16le base64，可被 JS Float32Array 正确解码）
- [ ] `tests/fixtures/mock_getusermedia.js` 在浏览器 console 中加载后，`navigator.mediaDevices.getUserMedia({audio:true})` 返回虚拟 MediaStream（不报错）
- [ ] 虚拟 MediaStream 在 `feeding=false` 时输出静音（VAD 不触发 speaking）
- [ ] 虚拟 MediaStream 在 `feeding=true` 且 audioQueue 有数据时，前端 VAD 在 ~96ms 内检测到 speaking 状态
- [ ] `tests/test_browser_e2e.sh` 无参数运行时执行单轮完整对话测试（录音 → 注入音频 → 等待响应 → 截图验证）
- [ ] `tests/test_browser_e2e.sh --barge-in` 运行时在 TTS 播放期间注入新音频，验证打断行为
- [ ] `tests/test_browser_e2e.sh --multi` 运行时执行 3 轮对话，chat 区域累计多条消息
- [x] `tests/test_browser_e2e.sh` 在 fixture 文件不存在时输出 SKIP 并优雅退出（exit 0）
- [ ] `download/browser-e2e/` 目录产出截图文件（01-page-loaded.png, 02-vad-speaking.png, 03-response-received.png 等）
- [ ] `download/browser-e2e/result.json` 包含结构化测试结果（每轮的 asr_matched、llm_received、tts_received、screenshot 路径）
- [ ] agent-browser errors 输出为空（无 JS 运行时错误）
- [x] `tests/run_all_tests.sh` 无参数运行时行为不变（不执行浏览器 E2E）
- [x] `tests/run_all_tests.sh --full` 运行时在第 6 步执行浏览器 E2E
- [x] 浏览器 E2E 失败不阻塞 run_all_tests.sh 整体退出码
- [ ] 所有新增文件遵循 PR 规范：每个功能一个 PR、标题/描述/测试方式完整
- [x] `tests/fixtures/.gitkeep` 存在，fixture JSON 在 .gitignore 中（避免大文件入库）
