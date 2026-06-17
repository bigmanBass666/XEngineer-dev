# 视觉对话端到端闭环测试计划

> 状态：**讨论中，持续更新**
> 最后更新：2026-06-15
> 目标：建立「测试 → 发现问题 → 修复 → 再测试」的自动化闭环，覆盖视觉对话完整链路

---

## Phase 0：Git/PR 规范强制执行 ✅ 已完成

已完成内容：pre-commit hook 阻止 main 分支 commit、pre-push hook 阻止直接推 main、setup.sh 增加 PR 规范提醒、冻结仓库已移除、仓库统一为单一 origin（XEngineer-dev）。相关 PR：#3-#7。

---

## 零、沙箱测试工具箱

> **核心原则**：沙箱内有一组 SDK CLI 工具（TTS/ASR/VLM/agent-browser/image-search/web-reader），可以作为**测试验证工具**使用，但**不能作为项目依赖**——这些 SDK 离开沙箱就不可用。测试脚本中可以调用它们，但项目源码（后端/前端）不能 import 它们。

### 可用工具一览

| 工具 | CLI 命令 | 能力 | 对应 Phase |
|------|---------|------|-----------|
| **TTS** | `z-ai tts -i "文本" -o output.pcm --format pcm` | 合成真实中文语音，输出 PCM/WAV/MP3，24kHz | Phase 2 — 解决 D3（替代无效的正弦波） |
| **ASR** | `z-ai asr -f audio.wav -o result.json` | 语音转文字，验证音频识别结果 | Phase 2 — 独立验证 ASR 输出 |
| **VLM** | `z-ai vision -p "描述图片" -i image.jpg` | 图像理解，支持 base64 内联 `data:image/...;base64,...` | Phase 1 — 验证方案 A 可行性 |
| **agent-browser** | `agent-browser open <url>` + `snapshot`/`screenshot`/`console` | 前端自动化：截图、DOM 检查、console log/error | Phase 3 — 前端视觉验证 |
| **image-search** | `z-ai image-search -q "描述" -c 5` | 搜索网络图片，返回可用的公网 URL | Phase 1 — 生成测试图片数据 |
| **web-reader** | `z-ai function -n page_reader -a '{"url":"..."}'` | 抓取网页内容 | 辅助 — 验证部署页面可访问 |

### 关键约束

- **TTS 单次上限 1024 字符**，长文本需分段
- **TTS 输出 24kHz**，项目 ASR 期望 16kHz → 需要 ffmpeg 重采样（`-ar 16000`）
- **VLM 支持 base64 内联 URL**，格式 `data:image/jpeg;base64,<data>` → 这直接验证了 Phase 1 方案 A 可行
- **agent-browser 无摄像头/麦克风** → 只能验证页面加载、WS 连接、UI 状态，不能测试真实音视频采集

---

## 一、背景与问题

### 1.1 当前测试能力

已实现的测试手段：

| 工具 | 能力 | 已验证 | 备注 |
|------|------|--------|------|
| `curl` | 后端 health check | ✅ | — |
| Python `websockets` 脚本 | WS 连接、echo、VAD 会话 | ✅ | — |
| 合成正弦波 PCM | 音频传输协议 | ✅（但 ASR 无法识别） | **将被沙箱 TTS 替代** |
| `agent-browser` | 前端截图、console log 抓取 | ✅ | — |
| `railway logs` | 后端运行时日志 | ✅ | — |
| 沙箱 TTS CLI | 合成真实中文语音 | 🆕 待用 | 解决 D3 |
| 沙箱 VLM CLI | 验证 base64 图片理解 | 🆕 待用 | 验证 Phase 1 方案 |
| 沙箱 ASR CLI | 独立验证音频识别 | 🆕 待用 | Phase 2 对照验证 |

### 1.2 当前链路断裂（已发现）

