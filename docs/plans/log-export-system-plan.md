# 日志导出系统功能计划

## 问题描述

移动端音频路由修复已生效（音量键可控制扬声器音量），但真人测试中出现了多个难以描述的异常行为。当前项目日志现状导致无法有效排查：

### 现状痛点

| 痛点 | 说明 |
|------|------|
| **关键业务事件无日志** | ASR 识别结果、VLM 回复内容、VAD 检测开始/结束、音频播放/暂停等核心事件完全没有日志 |
| **日志不结构化** | 全部是纯字符串拼接的 `console.*`，无时间戳、无设备信息、无会话 ID |
| **无法导出** | 浏览器 console 日志随页面关闭即丢失，用户无法导出给开发者分析 |
| **无日志级别控制** | 生产环境也会输出所有 console，且没有 debug/info 级别用于详细调试 |
| **传输成本高** | 用户描述 bug 需要口头转述，信息损失严重 |

### 目标

构建一套**轻量级前端日志导出系统**，让用户在真人测试完成后，可以一键导出包含完整调试信息的日志文件，方便分享给 AI 助手分析问题。

---

## 技术方案设计

### 核心架构

```
┌─────────────────────────────────────────────────┐
│                 LogExportSystem                  │
├─────────────┬───────────────────────────────────┤
│  Logger     │  结构化日志收集器（替代 console.*） │
│  Storage    │  内存环形缓冲区（固定容量）         │
│  Exporter   │  导出为文件 / 推送到 GitHub        │
│  UI         │  导出按钮 + 日志预览面板            │
├─────────────┴───────────────────────────────────┤
│              各模块集成点                         │
│  useWebSocket / useVAD / AudioPlayer            │
│  useAudioSession / App.tsx                      │
└─────────────────────────────────────────────────┘
```

### 方案对比：日志导出目标

| # | 方案 | 用户体验 | 开发成本 | AI 助手获取难度 | 推荐度 |
|---|------|---------|---------|---------------|--------|
| A | 导出为 JSON/文本文件下载 | ⭐⭐ 需上传给 AI | ⭐ 最低 | 需用户手动上传 | 备选 |
| B | 导出为 GitHub Issue（自动创建） | ⭐⭐⭐⭐ 一键完成 | ⭐⭐⭐ 需 GitHub OAuth + API | ⭐⭐⭐⭐ AI 直接读 | ⭐⭐⭐⭐ |
| C | 导出为 GitHub Gist（匿名/公开） | ⭐⭐⭐⭐ 一键完成 | ⭐⭐ 仅需 GitHub Token | ⭐⭐⭐⭐ AI 直接读 | ⭐⭐⭐⭐⭐ |
| D | 复制到剪贴板（文本摘要） | ⭐⭐⭐ 粘贴给 AI | ⭐ 最低 | ⭐⭐⭐⭐⭐ 粘贴即可 | ⭐⭐⭐ |
| E | 上传到后端 WebSocket 通道 | ⭐⭐⭐ 自动上传 | ⭐⭐ 后端需新增端点 | ⭐⭐⭐ 后端存储 | ⭐⭐ |

### 推荐方案：C（GitHub Gist）为主 + A（文件下载）为兜底

**理由**：
1. **GitHub Gist** 是最佳平衡点：一键创建、生成 URL、AI 助手可直接通过 GitHub API 读取内容，无需用户手动上传文件
2. **文件下载** 作为兜底：Gist API 不可用或用户未配置 Token 时，仍可导出文件
3. 用户已经有 GitHub Token（`.env` 中已有 `GITHUB_TOKEN`），可以直接复用

> ⚠️ **安全注意**：日志中可能包含用户语音内容（ASR 转录文本）和 AI 回复内容，不应作为公开 Gist。需使用 **secret Gist**（仅持有链接的人可访问）。

---

## 详细设计

### 1. Logger — 结构化日志收集器

新建 `xengineer-frontend/src/lib/logger.ts`：

```typescript
/**
 * 结构化日志收集器
 *
 * 核心设计：
 * - 替代所有 console.log/warn/error 调用
 * - 每条日志包含：timestamp、level、module、event、data
 * - 支持日志级别过滤（debug/info/warn/error）
 * - 所有日志自动写入内存缓冲区供导出
 */

export interface LogEntry {
  timestamp: number;    // Date.now() 毫秒时间戳
  level: 'debug' | 'info' | 'warn' | 'error';
  module: string;       // 模块标签，如 'WS'、'VAD'、'ASR'、'TTS'、'VLM'、'AudioSession'
  event: string;        // 事件名，如 'connected'、'asr_result'、'tts_play'
  message: string;      // 人类可读描述
  data?: unknown;       // 附加数据（JSON 序列化）
}

// 环上下文：每个会话开始时记录设备/浏览器信息
export interface LogContext {
  sessionId: string;
  userAgent: string;
  platform: string;
  screenWidth: number;
  screenHeight: number;
  language: string;
  startTime: number;
}
```

