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

**核心原则：Agnes优先，火山引擎/NVIDIA补充。**

| 环节 | 模型 | 来源 |
|------|------|------|
| 语音→文字(中文) | 火山引擎 bigmodel_async（双向流式） | 火山引擎 |
| 语音→文字(兜底) | 浏览器原生 SpeechRecognition API | 浏览器内置 |
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
| ASR | 火山引擎 bigmodel_async（浏览器直连WebSocket） |
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
| 火山引擎 流式ASR (bigmodel_async) | `wss://openspeech.bytedance.com` | ✅ 待测 | ⚠️ | 需WebSocket代理或直连 |

> **关键发现（已全面验证）：**
> 1. NVIDIA NIM 托管 API（`integrate.api.nvidia.com`）只有120个文本/视觉/嵌入模型，**语音模型均不在托管API上**
> 2. `nemotron-voicechat` 需**本地Docker部署 + 2张GPU(共128GB+ VRAM)**，不是云端HTTP API
> 3. `z-ai tts` / `z-ai asr` 走Z.ai内部代理（`internal-api.z.ai`），仅开发环境可用，Netlify不可用
> 4. Agnes 3个端点全部公网可访问，Netlify部署后可直接使用
> 5. **火山引擎流式ASR** — 云端WebSocket API，支持中文实时识别，**bigmodel_async模式**首字延迟低、支持VAD分句+热词，完美匹配语音绘图场景
>
> **ASR方案确定：火山引擎 bigmodel_async（双向流式优化版）**
> - 模式：WebSocket二进制流式，200ms分包，VAD 800ms判停
> - 优势：低延迟、支持热词（绘图术语）、支持二遍识别（快+准）
> - 详见 `docs/api/Volcengine-ASR-Streaming.md`

### 7. 题目分析与评委关注点 ✅

**题目二原文核心要求：**
> 用户不能使用鼠标或键盘，仅通过语音指令完成绘图创作。请综合考虑：
> 1. 指令理解的准确性与容错性
> 2. 语音到绘图操作的响应延迟
> 3. 复杂指令的拆解与执行能力

**评委看重的三个维度分析：**

**维度一：指令理解的准确性与容错性**
- 评委想知道：用户说的话能不能被正确理解？说错了系统能不能兜底？
- 不是简单的"画圆"→circle，而是"那个大一点的红色圆形放到右上角"这种自然语言，LLM能不能准确解析
- 容错：同义词识别（"清除"="清空"="擦掉"），模糊指令的智能澄清
- 识别错误时的优雅降级，而不是直接报错或无响应

**维度二：语音到绘图操作的响应延迟**
- 体验的核心指标：说完话到画面变化有多快？
- ASR延迟 + LLM解析延迟 + Canvas渲染延迟，每一层都要快
- ASR流式识别 + LLM流式输出 + Canvas即时渲染，尽量做到说完话1-2秒内看到变化
- AI生图场景可适当放宽（3-5秒可接受），Canvas绘图操作必须快（<1秒体感）

**维度三：复杂指令的拆解与执行能力**
- 拉开差距的关键维度，简单指令谁都能做，复杂拆解才是亮点
- "画一个红色的太阳在左上角，下面画一棵绿色的树" → 多对象 + 各自属性 + 空间位置关系
- LLM需要将自然语言拆解为结构化的操作序列，按顺序执行
- 这是体现AI智能程度的核心，也是作品差异化的关键

**制胜策略判断：**
- 核心不在于Canvas绘图引擎多么强大（评委看的是AI能力不是绘图工具）
- **语音→理解→执行**这条链路的流畅度和智能程度才是灵魂
- **LLM指令解析**是唯一能体现"AI"的地方，是核心投入重点
- Canvas绘图是载体，AI生图是加分项，指令理解才是主体

---

### 1. 产品设计
- [x] 目标用户：创作者/通用用户
- [x] 产品定位：**创意工具** — "用嘴画画"的新交互方式 + AI生图增强
- [ ] UI风格：待定
- [ ] 产品名称：待定
- [ ] 语言支持：待定（中文优先 vs 中英双语）

### 2. 功能范围（MVP边界）
- [x] 方向：从比赛要求出发，72小时可完成的范围内最大化Demo效果
- [ ] 具体功能列表待确定

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