| # | 断裂点 | 位置 | 影响 | 沙箱工具如何辅助 |
|---|--------|------|------|----------------|
| D1 | 图片未传入 VLM | `orchestrator.py` handle_image() 只保存 base64，未调用 `vlm_node.update_image()` | VLM 始终无图，产品是"纯文本对话" | 修复后用 VLM CLI 发送 base64 图片验证端到端 |
| D2 | VLM 期望 image_url 而非 base64 | `vlm_node.py` 第 54 行读 `image_url`，但 ASR 传来的是 `image: base64数据` | 即使修了 D1，VLM 拿到的也是无效的 base64 字符串当 URL | VLM CLI 已证明 `data:image/jpeg;base64,...` 格式可用 → 方案 A 可行 |
| D3 | 合成测试数据无真实语音 | 正弦波 440Hz 不是语音，ASR 识别不出文字 | 无法验证 ASR→VLM→TTS 完整链路 | **沙箱 TTS 直接解决**：`z-ai tts` 生成真实中文语音 |
| D4 | agent-browser 无摄像头/麦克风 | headless 浏览器无法获取硬件设备 | 无法模拟真实视频通话场景 | 无解，需用户手动测试；但可用 TTS 音频替代麦克风输入 |

### 1.3 目标闭环

```
  ┌──────────────────────────────────────────────────────┐
  │                    测试闭环                              │
  │                                                        │
  │  沙箱 TTS 合成语音 ──→ WS 发送 ──→ 后端 ASR 识别       │
  │       ↑                                    ↓          │
  │  验证 TTS 输出 ←── 后端 TTS ←── VLM+LLM(带图片)       │
  │                                                        │
  │  agent-browser 打开前端 ──→ 截图 ──→ console 检查      │
  │                                                        │
  │  沙箱 VLM 独立验证：base64 图片 → 描述文字              │
  │  沙箱 ASR 独立验证：合成音频 → 识别文字                   │
  │                                                        │
  │  发现问题 → 修代码 → push PR → Railway 部署 → 重测      │
  └──────────────────────────────────────────────────────┘
```

---

## 二、计划分步

### Phase 1：修通图片链路（D1 + D2）

**目标**：让 Camera 截图真正流入 VLM，实现多模态理解

**涉及文件**：
- `xengineer-backend/app/pipeline/orchestrator.py` — handle_image() 改为调用 vlm_node
- `xengineer-backend/app/pipeline/vlm_node.py` — 支持接收 base64 图片（而非仅 URL）

**技术方案 — 确定用方案 A（base64 直传）**：

沙箱 VLM CLI 已验证 `data:image/jpeg;base64,...` 内联 URL 格式可用，无需外部图床。

| 方案 | 做法 | 优点 | 缺点 | 决定 |
|------|------|------|------|------|
| A. base64 直传 | orchestrator 把 base64 直接传给 VLM，VLM 构建 `data:image/jpeg;base64,...` 内联 URL | 零外部依赖，纯内存；沙箱 VLM 已验证可行 | base64 体积大，每帧 ~100KB | ✅ 采用 |
| B. 临时图床 | orchestrator 把 base64 存到 Railway volume / S3 / imgbb，拿到公网 URL 再传给 VLM | 图片体积小，URL 可缓存 | 多一个外部依赖，增加延迟和故障点 | ❌ 不采用 |

**改动要点**：
1. `orchestrator.handle_image()` → 调用 `self.vlm_node.update_image(data)` 传入 base64
2. `vlm_node.process()` → 构造 `data:image/jpeg;base64,{base64_data}` 作为 image_url
3. `asr_node._on_final()` → 传递 `{"text": text, "image": self._latest_image}`（已有，需确认 orchestrator 会把 image 传下来）

**沙箱验证方案**（修复后执行）：
1. 用 `image-search` 搜索一张测试图片，拿到 base64 数据
2. 用 VLM CLI 验证：`z-ai vision -p "请描述这张图片" -i test.jpg` 确认 VLM 能理解图片
3. 通过 WS 发送图片 + 文字消息到后端，验证 LLM 回复包含画面相关描述
4. 对照 VLM CLI 的独立输出和后端的 LLM 回复，确认图片确实流入了 VLM

**PR 规划**：
- PR 标题：`fix: 修复图片未传入 VLM 的断裂，实现多模态对话`
- 包含文件：orchestrator.py, vlm_node.py
- 测试：沙箱 VLM CLI 验证 + WS 端到端验证

---

### Phase 2：沙箱 TTS 合成测试语音 → 端到端闭环（D3）

**目标**：用沙箱 TTS 合成真实中文语音 → 转码 → 喂给后端 ASR → 跑通完整链路

**技术方案**：

