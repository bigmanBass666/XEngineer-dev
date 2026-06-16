# XEngineer 全真视频通话 E2E 测试计划

> 创建时间: 2026-06-17
> 最后更新: 2026-06-17
> 状态: **执行中**

---

## 一、目标

模拟真人从打开页面到完成多轮视频对话的全过程，验证 **VAD → ASR → VLM → LLM → TTS** 每个环节真正跑通。评委看到的是一个完整可用的视频对话系统，不是只检查 UI 元素存不存在。

---

## 二、当前现状（2026-06-17 实际调研）

### 2.1 前端（Netlify）✅ 已就绪
- 地址: `https://xengineer-frontend.netlify.app`
- 部署: 自动构建已配置（GitHub push → Netlify build hook → 自动部署）
- UI 状态: 页面渲染正常，按钮可点击，视频镜像，无 JS 错误
- 已验证: 18/18 基础自动化测试通过

### 2.2 后端（Railway）❌ 构建失败
- 服务名: `XEngineer-dev`
- Service ID: `db408340-3525-41ff-865d-a68108b7966b`
- Project: `imaginative-fascination` (`42bfbd0d-03fe-4b50-801c-e83978fe75f3`)
- Environment: `production` (`ed9ce954-227e-4759-a63d-ee16f3631715`)
- Service Instance: `151a8521-503d-483d-91f2-3f965e1db5ed`
- Root Directory: `xengineer-backend/` ✅（已通过 GraphQL API 设置）
- **域名**: `xengineer-dev-production.up.railway.app`
- **最近 3 次部署全部 FAILED**:
  - `98b48899` — FAILED (2026-06-16T15:40:14)
  - `c6365767` — FAILED (2026-06-16T15:35:02)
  - `e8225200` — FAILED (2026-06-16T13:01:52)
- **环境变量**: 用户已配置（火山引擎 token、AGNES key 等）✅

### 2.3 nixpacks.toml 疑似问题
当前 nixpacks.toml 在**仓库根目录** (`XEngineer/nixpacks.toml`)，内容：
```toml
[phases.setup]
nixPkgs = ["...", "python311"]

[phases.install]
cmds = ["pip install -r xengineer-backend/requirements.txt"]

[start]
cmd = "cd xengineer-backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT"
```
同时 `xengineer-backend/runtime.txt` 指定 `python-3.12.0`，可能版本冲突。

### 2.4 前端 WS 地址断裂
当前 `useWebSocket.ts` 第 4 行 fallback 走 `wss://xengineer-frontend.netlify.app:8000/ws`，
后端实际在 `wss://xengineer-dev-production.up.railway.app/ws`。

---

## 三、断裂点与修复计划

| # | 断裂点 | 严重度 | 修复方案 | PR |
|---|--------|--------|---------|-----|
| D1 | Railway 构建 3 次 FAILED | 🔴 阻塞 | 查构建日志 → 修 nixpacks.toml（可能需移入 xengineer-backend/ 或统一 Python 版本） | 待定 |
| D2 | 前端 WS fallback 地址错误 | 🔴 阻塞 | 修改 useWebSocket.ts fallback 为 Railway 域名 + Netlify 注入 VITE_WS_URL | 待定 |
| D3 | Stub 模式 TTS 无真实音频 | 🟡 影响 Stub 测试 | 修改 StubNode 使 TTS stub 发送一段预录 mp3 base64 | 待定 |

---

## 四、全链路数据流

```
用户点击"开始录音"
  → getUserMedia(audio) → AudioContext(16kHz) → ScriptProcessorNode(512,1,1)
  → EnergyVAD 检测 speaking
  → App.tsx: send({type:"vad_status", speaking:true})
  → WS → 后端 orchestrator._start_asr_session()
  → 同时 Camera 组件截图 → send({type:"image", data:base64})

用户说话中...
  → ScriptProcessorNode 每 32ms 回调
  → VAD speaking 状态下: Float32→Int16→base64
  → App.tsx: send({type:"audio", data:base64})
  → WS → 后端 ASR 节点

用户停止说话（VAD silent）
  → send({type:"vad_status", speaking:false})
  → ASR stop_session() → 最终识别结果
  → {type:"asr_final", text:"..."} → 前端对话区
  → VLM+LLM: 多模态 prompt → Agnes API 流式生成
  → 多个 {type:"llm_chunk"} → StreamingMessage 实时显示
  → TTS: 火山合成 mp3 → {type:"tts_audio", data:base64}
  → 前端 AudioPlaybackManager.enqueue() → 解码播放
  → {type:"tts_end"} → ChatBubble 写入完整回复
```

---

## 五、执行阶段

### P1 — 修复 Railway 构建（阻塞一切）
- 查构建日志定位错误
- 统一 Python 版本或调整 nixpacks.toml
- push → 等重构建 → 验证 `/health`
- **产出**: PR + 后端健康

### P2 — 修复前端 WS 地址
- 修改 `useWebSocket.ts` fallback 指向 Railway 域名
- Netlify 配置 `VITE_WS_URL` 环境变量
- push → 等自动部署
- **产出**: PR + 前端重新部署

### P3 — 验证 WS 连通
- agent-browser 打开 Netlify 页面
- 验证 StatusBar 显示"已连接"
- 发送测试消息 → 收到 WS echo
- **产出**: 截图 + result.json

### P4 — Stub 模式全链路测试
- 注入 getUserMedia hook + 虚拟摄像头 + PCM 音频
- 点击录音 → VAD → audio → 后端 stub 处理
- 修改 TTS stub 发送真实 mp3 验证播放链路
- **产出**: PR（stub 改动）+ 截图 + result.json

### P5 — 真实模式全链路测试
- Railway 切换 `USE_REAL_NODES=true`
- 完整 VAD → ASR → VLM+LLM → TTS
- 多轮对话 + barge-in
- **产出**: 截图 + result.json + 最终验收

---

## 六、历史问题记录

| 日期 | 问题 | 根因 | 修复 | PR |
|------|------|------|------|-----|
| 06-16 | 发送测试消息 UI 不更新 | sendTest 未添加用户消息 | 添加 setMessages | #40 |
| 06-16 | 视频画面未镜像 | 缺少 scaleX(-1) | Camera 组件添加 style | #40 |
| 06-16 | Netlify tsc 构建失败 | tsconfig 缺 vite/client 类型 | 添加 types | #42 |
| 06-16 | Railway build failed (第一轮) | 根目录 package.json 误检测 | 改 rootDirectory | API 直接改 |
| 06-16 | HTTPS 页面白屏 | ws:// 在 HTTPS 上 SecurityError | 自动检测 wss:// | #45 |
| 06-16 | Netlify 无自动部署 | 站点未关联 Git 仓库 | deploy key + webhook | 手动配置 |
| 06-16 | Railway build failed (第二轮) | nixpacks.toml + runtime.txt 版本冲突? | 待查 | 待定 |
| 06-17 | 前端 WS 地址指向错误 | hostname fallback 指向当前域名 | 改 fallback + 注入 VITE_WS_URL | 待定 |
