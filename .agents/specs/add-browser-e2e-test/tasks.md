# Tasks

- [x] Task 1: 创建音频预合成脚本 `tests/prepare_test_audio.py`
  - [x] SubTask 1.1: 调用 `z-ai tts` 合成 5 条测试语句的 WAV 音频
  - [x] SubTask 1.2: 用 ffmpeg 重采样至 16kHz mono PCM（s16le 格式）
  - [x] SubTask 1.3: 将 PCM base64 编码，输出为 `tests/fixtures/test_audio_set.json`
  - [x] SubTask 1.4: 支持 `--force` 强制重新合成、缓存复用、TTS 不可用时正弦波降级
  - [x] SubTask 1.5: 创建 `tests/fixtures/` 目录 + `.gitkeep`

- [x] Task 2: 创建 getUserMedia Hook 脚本 `tests/fixtures/mock_getusermedia.js`
  - [x] SubTask 2.1: Monkey-patch `navigator.mediaDevices.getUserMedia`
  - [x] SubTask 2.2: 使用 `AudioContext.createMediaStreamDestination()` + `ScriptProcessorNode(512, 0, 1)` 构造虚拟 MediaStream
  - [x] SubTask 2.3: 实现 `window.__mockAudio` 状态对象（audioQueue, offset, feeding）
  - [x] SubTask 2.4: 无数据时输出静音，feeding 时按 32ms/chunk 速率推送 Float32 PCM
  - [x] SubTask 2.5: 音频数据耗尽时自动停止（feeding=false, offset=0）

- [x] Task 3: 创建浏览器 E2E 主测试脚本 `tests/test_browser_e2e.sh`
  - [x] SubTask 3.1: 打开 Netlify 页面 + `--init-script` 加载 mock_getusermedia.js
  - [x] SubTask 3.2: 等待 networkidle + 截图 + 检查 WS 连接
  - [x] SubTask 3.3: 通过 `eval --stdin` 加载预合成音频 JSON
  - [x] SubTask 3.4: snapshot 找按钮 → click 开始录音
  - [x] SubTask 3.5: eval 触发音频注入 → 等待 VAD speaking → 截图
  - [x] SubTask 3.6: 注入静音 → 等待 pipeline 完成（ASR + LLM + TTS）
  - [x] SubTask 3.7: 截图验证 chat 气泡 + errors 检查
  - [x] SubTask 3.8: 输出 `result.json` 结构化结果
  - [x] SubTask 3.9: `--barge-in` 模式：TTS 播放期间注入新音频
  - [x] SubTask 3.10: `--multi` 模式：3 轮对话依次测试
  - [x] SubTask 3.11: 前置条件检查（fixture 文件存在性），不存在时 SKIP

- [x] Task 4: 修改 `tests/run_all_tests.sh` 集成浏览器 E2E
  - [x] SubTask 4.1: 添加 `--full` 参数解析
  - [x] SubTask 4.2: `--full` 时执行第 6 步 `bash tests/test_browser_e2e.sh --multi`
  - [x] SubTask 4.3: 浏览器 E2E 失败记为 WARNING 不阻塞退出码

# Task Dependencies

- [Task 2] depends on [Task 1] — Hook 脚本需要 fixture JSON 中的音频格式定义
- [Task 3] depends on [Task 1] and [Task 2] — 主脚本需要预合成音频 + Hook 脚本
- [Task 4] depends on [Task 3] — 集成需要主脚本已完成