```
沙箱 TTS CLI（z-ai tts）
  "你好，请介绍一下你自己"
       ↓
  WAV/PCM 音频（24kHz）
       ↓
  ffmpeg 重采样 → PCM 16kHz mono（匹配后端 ASR 期望）
       ↓
  base64 encode → WebSocket 发送到后端
       ↓
  后端 ASR 识别 → VLM（带图片，Phase 1 修好后）→ LLM 回复 → TTS 输出
```

**前置依赖**：
- `ffmpeg` 可用（沙箱内检查）
- 后端 Railway 已部署且 health check 通过
- Phase 1 已完成（图片链路修通）

**测试数据集**（沙箱 TTS 合成）：

| # | 测试语句 | 预期 ASR 识别 | 验证点 |
|---|---------|-------------|--------|
| 1 | "你好，请介绍一下你自己" | 你好，请介绍一下你自己 | 基础对话 |
| 2 | "你看到了什么？" | 你看到了什么 | 触发 VLM 视觉描述 |
| 3 | "画面中有几个人？" | 画面中有几个人 | VLM 计数能力 |
| 4 | "请用中文回答" | 请用中文回答 | 语言控制 |
| 5 | "谢谢，再见" | 谢谢，再见 | 结束对话 |

**沙箱验证方案**（分两步验证）：

**步骤 A — 独立验证 TTS→ASR（不经过后端）**：
```bash
# 1. 合成语音
z-ai tts -i "你好，请介绍一下你自己" -o test_voice.wav --format wav
# 2. 重采样到 16kHz
ffmpeg -i test_voice.wav -ar 16000 -ac 1 test_voice_16k.wav
# 3. 独立 ASR 验证
z-ai asr -f test_voice_16k.wav -o asr_result.json
# 4. 对比识别结果与原始文本
```
这一步确认 TTS→ASR 链路在沙箱内可用，ASR 能正确识别 TTS 合成的语音。

**步骤 B — 端到端验证（经过后端 WS）**：
```bash
# 1. 合成语音 → 重采样 → base64
# 2. 通过 WebSocket 发送到后端
# 3. 检查后端 ASR 识别结果
# 4. 检查 LLM 回复内容
# 5. 检查 TTS 输出音频数据格式
```

**涉及文件**：
- `tests/test_pipeline_e2e.py` — 更新测试脚本，调用沙箱 TTS 生成真实语音数据

**PR 规划**：
- PR 标题：`test: 用沙箱 TTS 合成真实语音替代正弦波，更新端到端测试`
- 包含文件：tests/test_pipeline_e2e.py
- 测试：5 条测试语句全部通过 ASR 识别 + LLM 回复合理

---

### Phase 3：前端 agent-browser 视觉验证

**目标**：用 agent-browser 打开线上前端，验证 WebSocket 连接 + UI 状态

**测试流程**：
```
agent-browser open https://optalk.netlify.app
  → screenshot（保存到 /home/z/my-project/download/）
  → snapshot -i（检查页面交互元素）
  → console（检查 WS 连接日志）
  → errors（检查 JS 异常）
  → wait --text "Connected"（确认 WS 连接成功，或检查连接状态元素）
  → screenshot（显示 connected 状态）
```

**可验证项**：

| # | 验证项 | 方法 | 预期结果 |
|---|--------|------|---------|
| 1 | 页面正常加载 | `agent-browser screenshot` | 无白屏，UI 元素完整 |
| 2 | WebSocket 连接建立 | `agent-browser console` 检查 WS 日志 | 看到 `[WS] Connected` 或类似消息 |
| 3 | 无 JS 错误 | `agent-browser errors` | 空输出 |
| 4 | UI 交互元素存在 | `agent-browser snapshot -i` | 按钮输入框等元素可识别 |

**限制**：
- headless 无摄像头，无法测试 Camera 组件
- headless 无麦克风，无法测试 AudioRecorder
- 无法播放/听到 TTS 音频输出

**涉及文件**：
- `tests/test_frontend_visual.sh` — agent-browser 自动化测试 shell 脚本

**PR 规划**：
- PR 标题：`test: 添加前端 agent-browser 视觉验证脚本`
- 包含文件：tests/test_frontend_visual.sh

---

### Phase 4：一键测试脚本

**目标**：一个命令跑完所有测试，输出报告

**脚本设计**：`tests/run_all_tests.sh`