**日志级别定义**：

| 级别 | 用途 | 示例 |
|------|------|------|
| `debug` | 详细调试信息（开发模式） | VAD 帧数据、WebSocket 帧详情、音频队列状态 |
| `info` | 关键业务事件（默认记录） | 连接成功、ASR 结果、VLM 回复、播放开始/结束、VAD 检测 |
| `warn` | 异常但可恢复 | 连接断开（自动重连中）、音频解码失败、Gist API 失败 |
| `error` | 严重错误 | WebSocket 构造失败、VAD 启动失败、摄像头失败 |

### 2. Storage — 内存环形缓冲区

```typescript
/**
 * 固定容量的环形缓冲区
 *
 * - 最大容量：2000 条（约 10 分钟中等活跃度使用）
 * - 超出容量时自动覆盖最旧日志
 * - 导出时自动注入 LogContext（设备/浏览器信息）
 * - 每条日志同时输出到 console（兼容 DevTools 调试）
 */
```

**容量设计考量**：
- 一次真人测试通常 3-10 分钟
- 中等活跃度约 3-5 条/秒
- 2000 条 ≈ 7-11 分钟，覆盖绝大多数测试场景
- 单条日志平均约 200 字节，2000 条 ≈ 400KB，内存完全可控

### 3. Exporter — 导出器

#### 3a. GitHub Gist 导出（主方案）

```typescript
/**
 * 将日志导出为 Secret GitHub Gist
 *
 * 流程：
 * 1. 从缓冲区收集所有日志
 * 2. 序列化为 JSON（带缩进，可读）
 * 3. 注入 LogContext 头部
 * 4. 调用 GitHub Gist API 创建 secret Gist
 * 5. 返回 Gist URL 供用户分享
 *
 * 注意：
 * - 使用 secret Gist（非公开）
 * - Gist 文件名格式：xengineer-log-{sessionId}-{timestamp}.json
 * - 需要 GitHub Token（已有 GITHUB_TOKEN）
 */
```

**GitHub Gist API**：
```
POST https://api.github.com/gists
Authorization: Bearer {GITHUB_TOKEN}

{
  "description": "XEngineer 前端日志导出",
  "public": false,
  "files": {
    "xengineer-log-{id}-{ts}.json": {
      "content": "{ ... 日志 JSON 内容 ... }"
    }
  }
}
```

#### 3b. 文件下载导出（兜底方案）

```typescript
/**
 * 将日志导出为 JSON 文件下载
 *
 * 流程：
 * 1. 从缓冲区收集所有日志
 * 2. 序列化为 JSON
 * 3. 创建 Blob + Object URL
 * 4. 触发 <a> 标签下载
 *
 * 文件名格式：xengineer-log-{sessionId}-{timestamp}.json
 */
```

#### 3c. 剪贴板摘要导出（快捷方案）

```typescript
/**
 * 生成日志摘要并复制到剪贴板
 *
 * 适合用户快速粘贴到对话框：
 * - 错误日志列表（error 级别的全部日志）
 * - 关键事件时间线（连接、ASR、VLM、播放等）
 * - 设备信息
 * - 总条数统计
 *
 * 格式：紧凑 Markdown 表格 + 详细错误信息
 */
```

### 4. UI — 导出控制面板

新建 `xengineer-frontend/src/components/LogExportPanel.tsx`：

```
┌──────────────────────────────────────┐
│  📋 Debug Panel           [折叠/展开] │
├──────────────────────────────────────┤
│  Session: abc123   Logs: 347/2000    │
│  Duration: 2m 15s                    │
│                                      │
│  [📋 Copy Summary]  [⬇️ Download]  │
│  [📤 Export to Gist]                │
│                                      │
│  Gist URL: (导出后显示)              │
│  ┌────────────────────────────────┐  │
│  │ https://gist.github.com/xxx   │  │
│  └────────────────────────────────┘  │
│                                      │
│  ── 最近 20 条日志 ──                │
│  12:30:01 [INFO] [WS] Connected     │
│  12:30:02 [INFO] [ASR] Result: "你好"│
│  12:30:03 [INFO] [VLM] Reply: "..."  │
│  12:30:04 [WARN] [TTS] Decode error │
│  ...                                 │
└──────────────────────────────────────┘
```

