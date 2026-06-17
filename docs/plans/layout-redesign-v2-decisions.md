# 第二轮 Mockup 决策与编排方案

> 分支: `feat/improve-ui` | 关联 PR: #54
> 关联文档: [`layout-redesign-discussion.md`](./layout-redesign-discussion.md)（第一轮讨论）
> 写作者: main agent | 日期: 2026-06-17
> 状态: **决策已确认，待派 8 个子代理执行**

---

## 1. 用户决策记录

用户已回答第一轮讨论文档 §6 的 5 个开放问题，决策如下：

| 问题 | 用户回答 | 说明 |
|---|---|---|
| Q1 mockup 数量 | **8 个全做** | 2 signature（示波器 + 暗房）× 4 布局 = 8 mockup |
| Q2 可切换方案 | **智能显隐** | AI 说话时字幕自动浮现，3 秒淡出；[💬] 按钮呼出完整历史 |
| Q3 新 signature | **全部实现** | 5 个新 signature 候选全部在 mockup 中实现 |
| Q4 调试模式 | **不需要** | 用 `data-testid` + `ws_debug_client.py` 替代（subagent-R1 报告支持） |
| Q5 对话内容 | **沿用旧的** | "你能看到我吗？"等固定对话，保持一致性 |
| **新增需求** | **必须设计响应式** | 移动端、平板、桌面都要覆盖，详见 §2 |

---

## 2. 响应式设计规范（用户新增需求）

### 2.1 断点定义

采用主流移动优先断点（与 Tailwind 默认对齐）：

| 断点 | 宽度范围 | 设备 | Tailwind 前缀 |
|---|---|---|---|
| **xs** | < 640px | 手机（竖屏） | 默认（无前缀） |
| **sm** | ≥ 640px | 手机（横屏）/ 小平板 | `sm:` |
| **md** | ≥ 768px | 平板（竖屏） | `md:` |
| **lg** | ≥ 1024px | 平板（横屏）/ 小笔记本 | `lg:` |
| **xl** | ≥ 1280px | 桌面 | `xl:` |
| **2xl** | ≥ 1536px | 大桌面 | `2xl:` |

### 2.2 各断点下的布局适配

#### 布局 ①（全屏+浮动字幕）的响应式

| 断点 | 视频区 | AI 字幕条 | 控制条 | 顶部状态栏 |
|---|---|---|---|---|
| xs (<640) | 全屏 | 全宽浮动 + 较小字号 | 全宽 + 5 按钮横排（缩小至 40×40px） | 单行：`● 00:42` + `AI 思考中`（隐藏连接质量） |
| sm-md (640-1023) | 全屏 | 全宽浮动 | 全宽 + 5 按钮横排（48×48px） | 单行 + 连接质量 |
| lg+ (≥1024) | 全屏 | 居中浮动（max-width 800px） | 居中胶囊（max-width 480px） | 双行：状态 + 数据读数 |

#### 布局 ②（大视频+右侧聊天栏）的响应式

| 断点 | 视频:聊天比例 | 聊天栏形态 |
|---|---|---|
| xs (<640) | 100:0（聊天栏隐藏） | 聊天栏变为底部抽屉，上滑呼出 |
| sm-md (640-1023) | 60:40 | 聊天栏始终可见但窄 |
| lg+ (≥1024) | 70:30 | 聊天栏始终可见 |

#### 布局 ③（全屏+可折叠抽屉）的响应式

| 断点 | 默认状态 | 抽屉形态 |
|---|---|---|
| xs (<640) | 视频全屏 | 抽屉变全屏覆盖（点击 [💬] 后整个屏幕是聊天） |
| sm-md (640-1023) | 视频全屏 | 抽屉滑出占 50% 宽度 |
| lg+ (≥1024) | 视频全屏 | 抽屉滑出占 40% 宽度，视频压到 60% |

#### 布局 ④（浮动全功能）的响应式

| 断点 | 浮动卡片 | 控制条 |
|---|---|---|
| xs (<640) | 全宽 + 双层（"你说"+"AI"）合并为单行切换 | 全宽胶囊 + 5 按钮缩小至 40×40px |
| sm-md (640-1023) | 居中（max-width 600px）+ 双层 | 居中胶囊 |
| lg+ (≥1024) | 居中（max-width 800px）+ 双层 | 居中胶囊（max-width 480px） |

### 2.3 移动端控制条设计

移动端控制条必须满足：
- **最小点击目标 44×44px**（iOS HIG + Material Design 推荐）
- **5 个按钮**：摄像头开关 / 麦克风 / 静音 / 截图 / 挂断
- **挂断按钮**与其他按钮间距更大（视觉分隔，红色 `#ef4444`）
- **横屏适配**：横屏时控制条可变为竖向（左侧或右侧）

### 2.4 平板过渡设计

