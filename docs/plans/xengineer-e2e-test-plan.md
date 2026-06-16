# XEngineer 全真视频通话 E2E 测试计划

> 创建时间: 2026-06-17
> 状态: 规划中

---

## 一、目标

模拟真人从打开页面到完成多轮视频对话的全过程，验证 **VAD → ASR → VLM → LLM → TTS** 每个环节真正跑通。评委看到的是一个完整可用的视频对话系统，不是只检查 UI 元素存不存在。

## 二、现状

### 2.1 前端（Netlify）✅ 已就绪
- 地址: `https://xengineer-frontend.netlify.app`
- 部署: 自动构建已配置（GitHub push → Netlify build hook → 自动部署）
- UI 状态: 页面渲染正常，按钮可点击，视频镜像，无 JS 错误
- 已验证: 18/18 基础自动化测试通过

### 2.2 后端（Railway）⚠️ 需确认
- 服务名: `XEngineer-dev`
- Project: `imaginative-fascination` (`42bfbd0d-03fe-4b50-801c-e83978fe75f3`)
- Environment: `production` (`ed9ce954-227e-4759-a63d-ee16f3631715`)
- Root Directory: 已改为 `xengineer-backend/` ✅
- **未知项:**
  - 后端是否部署成功？（改 rootDirectory 后会触发重新构建）
  - 后端公网域名是什么？（Railway 后台 → Services → XEngineer-dev → Settings → Networking 可查看）
  - 后端是否监听正确的端口（ Railway 通过 `$PORT` 环境变量指定）

### 2.3 关键断裂点 ❌ 必须解决

**前端 WS 地址错误。** 当前代码:
```typescript
// xengineer-frontend/src/hooks/useWebSocket.ts
const WS_URL = import.meta.env.VITE_WS_URL || 
  `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.hostname}:8000/ws`
```

在 Netlify 上，`window.location.hostname` = `xengineer-frontend.netlify.app`，
所以 WS 连的是 `wss://xengineer-frontend.netlify.app:8000/ws`——这是错的，
后端在 Railway 上，不在 Netlify 上。

**修复方案:** 在 Netlify 构建时注入 `VITE_WS_URL` 环境变量，指向 Railway 后端的真实域名。

## 三、待用户确认事项

| # | 问题 | 需要的信息 | 用途 |
|---|------|-----------|------|
| 1 | Railway 后端公网域名 | 类似 `xxx.up.railway.app` 的 URL | 配置前端 WS 连接地址 |
| 2 | 后端是否已部署成功 | Railway 后台的部署日志 | 确认后端可用 |
| 3 | 后端 API key 配置 | 后端需要 VLM/LLM/TTS 的 API key | 确认后端能调用 AI 服务 |

## 四、全链路测试流程（后端通了之后）

### 阶段 1: 环境准备
| 步骤 | 操作 | 验证点 |
|------|------|--------|
| 1.1 | 前端注入 `VITE_WS_URL` → Railway 后端域名 | 构建成功，前端 JS 中 WS 地址正确 |
| 1.2 | 重新部署前端到 Netlify | 线上版本包含正确的 WS 地址 |
| 1.3 | 确认后端健康 | `GET /health` 返回 200 |

### 阶段 2: 页面基础功能
| 步骤 | 操作 | 验证点 |
|------|------|--------|
| 2.1 | 打开 `https://xengineer-frontend.netlify.app` | 页面正常渲染，无白屏 |
| 2.2 | 检查底部状态栏 | 显示"已连接"（WS 连上后端） |
| 2.3 | 检查视频区域 | video 元素存在，有"开启摄像头"按钮 |
| 2.4 | 点击"发送测试消息" | 用户消息出现 + 系统回显消息（WS echo） |
| 2.5 | 检查视频镜像 | `transform: scaleX(-1)` |

### 阶段 3: 虚拟音视频注入
| 步骤 | 操作 | 验证点 |
|------|------|--------|
| 3.1 | 注入虚拟摄像头（canvas 动画 → captureStream） | video 元素有画面 |
| 3.2 | 注入 getUserMedia hook（mock_getusermedia.js） | `window.__mockAudio` 就绪 |
| 3.3 | 注入 PCM 音频数据（15840 samples, ~1s） | `setAudio` + `startFeeding` 成功 |
| 3.4 | 点击录音按钮 | VAD 状态变为 speaking |

### 阶段 4: 对话全链路验证
| 步骤 | 操作 | 验证点 |
|------|------|--------|
| 4.1 | 等待 VAD → ASR 处理（~5s） | 对话区出现用户识别文本（如"你好""介绍"） |
| 4.2 | 等待 LLM + VLM 处理（~10s） | AI 回复流式出现在对话区 |
| 4.3 | 等待 TTS 播放 | 有音频播放指示（播放器状态变化） |
| 4.4 | 截图保存 | 全程截图，可追溯每步 UI 状态 |

### 阶段 5: 多轮对话 + 打断
| 步骤 | 操作 | 验证点 |
|------|------|--------|
| 5.1 | 注入第二段 PCM + 点击录音 | 第二轮用户消息出现 |
| 5.2 | 等待第二轮 AI 回复 | 新的 AI 消息出现在对话区 |
| 5.3 | AI 说话时注入新语音（barge-in） | TTS 停止，新一轮对话开始 |
| 5.4 | 全程无 JS 错误 | console 无 error 级别日志 |

## 五、技术实现要点

### 5.1 虚拟摄像头
```javascript
// canvas 绘制动画 → captureStream() → 替换 video.srcObject
const canvas = document.createElement('canvas');
canvas.width = 640; canvas.height = 480;
const ctx = canvas.getContext('2d');
// 绘制动画帧...
const stream = canvas.captureStream(30);
video.srcObject = stream;
```

### 5.2 虚拟音频
- 使用 `tests/fixtures/mock_getusermedia.js` hook
- PCM 数据来自 `tests/fixtures/test_audio_set.json`（Float32 base64）
- `ScriptProcessorNode` 以实时速率推送音频到 `MediaStreamDestination`

### 5.3 agent-browser 测试脚本
- 使用已有的 `tests/fixtures/` 下的 mock 文件
- 每步截图保存到 `download/netlify-e2e/`
- 最终生成 `result.json` 结构化报告

## 六、前置工作清单

- [ ] 用户确认 Railway 后端域名
- [ ] 确认后端部署成功且健康
- [ ] Netlify 注入 `VITE_WS_URL` 环境变量
- [ ] 重新部署前端
- [ ] 验证 WS 连接正常
- [ ] 编写全链路测试脚本
- [ ] 执行测试并记录结果
- [ ] 修复发现的问题（如有）

## 七、历史问题记录

| 日期 | 问题 | 根因 | 修复 | PR |
|------|------|------|------|-----|
| 06-16 | 发送测试消息 UI 不更新 | sendTest 未添加用户消息 | 添加 setMessages | #40 |
| 06-16 | 视频画面未镜像 | 缺少 scaleX(-1) | Camera 组件添加 style | #40 |
| 06-16 | Netlify tsc 构建失败 | tsconfig 缺 vite/client 类型 | 添加 types | #42 |
| 06-16 | Railway build failed | 根目录 package.json 误检测 | 改 rootDirectory | API 直接改 |
| 06-16 | HTTPS 页面白屏 | ws:// 在 HTTPS 上 SecurityError | 自动检测 wss:// | #45 |
| 06-16 | Netlify 无自动部署 | 站点未关联 Git 仓库 | deploy key + webhook | 手动配置 |
| 06-17 | 前端 WS 地址指向错误 | hostname 默认当前域名 | 需注入 VITE_WS_URL | 待做 |