**设计考量**：
- 默认折叠，不干扰正常使用
- 可通过某种手势（如连续点击版本号 3 次）或 URL 参数 `?debug=true` 打开
- 三个导出按钮：剪贴板摘要（最快捷）、文件下载（兜底）、Gist 导出（最完整）
- 最近 20 条日志的实时预览（info 以上级别）
- Gist URL 导出后可一键复制

### 5. 各模块日志集成点

需要新增日志的关键事件（当前完全缺失的）：

#### 5a. `useWebSocket.ts`

| 事件 | 级别 | 附加数据 |
|------|------|---------|
| 发送消息 | `debug` | `{ type, payload 摘要 }` |
| 收到消息 | `debug` | `{ type, payload 摘要 }` |
| 收到 ASR 结果 | `info` | `{ text, final }` |
| 收到 VLM 回复 | `info` | `{ text }` |
| 收到 TTS chunk | `debug` | `{ index, size }` |
| 连接成功 | `info` | `{ url }` |
| 连接断开 | `warn` | `{ code, reason }` |
| 重连尝试 | `warn` | `{ attempt, delay }` |

#### 5b. `useVAD.ts`

| 事件 | 级别 | 附加数据 |
|------|------|---------|
| VAD 启动 | `info` | `{ sampleRate, frameSize }` |
| 检测到语音开始 | `info` | `{ timestamp }` |
| 检测到语音结束 | `info` | `{ duration }` |
| VAD 停止 | `info` | — |
| 处理帧 | `debug` | `{ volume, energy }` |

#### 5c. `AudioPlayer.tsx`

| 事件 | 级别 | 附加数据 |
|------|------|---------|
| 入队 chunk | `debug` | `{ index, size }` |
| 开始播放 | `info` | — |
| 播放结束 | `info` | `{ reason: 'complete' | 'barge-in' }` |
| barge-in 中断 | `info` | `{ playedChunks, pendingChunks }` |
| 解码错误 | `error` | `{ error }` |
| 队列状态 | `debug` | `{ pending, playing }` |

#### 5d. `App.tsx`

| 事件 | 级别 | 附加数据 |
|------|------|---------|
| 会话初始化 | `info` | `{ sessionId, deviceInfo }` |
| 发送用户消息 | `info` | `{ text }` |
| 收到 AI 回复 | `info` | `{ text }` |
| barge-in 触发 | `info` | — |
| 消息列表更新 | `debug` | `{ count }` |

#### 5e. `useAudioSession.ts`

| 事件 | 级别 | 附加数据 |
|------|------|---------|
| 初始化 | `info` | `{ platform, type }` |
| 切换 playback | `info` | — |
| 切换 play-and-record | `info` | — |
| 切换失败 | `warn` | `{ error }` |

---

## 修改文件清单

| 文件 | 改动类型 | 说明 |
|------|---------|------|
| `xengineer-frontend/src/lib/logger.ts` | **新建** | 结构化日志收集器 + 环形缓冲区 |
| `xengineer-frontend/src/lib/logExporter.ts` | **新建** | 导出器（Gist / 文件 / 剪贴板） |
| `xengineer-frontend/src/components/LogExportPanel.tsx` | **新建** | 导出 UI 面板 |
| `xengineer-frontend/src/hooks/useWebSocket.ts` | 修改 | 替换 console.* 为 logger，补充关键事件日志 |
| `xengineer-frontend/src/hooks/useVAD.ts` | 修改 | 替换 console.* 为 logger，补充 VAD 检测事件日志 |
| `xengineer-frontend/src/components/AudioPlayer.tsx` | 修改 | 替换 console.* 为 logger，补充播放生命周期日志 |
| `xengineer-frontend/src/hooks/useAudioSession.ts` | 修改 | 替换 console.* 为 logger |
| `xengineer-frontend/src/hooks/useCamera.ts` | 修改 | 替换 console.* 为 logger |
| `xengineer-frontend/src/App.tsx` | 修改 | 初始化 Logger 注入设备信息，集成 LogExportPanel |

---

## 导出日志格式示例