平板（768-1023px）是手机和桌面的过渡，需要特殊处理：
- **布局 ①③④**: 平板与桌面基本一致，仅尺寸略缩
- **布局 ②**: 平板视频:聊天比例从 70:30 调整为 60:40（聊天栏更宽，保证可读性）
- **触控优化**: 平板是触控设备，所有按钮 hover 状态改为 active 状态反馈

### 2.5 mockup 截图要求（响应式覆盖）

每个 mockup 必须出 **3 张截图**（不再是 2 张）：

| 截图 | 尺寸 | 断点 | 用途 |
|---|---|---|---|
| `desktop-1440x900.png` | 1440×900 | xl | 桌面端完整布局 |
| `tablet-768x1024.png` | 768×1024 | md | 平板竖屏 |
| `mobile-375x812.png` | 375×812 | xs | 手机竖屏 |

**8 个 mockup × 3 张截图 = 24 张截图**

---

## 3. 第二轮 Mockup 编排方案

### 3.1 8 个子代理编号

| 子代理 | 布局 | Signature | 输出目录 |
|---|---|---|---|
| subagent-M7 | ① 全屏+浮动字幕 | A 示波器 | `docs/ui-mockups-v2/01-fullscreen-oscilloscope/` |
| subagent-M8 | ① 全屏+浮动字幕 | B 暗房 | `docs/ui-mockups-v2/02-fullscreen-darkroom/` |
| subagent-M9 | ② 大视频+聊天栏 | A 示波器 | `docs/ui-mockups-v2/03-split-oscilloscope/` |
| subagent-M10 | ② 大视频+聊天栏 | B 暗房 | `docs/ui-mockups-v2/04-split-darkroom/` |
| subagent-M11 | ③ 全屏+抽屉 | A 示波器 | `docs/ui-mockups-v2/05-drawer-oscilloscope/` |
| subagent-M12 | ③ 全屏+抽屉 | B 暗房 | `docs/ui-mockups-v2/06-drawer-darkroom/` |
| subagent-M13 | ④ 浮动全功能 | A 示波器 | `docs/ui-mockups-v2/07-floating-oscilloscope/` |
| subagent-M14 | ④ 浮动全功能 | B 暗房 | `docs/ui-mockups-v2/08-floating-darkroom/` |

### 3.2 每个子代理的输出清单

每个子代理输出 **4 个文件**：

```
docs/ui-mockups-v2/<NN>-<layout>-<signature>/
├── mockup.html              # 单文件 HTML+CSS（30-80KB）
├── desktop-1440x900.png     # 桌面端截图
├── tablet-768x1024.png      # 平板截图
└── mobile-375x812.png       # 移动端截图
```

**总计**: 8 × 4 = 32 个文件

### 3.3 每个子代理的 prompt 公共部分

所有 8 个子代理的 prompt 都包含以下公共规范（主代理在派发时统一注入）：

#### A. 布局规范（按布局类型分发）

- **布局 ①（subagent-M7/M8）**: 视频全屏 + 浮动 AI 字幕条（智能显隐）+ 底部浮动控制条 + 顶部浮动状态栏
- **布局 ②（subagent-M9/M10）**: 视频 70%（桌面）/ 60%（平板）/ 100%（手机，聊天栏变底部抽屉）+ 右侧聊天栏 + 底部浮动控制条 + 顶部状态栏
- **布局 ③（subagent-M11/M12）**: 视频全屏默认 + [💬] 按钮呼出右侧抽屉（桌面 40%/平板 50%/手机全屏）+ 浮动 AI 字幕条 + 底部浮动控制条
- **布局 ④（subagent-M13/M14）**: 视频全屏 + 浮动双层卡片（"你说"+"AI"）+ 底部浮动胶囊控制条 + 顶部浮动状态栏（含挂断按钮）

#### B. Signature 规范（按 signature 类型分发）

- **示波器（A，subagent-M7/M9/M11/M13）**:
  - 颜色 tokens: `--surface-0: #0a0a0b` / `--surface-1: #131316` / `--surface-2: #1c1c20` / `--surface-3: #26262c` / `--surface-4: #34343c` / `--brand-500: #c8453c` / `--brand-400: #d65a52` / `--brand-600: #a83a32` / `--scope-cyan: #5eead4`
  - 字体: Noto Serif SC (display) + Noto Sans SC (body) + JetBrains Mono (data)
  - 旧 signature 移植: 取景器十字线（视频四角 L + 中心十字）/ 数据读数条（顶部状态栏）/ 流式光标（朱砂红方块呼吸）
  - 新 signature 实现: VAD 边缘光晕（朱砂红 `#c8453c`）/ 通话计时器（JetBrains Mono `● 00:42`）/ AI 四态指示（IDLE/LISTENING/THINKING/SPEAKING）/ 浮动控制条胶囊（1px 朱砂红边框）/ 用户语音字幕（仅布局④）

