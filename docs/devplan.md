# XEngineer 开发规划

> 状态：讨论中，持续更新
> 最后更新：2026-06-12
> 赛题：第四批次 6.12-6.14（72小时）

---

## 已确定事项

### 1. 选题：题目二 — AI 语音绘图工具 ✅

**决策理由：**
- Agnes 3个模型能用上2个（Text+Image），Video可做Demo素材，利用率最高
- 蓝海赛道，直接竞品极少，差异化空间大（题目一有Pipecat/LiveKit等大量成熟项目）
- 技术栈更轻，无需WebRTC/视频流处理，精力集中在体验打磨
- "用嘴说一句话就生成一幅画"是其他竞品都没有的杀手锏

### 2. 模型方案 ✅

**核心原则：Agnes优先，NVIDIA补充。**

| 环节 | 模型 | 来源 |
|------|------|------|
| 语音→文字(中文) | `nvidia/parakeet-ctc-0_6b-zh-cn` | NVIDIA |
| 语音→文字(兜底) | `openai/whisper-large-v3` | NVIDIA |
| 指令解析/对话 | `agnes-2.0-flash` | Agnes |
| AI生图 | `agnes-image-2.1-flash` | Agnes |
| 设计文档参考 | `agnes-2.0-flash`（Thinking模式） | Agnes |

> 详细模型清单见 `docs/model-selection.md`

### 3. 代码相似度策略 ✅

- **全部手搓，不借鉴开源项目业务代码**
- 不用 `create-next-app` 等CLI工具生成模板，手动建项目
- 题目二核心代码（Canvas绘图引擎、指令解析逻辑、状态管理）均为原创
- API调用代码（fetch Agnes/NVIDIA）属于标准写法，不构成相似度风险
- 第三方库使用需在README中列明依赖
- 规则原文：代码重复率50%以上取消路演资格 + 列入招聘黑名单

### 4. 参赛形式：单人 ✅

### 5. 技术栈 ✅

| 类别 | 选型 |
|------|------|
| 框架 | Next.js 14 + React 18 |
| 语言 | TypeScript |
| 样式 | Tailwind CSS 3 |
| 包管理 | pnpm |
| 绘图 | 原生 Canvas API（手搓） |
| ASR | NVIDIA NIM（浏览器录音 → 后端转发） |
| LLM | Agnes Text API |
| 生图 | Agnes Image API |
| 部署 | GitHub + Netlify |

### 6. 代码仓库策略 ✅

- 独立Git仓库：`/home/z/my-project/XEngineer/`（branch: main）
- GitHub临时仓库：`bigmanBass666/XEngineer-temp`（private）
- `.git/hooks/post-commit` 自动push
- 正式参赛时用 orphan branch 压成1个干净commit推新公开仓库
- commit时间戳必须在6.12-6.14内
- 每个PR只做一件事，描述清晰

---

## 模型连通性验证 ✅

> 测试时间: 2026-06-12

| 模型 | 端点 | 状态 | Netlify可用？ | 备注 |
|------|------|------|-------------|------|
| Agnes Text (agnes-2.0-flash) | `apihub.agnes-ai.com/v1/chat/completions` | ✅ 正常 | ✅ | 公网端点，有key就能用 |
| Agnes Image (agnes-image-2.1-flash) | `apihub.agnes-ai.com/v1/images/generations` | ✅ 正常 | ✅ | 公网端点，~3秒出图 |
| Agnes Video (agnes-video-v2.0) | `apihub.agnes-ai.com/v1/videos` | ✅ 正常 | ✅ | 公网端点，异步轮询 |
| NVIDIA LLM (nemotron-3-super) | `integrate.api.nvidia.com/v1` | ✅ 正常 | ✅ | 公网端点，有key能用 |
| NVIDIA ASR/TTS/voicechat | N/A | ❌ 不可用 | ❌ | 需本地Docker+GPU部署，非云端API |

> **关键发现（已全面验证）：**
> 1. NVIDIA NIM 托管 API（`integrate.api.nvidia.com`）只有120个文本/视觉/嵌入模型，**语音模型均不在托管API上**
> 2. `nemotron-voicechat` 是一个需要**本地Docker部署 + 2张GPU(共128GB+ VRAM)**的模型，不是云端HTTP API
> 3. `z-ai tts` / `z-ai asr` 走Z.ai内部代理（`internal-api.z.ai`），仅开发环境可用，Netlify不可用
> 4. Agnes 3个端点全部公网可访问，Netlify部署后可直接使用
>
> **结论：NVIDIA语音能力（ASR/TTS/voicechat）在Netlify部署场景下完全不可用。**
> **需要替代方案：浏览器原生 Web Speech API 或其他云端ASR/TTS服务。**

### 1. 产品设计 ✅
- [x] 目标用户：创作者/通用用户
- [x] 产品定位：**创意工具** — "用嘴画画"的新交互方式 + AI生图增强
- [x] UI风格：待定（现代简洁，深色/浅色待讨论）
- [x] 产品名称：待定
- [x] 语言支持：待定（中文优先 vs 中英双语待测试ASR后确定）

### 2. 功能范围（MVP边界）
- [x] 方向：从比赛要求出发，72小时可完成的范围内最大化Demo效果
- [ ] 具体功能列表待连通性验证后确定

### 3. 技术细节
- [ ] 指令集设计（支持哪些语音指令？如何拆解复杂指令？）
- [ ] Canvas架构（状态管理、绘图操作抽象、撤销/重做）
- [ ] ASR方案细节（录音方式、分段策略、中文支持）
- [ ] AI生图触发方式（什么指令触发？如何融入绘图流程？）
- [ ] 错误处理与容错（识别错误、网络异常）

### 4. 时间线
- [ ] Day 1（6.12）重点任务
- [ ] Day 2（6.13）重点任务
- [ ] Day 3（6.14）重点任务 + 录Demo视频
- [ ] 24h内提交仓库地址（绑定Netlify）

### 5. 部署
- [ ] 正式GitHub仓库创建时机
- [ ] Netlify绑定

---

## 技术方案（待填充）

*产品设计确认后填写*

---

## 任务拆分（待填充）

*功能范围确定后填写*

---

## 时间线（待填充）

*讨论后填写*