```json
{
  "meta": {
    "sessionId": "abc123def456",
    "exportTime": "2026-06-18T15:30:00.000Z",
    "device": {
      "userAgent": "Mozilla/5.0 (Linux; Android 14; ...) Chrome/126.0.0.0",
      "platform": "Android",
      "screenWidth": 1080,
      "screenHeight": 2400,
      "language": "zh-CN"
    },
    "stats": {
      "totalLogs": 347,
      "duration": 135000,
      "levelCounts": { "debug": 180, "info": 142, "warn": 20, "error": 5 }
    }
  },
  "logs": [
    {
      "t": 1718700600000,
      "level": "info",
      "module": "WS",
      "event": "connected",
      "msg": "WebSocket 连接成功",
      "data": { "url": "wss://..." }
    },
    {
      "t": 1718700601500,
      "level": "info",
      "module": "ASR",
      "event": "result",
      "msg": "ASR 识别结果 (final)",
      "data": { "text": "你好" }
    },
    {
      "t": 1718700603000,
      "level": "info",
      "module": "VLM",
      "event": "reply",
      "msg": "VLM 回复",
      "data": { "text": "你好！有什么可以帮你的？" }
    },
    {
      "t": 1718700604500,
      "level": "info",
      "module": "TTS",
      "event": "play_start",
      "msg": "TTS 开始播放",
      "data": { "chunks": 12 }
    },
    {
      "t": 1718700608000,
      "level": "info",
      "module": "VAD",
      "event": "speech_start",
      "msg": "检测到用户开始说话",
      "data": {}
    },
    {
      "t": 1718700608100,
      "level": "info",
      "module": "TTS",
      "event": "barge_in",
      "msg": "Barge-in 中断 TTS 播放",
      "data": { "playedChunks": 6, "pendingChunks": 6 }
    }
  ]
}
```

---

## 风险评估

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| 日志缓冲区占用内存过大 | 低端设备可能卡顿 | 固定 2000 条上限 + 环形覆盖；2000 × ~200B ≈ 400KB，可接受 |
| GitHub Token 暴露在前端代码中 | Token 泄露风险 | 使用只读 scope 的 Personal Access Token；或通过后端代理创建 Gist |
| Gist API 限流 | 导出失败 | 兜底到文件下载；GitHub API 限流为 5000 次/小时，足够使用 |
| Secret Gist URL 可被猜测 | 日志可能被第三方读取 | Gist URL 包含随机 ID，不可枚举；日志不含敏感个人信息（仅 ASR 转录文本） |
| 生产环境日志量过大 | 影响性能 | 默认仅记录 info 级别以上；debug 级别需通过 `?debug=true` 开启 |
| iOS Safari 上 clipboard API 受限 | 剪贴板导出可能失败 | 捕获异常，提示用户使用文件下载替代 |

---

## 实施步骤

### Step 1：新建 `logger.ts` — 结构化日志收集器
- 定义 `LogEntry`、`LogContext` 类型
- 实现 `Logger` 类（环形缓冲区 + 级别过滤 + console 输出）
- 导出全局单例 `logger` 实例

### Step 2：新建 `logExporter.ts` — 导出器
- 实现 Gist 导出（POST /gists API）
- 实现文件下载（Blob + a.click()）
- 实现剪贴板摘要（navigator.clipboard.writeText）

### Step 3：新建 `LogExportPanel.tsx` — UI 面板
- 折叠/展开面板
- 导出按钮（剪贴板 / 下载 / Gist）
- 最近 20 条日志预览
- Gist URL 显示 + 复制

### Step 4：改造现有模块日志
- 逐个文件替换 `console.*` 为 `logger.*`
- 补充所有缺失的关键事件日志

### Step 5：App.tsx 集成
- 初始化 Logger + 注入 LogContext
- 挂载 LogExportPanel

### Step 6：测试 + 部署
- 本地构建验证
- 部署到 Netlify
- 真人测试日志导出流程

---

## 讨论点

以下是需要在实施前确认的设计决策：

1. **GitHub Token 放在前端还是通过后端代理？**
   - 前端直传：简单，但 Token 暴露在前端 bundle 中（可被逆向）
   - 后端代理：安全，但需新增 WebSocket 消息类型 + 后端处理逻辑

2. **日志默认级别？**
   - 选项 A：生产环境默认 `info`（含关键业务事件），开发/调试模式 `debug`
   - 选项 B：生产环境默认 `warn`（仅警告和错误），需要通过 `?debug=true` 或点击调试面板才开启 `info`

3. **LogExportPanel 触发方式？**
   - 选项 A：固定显示在页面底部（始终可见）
   - 选项 B：URL 参数 `?debug=true` 触发显示
   - 选项 C：隐藏手势（如长按 Logo 3 秒）触发
   - 选项 D：专用调试页面 `/debug`

4. **是否需要日志上传到后端存储？**
   - 优点：AI 助手可以直接通过后端 API 读取，无需依赖 GitHub Gist
   - 缺点：需要后端新增存储端点，增加系统复杂度

5. **环形缓冲区容量？**
   - 当前设计：2000 条
   - 可选：1000 条 / 2000 条 / 5000 条