- **暗房（B，subagent-M8/M10/M12/M14）**:
  - 颜色 tokens: `--safelight: #7a1f1f` / `--dev-black: #0d0a0a` / `--paper: #f4ead5` / `--silver: #8a8478` / `--developer: #3a2418` / `--red-glow: rgba(122, 31, 31, 0.25)`
  - 字体: Cormorant Garamond (display) + Inter (body) + IBM Plex Mono (data)
  - 旧 signature 移植: 红色 ambient 光晕（左上角径向渐变，overlay 混合）/ 胶片穿孔（视频左右两侧 8 个小方块）/ 流式回复显影动效（blur 8px→0 + opacity 0→1）/ "显影时间"进度（`DEV 12s`）/ 印章式时间戳（红色边框 + mono 字体）
  - 新 signature 实现: VAD 边缘光晕（安全灯红 `#7a1f1f`）/ 通话计时器（IBM Plex Mono `DEV 00:42`）/ AI 四态指示（待显影/曝光中/显影中/已显影）/ 浮动控制条胶囊（暖色调 `rgba(45,24,16,0.6)` + 黄铜边框）/ 用户语音字幕（上层"曝光中"+ 下层"显影中"动效，仅布局④）

#### C. 可切换文字回复方案（智能显隐，所有 8 个 mockup 都实现）

- 默认状态：AI 字幕条隐藏
- AI 开始流式回复时：字幕条自动浮现（300ms 渐显）+ 持续显示
- AI 回复结束 + 3 秒后：字幕条自动淡出
- 用户随时点击 [💬] 按钮：呼出完整对话历史抽屉（布局③本身就是抽屉，其他布局的抽屉为附加层）
- 首次进入应用时显示 2 秒引导提示："点击 [💬] 查看对话历史"
- [💬] 按钮在顶部状态栏始终可见，带未读小红点（有未查看的 AI 回复时）
- AI 字幕条出现时，右下角小提示："点击查看完整对话"

#### D. 响应式要求（所有 8 个 mockup 都实现）

- 断点: xs (<640) / sm-md (640-1023) / lg+ (≥1024)
- 必须出 3 张截图: desktop-1440x900.png / tablet-768x1024.png / mobile-375x812.png
- 移动端控制条按钮最小 44×44px
- 移动端布局见 §2.2 各布局的响应式表

#### E. 对话内容（所有 8 个 mockup 都沿用）

```
USER: 你好，你能看到我吗？
AI: 是的，我能看到你。你戴着一副金属半框眼镜...
SYS: 摄像头已开启
USER: 好的，那你能听到我说话吗？
AI:（流式中，含光标）
```

#### F. 技术规范

- 纯 HTML + 内联 CSS 单文件（`<style>` 标签内）
- 通过 `<link>` 引入 Google Fonts
- 不引入任何 JS 框架，不连真实后端，不调 getUserMedia
- 允许用 CSS animation / keyframes 模拟动效
- 文件大小目标: 30-80KB
- 不 commit / 不 push（主代理统一收集）
- 不修改 XEngineer 仓库的其他文件

### 3.4 子代理执行流程

1. **主代理派发** 8 个子代理并行执行（一条消息 8 个 Task 调用）
2. 每个子代理:
   - 创建目录 `docs/ui-mockups-v2/<NN>-<layout>-<signature>/`
   - 写入 `mockup.html`
   - 用 agent-browser 截图 3 张（桌面 + 平板 + 移动）
   - 验证文件完整性
   - 追加 worklog
   - 返回工作汇报
3. **主代理统一收集** 8 个 mockup 目录
4. **主代理 commit + push** 到 `feat/improve-ui` 分支
5. **主代理在 PR #54 贴评论** 包含 8 张桌面截图供用户挑选

### 3.5 时间预估

- 8 个子代理并行做 mockup: 约 15-25 分钟（每个子代理独立工作，互不阻塞）
- 主代理 push + 贴评论: 约 3-5 分钟
- 总耗时: 约 20-30 分钟

---

## 4. 待用户最终确认

主代理已根据用户对 §6 的回答完成本编排方案，**默认按本方案派 8 个子代理执行**。

如果用户对本方案有任何调整（如响应式断点、子代理编号、输出目录命名等），请在 PR #54 评论里指出。**如无异议，主代理将立即派 8 个子代理开始第二轮 mockup 制作。**

---

## 5. 关联文档

- 第一轮讨论文档: [`layout-redesign-discussion.md`](./layout-redesign-discussion.md)（含问题诊断 / 4 候选布局 / 调试依赖性研究 / signature 演化 / 可切换方案）
- 主计划文档: [`ui-improvement-plan.md`](./ui-improvement-plan.md)
- 前端代码摘要: `docs/ui-research/frontend-structure.md`
- 调试依赖性研究报告: `docs/ui-research/debug-dependency-analysis.md`
- 第一轮 mockup（旧布局）: `docs/ui-mockups/`（A-F 6 个方案，作为 signature 来源）
- 第二轮 mockup（新布局）: `docs/ui-mockups-v2/`（待 8 个子代理创建）
- baseline 截图: `/home/z/my-project/download/ui-baseline/`（本地，不入仓库）
- frontend-design SKILL: `/home/z/my-project/skills/frontend-design/SKILL.md`