```bash
#!/bin/bash
# XEngineer 一键测试（从沙箱运行）
set -e

RESULTS=()

echo "=== 1. 后端 Health Check ==="
HEALTH=$(curl -sf https://xengineer-dev-production.up.railway.app/health)
echo "$HEALTH"
RESULTS+=("Health: OK")

echo ""
echo "=== 2. 前端页面可访问 ==="
STATUS=$(curl -sf -o /dev/null -w "%{http_code}" https://optalk.netlify.app)
echo "HTTP $STATUS"
RESULTS+=("Frontend: HTTP $STATUS")

echo ""
echo "=== 3. 沙箱 TTS→ASR 独立验证 ==="
z-ai tts -i "你好" -o /tmp/test_voice.wav --format wav 2>/dev/null
ffmpeg -i /tmp/test_voice.wav -ar 16000 -ac 1 /tmp/test_voice_16k.wav -y 2>/dev/null
z-ai asr -f /tmp/test_voice_16k.wav -o /tmp/asr_result.json 2>/dev/null
echo "ASR 结果: $(cat /tmp/asr_result.json)"
RESULTS+=("TTS→ASR: $(cat /tmp/asr_result.json | head -1)")

echo ""
echo "=== 4. Pipeline E2E（WS 测试） ==="
python3 tests/test_pipeline_e2e.py
RESULTS+=("Pipeline E2E: done")

echo ""
echo "=== 5. 前端视觉验证 ==="
bash tests/test_frontend_visual.sh
RESULTS+=("Frontend Visual: done")

echo ""
echo "=== 测试报告 ==="
for r in "${RESULTS[@]}"; do
  echo "  ✅ $r"
done
```

**PR 规划**：
- PR 标题：`chore: 添加一键测试脚本 run_all_tests.sh`
- 包含文件：tests/run_all_tests.sh

---

## 三、已知限制

| 限制 | 原因 | 影响 | 缓解方案 |
|------|------|------|---------|
| 无法测试真实摄像头 | headless 无硬件 | Camera 组件未经验证 | 用户手动测试 + 录屏 |
| 无法测试真实麦克风 | headless 无硬件 | AudioRecorder + VAD 未验证 | **沙箱 TTS 合成语音替代** |
| 无法听到 TTS 音频 | 无声卡/扬声器 | 音频播放效果未知 | 验证后端返回的 base64 音频数据格式有效 |
| TTS→ASR 音质有损 | 合成语音 → 重采样 → WS 传输 | ASR 识别率可能低于真实语音 | 多条测试语句，沙箱独立 ASR 对照 |
| 沙箱 SDK 不可用于项目代码 | SDK 只在沙箱内可用 | 不能写进项目源码 | 仅用于测试脚本，项目用 Volcengine 原生 SDK |
| TTS 24kHz → ASR 16kHz | 采样率不匹配 | 需要 ffmpeg 重采样 | `ffmpeg -ar 16000` 一行解决 |
| Railway 冷启动延迟 | 免费套餐休眠 | 首次请求可能超时 | 测试前先发 health check 唤醒 |

---

## 四、执行顺序与依赖

```
Phase 0 (Git规范强制) ✅ 已完成（PR #3-#7）
    ↓
Phase 1 (修图片链路) ← 无依赖，可立即开始
    ↓                ← 沙箱 VLM CLI 已验证 base64 方案可行
Phase 2 (TTS合成语音) ← 依赖 Phase 1（图片通了才有意义）
    ↓                ← 沙箱 TTS + ASR + ffmpeg 重采样
Phase 3 (前端视觉验证) ← 可与 Phase 2 并行
    ↓                ← agent-browser 自动化
Phase 4 (一键脚本) ← 依赖 Phase 2 + Phase 3 完成
```

---

## 五、验收标准

| # | 标准 | 验证方式 |
|---|------|---------|
| A | 图片传入 VLM，LLM 回复包含画面描述 | 沙箱 VLM CLI 验证 + WS 端到端：发测试图片 + "请描述你看到了什么" |
| B | TTS→ASR→VLM→TTS 完整链路通过 | 沙箱 TTS 合成语音 → WS 发送 → 5/5 语句 ASR 识别正确 |
| C | 前端 WS 连接稳定，console 无 error | agent-browser 测试 |
| D | 所有改动通过 PR 提交，符合比赛规范 | GitHub PR 列表 |
| E | 主分支可运行，任意时间查看可复现 | Railway + Netlify 部署验证 |
