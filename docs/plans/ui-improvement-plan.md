# XEngineer UI 改造计划

> 分支: `feat/improve-ui` | 基线: main `5f06fcb`
> 依据:
> - 设计原则: `/home/z/my-project/skills/frontend-design/SKILL.md`（anthropics frontend-design）
> - 代码现状: `docs/ui-research/frontend-structure.md`（subagent-D 摘要）
> - 视觉现状: `/home/z/my-project/download/ui-baseline/`（7 张 baseline 截图）
> 写作者: main agent | 日期: 2026-06-17

---

## 0. 一页速览

| 维度 | 当前 | 目标 |
|---|---|---|
| 设计识别度 | Vite+Tailwind 默认外观，零品牌识别 | 第一眼能记住的"AI 视觉对话"产品 |
| 设计 tokens | 0 个 | 完整 token 系统（颜色/字体/间距/动效） |
| 字体 | 系统默认无衬线 | 思源宋体（display）+ 思源黑体（body）+ JetBrains Mono（数据） |
| 主色 | blue-600 | 朱砂红 #C8453C（signature 色，详见 §2） |
| 响应式 | 硬编码 w-1/2，移动端不可用 | sm/md/lg/xl 完整断点 |
| 动效 | 4 处基础 Tailwind animate | framer-motion 编排的呼吸/进入/状态切换动效 |
| PR 拆分 | — | 4 个 PR：tokens / signature / 组件层 / 动效 |

---

## 1. 设计简报 (Brief)

### 1.1 产品定位

**XEngineer 是一个"AI 视觉对话助手"** —— 用户对着摄像头说话，AI 同时看到画面、听到声音、流式回复文字 + 语音。

**一句话本质**: 让 AI 同时拥有"眼睛"和"耳朵"，与人类进行多模态实时对话。

### 1.2 受众

- 比赛/演示评委（关注"这东西做得很认真"）
- 技术爱好者（关注"我能不能上手用"）
- 潜在用户（关注"这跟我用过的 ChatGPT 有什么不一样"）

### 1.3 页面单一职责

**让用户在 5 秒内理解"我能对着镜头和 AI 说话"这件事，并被勾起试一试的冲动。**

### 1.4 必须避开的三个 AI 模板默认（SKILL.md 明文警示）

- ❌ warm cream background + serif display + terracotta accent（warm-editorial 模板）
- ❌ near-black background + acid-green or vermilion accent（tech-bro dark 模板）
- ❌ broadsheet-style + hairline rules + zero border-radius（newspaper 模板）

> **本次改造会主动避开上述三个默认**，但允许从其中一个出发做"反方向"演化（见 §2 signature 论证）。

---

## 2. Signature 设计：从产品本质出发的视觉概念

### 2.1 设计推理

按 SKILL.md "Ground it in the subject" 原则，从 XEngineer 自身世界取材：

| 产品元素 | 视觉转化 |
|---|---|
| 摄像头 = AI 的眼睛 | 取景框、扫描线、画面识别反馈 |
| 麦克风 = AI 的耳朵 | 声波纹、能量环、说话脉动 |
| 流式回复 = AI 在思考并说 | 字符渐显、光标呼吸、TTS 波形 |
| 双模态同时进行 | 左右分屏的"视觉/听觉"两套视觉语言并存 |
| 工程感（XEngineer） | 等宽字体的数据展示、坐标刻度、技术读数 |

### 2.2 选定 Signature 概念：「示波器 / Oscilloscope」

**核心隐喻**: 整个界面像一台科学仪器/示波器面板 —— 摄像头是输入探头、对话流是波形读数、AI 回复是信号解码结果。

**为什么不是 AI 模板默认**:
- 不是 cream+serif（我们用工程灰 + 朱砂红）
- 不是 black+acid-green（朱砂红 #C8453C 不是 acid-green/vermilion 那种荧光感，是更哑光的氧化铁红）
- 不是 broadsheet（保留圆角和呼吸感，不是冷峻的零圆角报纸排版）

**为什么是"示波器"**:
- 与"AI 视觉对话"的"仪器感"高度契合
- 工程师/技术评委一眼能 get 到"这不是套模板"
- 取景框、波形、刻度、读数 —— 这些元素都有功能来源（不是装饰）
- 与产品名 "XEngineer" 中的 "Engineer" 一脉相承

### 2.3 Signature 元素清单（每个都是"会被记住的一处"）

| # | 元素 | 位置 | 实现要点 |
|---|---|---|---|
| 1 | **取景器十字线** | Camera 视频四角 + 中心十字 | 四个 L 形角标 + 中心十字 hairline，跟随 VAD speaking 时变朱砂红 + 微闪 |
| 2 | **示波器波形** | 录音按钮上方 | 替代当前"绿色脉冲点"，用 32 根条形柱实时显示 RMS 能量，silent 时低幅基线噪声 + speaking 时大幅波动 |
| 3 | **数据读数条** | Header 右侧 | 等宽字体显示 `WS ● / VAD ● / 24kHz / 16kHz` 这种技术参数读数，像示波器面板右上角的状态灯组 |
| 4 | **流式回复"信号解码"动效** | StreamingMessage | 文字以"解码"方式逐字渐显（不透明度 0.3 → 1，每字错开 30ms），配合左侧朱砂红光标呼吸 |
| 5 | **背景网格** | 整页底层 | 极淡的 40px×40px hairline 网格（#1a1a1a / 5% 透明度），暗示"测量环境" |

### 2.4 设计风险声明（SKILL.md 要求 take one risk you can justify）

**风险**: 选择"示波器/仪器"隐喻可能让产品显得过于技术化，劝退非技术用户。

**论证**:
- 目标受众是技术评委 + 技术爱好者（§1.2），"仪器感"反而是加分项
- 比赛场景需要"被记住"，仪器面板比"另一个 ChatGPT-like 聊天 UI"更有记忆点
- 示波器元素都是功能性的（取景框/波形/读数），不是纯装饰，符合 SKILL.md "Structure is information" 原则
- 风险可在后续通过"语气文案"（如 empty state 用更友好的引导语）部分抵消

---

## 3. 设计 Token 系统

### 3.1 颜色 Token

```css
:root {
  /* === Surface (工程灰梯度) === */
  --surface-0: #0a0a0b;       /* 最底层背景（比 gray-900 更冷） */
  --surface-1: #131316;       /* 主面板背景 */
  --surface-2: #1c1c20;       /* 次级面板（header / footer / 气泡 AI） */
  --surface-3: #26262c;       /* 边框 / 分隔线 / hover */
  --surface-4: #34343c;       /* 强调边框 / active */

  /* === Text === */
  --text-primary: #f5f5f7;    /* 主文字 */
  --text-secondary: #a1a1a8;  /* 次文字 */
  --text-tertiary: #6b6b73;   /* 三级文字（读数/标签） */
  --text-inverse: #0a0a0b;    /* 反白文字 */

  /* === Brand (朱砂红 - signature) === */
  --brand-500: #c8453c;       /* 主 brand 色 */
  --brand-400: #d65a52;       /* hover/active */
  --brand-600: #a83a32;       /* pressed */
  --brand-glow: rgba(200, 69, 60, 0.35); /* 发光阴影 */

  /* === Functional === */
  --accent-success: #4ade80;  /* VAD speaking / 连接成功 */
  --accent-warning: #fbbf24;  /* WS connecting */
  --accent-danger: #ef4444;   /* 错误 */

  /* === Technical (示波器风格) === */
  --grid-line: rgba(255, 255, 255, 0.04); /* 背景网格线 */
  --scope-cyan: #5eead4;      /* 示波器副色（用于读数/刻度，与朱砂红互补） */
  --scope-amber: #fbbf24;     /* 示波器琥珀色（用于警告读数） */
}
```

**论证**:
- 朱砂红 `#C8453C` 取自氧化铁红（不是 acid-red / vermilion 荧光感），与示波器/工程仪器的历史配色一脉相承
- 工程灰梯度（surface-0 到 surface-4）比 Tailwind gray 更冷一点（带轻微蓝紫偏移），区分于"普通深色主题"
- 引入 `--scope-cyan` 作为副色：示波器传统读数为青色/绿色，与朱砂红形成补色对比，用于数据读数视觉分层

### 3.2 字体 Token

```css
:root {
  /* Display - 思源宋体（标题/品牌字/大字） */
  --font-display: 'Noto Serif SC', 'Source Han Serif SC', 'STSong', serif;

  /* Body - 思源黑体（正文/对话/按钮） */
  --font-body: 'Noto Sans SC', 'Source Han Sans SC', -apple-system, BlinkMacSystemFont, sans-serif;

  /* Mono - JetBrains Mono（数据读数/技术参数/状态指示） */
  --font-mono: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace;
}
```

**字体加载**: 通过 `index.html` 的 `<link>` 引入 Google Fonts:
- Noto Serif SC: weights 400/700
- Noto Sans SC: weights 400/500/700
- JetBrains Mono: weights 400/500

**字体角色**:
| 场景 | 字体 | 字重 | 字号 |
|---|---|---|---|
| Header logo "XEngineer" | Noto Serif SC | 700 | 20px，字距 0.15em |
| Hero 大标题（空状态） | Noto Serif SC | 700 | 36px |
| 副标题 / 引导语 | Noto Sans SC | 400 | 16px |
| 对话气泡内容 | Noto Sans SC | 400 | 14px |
| 按钮 / 标签 | Noto Sans SC | 500 | 13px |
| 状态读数 / 技术参数 | JetBrains Mono | 500 | 11px |
| 时间戳 / ID | JetBrains Mono | 400 | 11px |

### 3.3 间距 / 圆角 / 阴影 Token

```css
:root {
  /* 间距（4px 基准） */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-6: 24px;
  --space-8: 32px;
  --space-12: 48px;

  /* 圆角（仪器风格偏小圆角） */
  --radius-sm: 2px;   /* 按钮 / 标签 */
  --radius-md: 4px;   /* 气泡 / 卡片 */
  --radius-lg: 8px;   /* 大面板 */
  --radius-pill: 9999px;

  /* 阴影 */
  --shadow-panel: 0 1px 0 rgba(255,255,255,0.04) inset, 0 4px 12px rgba(0,0,0,0.3);
  --shadow-brand-glow: 0 0 24px var(--brand-glow);

  /* 边框 */
  --border-hairline: 1px solid var(--surface-3);
  --border-brand: 1px solid var(--brand-500);
}
```

### 3.4 动效 Token

```css
:root {
  --ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1);
  --ease-in-out-circ: cubic-bezier(0.85, 0, 0.15, 1);

  --dur-fast: 150ms;      /* hover / press */
  --dur-base: 250ms;      /* 状态切换 */
  --dur-slow: 500ms;      /* 进入动效 */
  --dur-sig: 1200ms;      /* signature 呼吸/扫描 */
}
```

### 3.5 Tailwind 配置同步

在 `tailwind.config.js` 的 `theme.extend` 中映射上述 CSS 变量为 Tailwind utility classes:

```js
theme: {
  extend: {
    colors: {
      'surface': {
        0: 'var(--surface-0)',
        1: 'var(--surface-1)',
        2: 'var(--surface-2)',
        3: 'var(--surface-3)',
        4: 'var(--surface-4)',
      },
      'brand': {
        400: 'var(--brand-400)',
        500: 'var(--brand-500)',
        600: 'var(--brand-600)',
      },
      // ... 其他 token
    },
    fontFamily: {
      display: 'var(--font-display)',
      body: 'var(--font-body)',
      mono: 'var(--font-mono)',
    },
    // ... radius / spacing / animation
  }
}
```

**好处**: 后续组件代码可直接用 `bg-surface-1` `text-brand-500` `font-mono` `text-[11px]` 等语义化 class，不再硬编码 hex。

---

## 4. 组件级改造清单

> 标注说明: 🔴=breaking change / 🟡=视觉变化 / 🟢=新增 / ⚙️=纯样式调整

### 4.1 全局层

| # | 改造点 | 类型 | 描述 |
|---|---|---|---|
| G1 | `src/index.css` 重写 | ⚙️ | 写入 §3 全部 CSS 变量；body 字体改为 `var(--font-body)`；背景改为 `var(--surface-0)` |
| G2 | `tailwind.config.js` 重写 | ⚙️ | 按 §3.5 把 CSS 变量映射到 Tailwind utility |
| G3 | `index.html` 引入字体 | 🟢 | `<link>` Google Fonts: Noto Serif SC + Noto Sans SC + JetBrains Mono |
| G4 | 引入新依赖 | 🟢 | `lucide-react`（图标库，替换内联 SVG）/ `framer-motion`（动效库） |
| G5 | 背景网格组件 | 🟢 | `<ScopeGrid />` 全屏 fixed 层，渲染 40×40 hairline 网格 |

### 4.2 App.tsx 布局层

| # | 改造点 | 类型 | 描述 |
|---|---|---|---|
| A1 | 响应式断点 | 🔴 | 左右双栏 `w-1/2` → `flex flex-col md:flex-row`，移动端纵向堆叠（摄像头在上 / 对话在下）；左右栏比例 `md:w-1/2` → `lg:w-[480px] xl:w-[520px]`（左栏固定宽度，右栏 flex-1） |
| A2 | Header 高度增加 | 🟡 | `h-12` → `h-14`，容纳数据读数条 |
| A3 | 整体容器 padding | 🟡 | 外层加 `p-3 md:p-4`，让面板有"悬浮在网格背景上"的层次感 |
| A4 | VAD 链路保护 | 🔴 | 不改 `handleVADStateChange` 逻辑，仅改 UI 触发点（按钮/状态显示）。建议在本 PR 暂不抽 `useConversationOrchestrator` hook，避免功能回归风险，留作后续重构 |

### 4.3 Header 组件（在 App.tsx 内，可考虑抽 `<Header />`）

| # | 改造点 | 类型 | 描述 |
|---|---|---|---|
| H1 | Logo 重设计 | 🟢 | 28px 蓝方块 → 24×24 SVG（朱砂红描边的取景框图标 + 内嵌十字线）；标题 "XEngineer" 用 `font-display font-bold tracking-[0.15em] text-[20px]` |
| H2 | 副标题 | 🟢 | 标题下加 1 行 `text-[11px] font-mono text-tertiary`：`AI VISION CONVERSATION ASSISTANT` |
| H3 | 右侧数据读数条 | 🟢 | `font-mono text-[11px]` 显示 4 个状态读数：`WS ●` / `VAD ●` / `24kHz` / `v0.1.0`，状态点颜色根据 connectionStatus/VADStatus 动态变化 |
| H4 | 底部 hairline | 🟡 | `border-b border-gray-700` → `border-b border-surface-3` + 加 1px 朱砂红渐变线（仅 header 底部中央 40% 宽度，作 signature 装饰） |

### 4.4 Camera.tsx

| # | 改造点 | 类型 | 描述 |
|---|---|---|---|
| C1 | 视频边框取景器 | 🟢 | 视频容器加 4 个 L 形角标（绝对定位，朱砂红 1.5px 描边，尺寸 16×16px） + 中心十字 hairline（`mix-blend-mode: difference` 让其在任何画面上都可见） |
| C2 | VAD speaking 时取景框动效 | 🟢 | speaking 状态下 4 个 L 角标从朱砂红 `#C8453C` 闪烁到亮红 `#FF6B5C`，1.2s 周期；十字线变粗 1.5px → 2px |
| C3 | 关闭状态占位 | 🟡 | 当前 `bg-gray-800` → 加 SVG "摄像头未开启" 图标（lucide `Camera` + 斜杠）+ 居中提示文字 |
| C4 | 开启/关闭按钮位置 | 🟡 | 从视频框内蓝色覆盖 → 视频框下方 `font-mono text-[11px]` 工程风按钮（开/关两种状态切换，类似仪器开关） |
| C5 | 截图闪光特效保留 | ⚙️ | 保留当前白色闪光逻辑，但时长从当前值调整到 200ms，配色用纯白 |

### 4.5 AudioRecorder.tsx（重大改造 - signature 元素 #2）

| # | 改造点 | 类型 | 描述 |
|---|---|---|---|
| R1 | 示波器波形可视化 | 🟢 | 替换当前"绿色脉冲点"，新增 32 根条形柱波形（高 48px，宽 2px，gap 2px）。silent 时低幅基线噪声动画（4-8px），speaking 时随 RMS 能量动态高度（8-44px）。颜色 `--brand-500` |
| R2 | 录音按钮重设计 | 🟡 | 当前 emerald/red 大按钮 → 工程风按钮：默认态 `border border-surface-4 text-secondary`，active 态 `bg-brand-500 text-white shadow-brand-glow`。文案 "● REC" / "■ STOP"，用 `font-mono text-[13px]` |
| R3 | 错误提示重设计 | 🟡 | 当前裸红字 → 容器化：`bg-accent-danger/10 border border-accent-danger/30 rounded-sm px-3 py-2`，前面加 lucide `AlertCircle` 图标，文字用 `font-body text-[12px]`，加可关闭 X |
| R4 | 状态文案 | ⚙️ | "静音" / "正在说话" / "检测到声音" → 用 `font-mono text-[11px]` 大写：`SILENT` / `SPEAKING` / `DETECTED` |

### 4.6 ChatBubble.tsx + StreamingMessage.tsx

| # | 改造点 | 类型 | 描述 |
|---|---|---|---|
| B1 | 消息角色标签 | 🟢 | 每条消息顶部加 `font-mono text-[10px] tracking-wider text-tertiary` 角色标签：`USER` / `AI` / `SYS`，替代当前靠颜色区分 |
| B2 | 时间戳 | 🟢 | 消息底部加 `font-mono text-[10px] text-tertiary` 时间戳 `HH:MM:SS` |
| B3 | User 气泡 | 🟡 | `bg-blue-600` → `bg-brand-500 text-white`，圆角 `rounded-br-sm` 保留（对话方向感） |
| B4 | AI 气泡 | 🟡 | `bg-gray-700` → `bg-surface-2 border border-surface-3`，圆角 `rounded-bl-sm` 保留 |
| B5 | System 气泡 | 🟡 | 居中卡片 `bg-surface-2/50 border border-surface-3 rounded-md` + 左侧朱砂红 2px 竖条 |
| B6 | StreamingMessage 光标 | 🟡 | `bg-blue-400 animate-pulse` → 朱砂红方块光标 `bg-brand-500` + framer-motion 呼吸动画（opacity 0.4 → 1，800ms） |
| B7 | 流式文字渐显动效 | 🟢 | 每个新增字符以 opacity 0.3 → 1 渐显，错开 30ms（用 framer-motion 的 `motion.span` + `key` 实现） |

### 4.7 StatusBar.tsx

| # | 改造点 | 类型 | 描述 |
|---|---|---|---|
| S1 | 重设计为"读数面板" | 🟢 | 整体改成 `font-mono text-[11px]` 读数风格，4-6 个分组读数用 `│` 分隔：`WS:CONNECTED │ VAD:SILENT │ AI:IDLE │ 24kHz │ v0.1.0` |
| S2 | AI 处理中读数 | 🟡 | 当前 spinner → 文字 `AI:THINKING` + 朱砂红 `animate-pulse` 圆点，配 `font-mono` |
| S3 | 音频播放指示 | 🟡 | 当前 4 根 bounce 波形 → 4 根朱砂红波形（保留动画逻辑，换色） |
| S4 | 状态点颜色映射 | ⚙️ | `ConnectionStatus` → 颜色映射：connected=success / connecting=warning / disconnected=tertiary / error=danger |

### 4.8 空状态 hero（新增，signature 元素 #4）

| # | 改造点 | 类型 | 描述 |
|---|---|---|---|
| E1 | 空状态组件抽出 | 🟢 | 新建 `<EmptyHero />` 组件，当 messages.length === 0 时渲染到右栏对话区 |
| E2 | Hero 大标题 | 🟢 | `font-display font-bold text-[36px] text-text-primary`："开始和 AI 视觉对话" |
| E3 | 副标题 | 🟢 | `font-body text-[16px] text-text-secondary`："打开摄像头，按下录音键，AI 同时看到你、听到你、回应你" |
| E4 | 引导箭头 | 🟢 | framer-motion 动画箭头从右栏指向左栏录音按钮位置（移动端改为向下指） |
| E5 | 能力卡片（可选） | 🟢 | 3 个小卡片横排展示能力：`看见` / `听见` / `流式回应`，每个卡片配 lucide 图标 + 1 行说明 |

---

## 5. PR 拆分计划

> 依据 worklog 红线："每个 PR 只做一件事" + "PR 需含标题/功能描述/实现思路/测试方式"

### PR #1: 基础层 - Design Tokens + 字体 + 依赖

**分支**: `feat/ui-tokens`（从 `feat/improve-ui` 切出）

**包含改造点**: G1, G2, G3, G4, G5

**改动文件**:
- `xengineer-frontend/package.json`（加 lucide-react + framer-motion）
- `xengineer-frontend/index.html`（加字体 link）
- `xengineer-frontend/src/index.css`（重写，加全部 CSS 变量）
- `xengineer-frontend/tailwind.config.js`（重写 theme.extend）
- `xengineer-frontend/src/components/ScopeGrid.tsx`（新建）
- `xengineer-frontend/src/App.tsx`（仅在根容器引入 ScopeGrid）

**验证方式**:
- `npm run build` 通过
- dev server 启动后页面颜色从 blue-600 → 朱砂红渐变（虽然多数组件还在用旧 class，但 body 背景和字体已变）
- 截图对比 baseline

**不包含**: 任何组件级视觉改造（避免一个 PR 太大）

### PR #2: Signature 层 - Header + 空状态 Hero

**分支**: `feat/ui-signature`（基于 PR #1 合并后）

**包含改造点**: A2, A3, H1, H2, H3, H4, E1, E2, E3, E4, E5

**改动文件**:
- `xengineer-frontend/src/App.tsx`（Header 区域重写 + 引入 EmptyHero）
- `xengineer-frontend/src/components/Header.tsx`（新建，从 App.tsx 抽出）
- `xengineer-frontend/src/components/EmptyHero.tsx`（新建）

**验证方式**:
- `npm run build` 通过
- 首屏截图：Header 显示朱砂红 logo + 数据读数条 + 空状态 hero 大字标题
- WS 连接状态正常（数据读数条 `WS:CONNECTED` 正确显示）

**不包含**: Camera/Recorder/ChatBubble 改造

### PR #3: 组件层 - Camera + Recorder + ChatBubble + StatusBar

**分支**: `feat/ui-components`（基于 PR #2 合并后）

**包含改造点**: C1-C5, R1-R4, B1-B7, S1-S4

**改动文件**:
- `xengineer-frontend/src/components/Camera.tsx`
- `xengineer-frontend/src/components/AudioRecorder.tsx`
- `xengineer-frontend/src/components/ChatBubble.tsx`
- `xengineer-frontend/src/components/StreamingMessage.tsx`
- `xengineer-frontend/src/components/StatusBar.tsx`
- `xengineer-frontend/src/App.tsx`（仅左右栏响应式断点 A1 + A4 VAD 链路保护的注释）

**验证方式**:
- `npm run build` 通过
- 完整流程截图：开启摄像头 → 取景器出现 → 开始录音 → 示波器波形动 → 假装说话（headless 不可用，用 mock）→ 状态切换正确
- VAD 链路功能不回归（人工 review code 确认 handleVADStateChange 未被改动）

**不包含**: 流式回复"信号解码"动效（B7 留到 PR #4）

### PR #4: 动效层 - 流式回复解码动效 + 微调

**分支**: `feat/ui-motion`（基于 PR #3 合并后）

**包含改造点**: B7（流式文字渐显）+ 全局微调

**改动文件**:
- `xengineer-frontend/src/components/StreamingMessage.tsx`
- `xengineer-frontend/src/components/AudioPlayer.tsx`（波形颜色微调）
- 其他根据 PR #1-3 截图发现的细节

**验证方式**:
- `npm run build` 通过
- 发送测试消息 → 流式回复文字以"解码"方式渐显
- 全套 UI 截图（最终版）保存到 `/home/z/my-project/download/ui-final/`

---

## 6. 验证策略

### 6.1 每个 PR 必须满足

- [ ] `npm run build` 通过（tsc + vite build）
- [ ] `git diff` 不含 `xengineer-frontend/dist/` 改动（build 产物不进 commit）
- [ ] agent-browser 截图至少 3 张状态：初始 / 录音中 / 收到回复
- [ ] WebSocket 功能不回归（连接成功 + 收到 echo）
- [ ] VAD 链路 code review：`handleVADStateChange` 中 `audioPlayer.stop()` + `send({vad_status})` + `setShouldCapture(true)` 三行未被改动

### 6.2 最终验证（PR #4 合并后）

- [ ] 7 张 baseline 截图 vs 7 张 final 截图对比
- [ ] 移动端 375px 截图无横向滚动条
- [ ] 桌面端 1440px 截图整体观感符合"示波器/仪器"signature
- [ ] 至少 1 个非开发者朋友/同事能 5 秒内说出"这看起来是个跟摄像头和麦克风对话的 AI"

---

## 7. 不做的事（Out of Scope）

明确列出本次 UI 改造**不做**的事，避免范围蔓延：

- ❌ 后端任何改动（API / WS 协议 / TTS 采样率）
- ❌ 引入 react-router（仍保持单页）
- ❌ 引入状态管理库（仍用 useState + useRef）
- ❌ ScriptProcessorNode → AudioWorklet 迁移（性能优化，不是 UI）
- ❌ 暗色/亮色主题切换（本次只做暗色，但 token 化方便未来扩展）
- ❌ 国际化（i18n）（仍保持中文）
- ❌ 抽 `useConversationOrchestrator` hook（功能重构，留作后续 PR）
- ❌ 把 `dist/` 从 git 追踪移除（这是基础设施改动，不混在 UI PR 里；但每个 PR 跑完 build 后用 `git checkout -- xengineer-frontend/dist/` 恢复）

---

## 8. 待用户确认的开放问题

在主代理开始派实施子代理之前，请用户回答以下问题（任何一项的回答都可能调整本计划）：

1. **Signature 概念"示波器/仪器"是否接受？**
   - 接受 → 按本计划走
   - 不接受，倾向其他方向 → 你给方向，我重写 §2
   - 想看候选 → 我可以再出 2 个备选 signature 概念

2. **朱砂红 `#C8453C` 作为 brand 色是否接受？**
   - 接受 → 按本计划走
   - 太红 → 可换成深朱砂 `#A83A32` 或铁锈红 `#8B3A2F`
   - 想换色 → 你给方向（如墨绿/深蓝紫/琥珀黄）

3. **字体选择是否接受？**
   - 思源宋体（display）+ 思源黑体（body）+ JetBrains Mono（数据）
   - 备选：思源黑体（display）+ 思源黑体（body）+ JetBrains Mono（数据）— 更工程感，少文气
   - 备选：霞鹜文楷（display）+ 思源黑体（body）+ JetBrains Mono（数据）— 更人文，少工程感

4. **PR 拆分是否接受 4 个？**
   - 接受 → 按本计划走
   - 太多 → 合并为 2 个（tokens+signature / components+motion）
   - 想加 → 拆得更细

5. **是否需要先用 mockup 工具（如 Figma）出视觉稿？**
   - 不需要 → 直接代码实现（子代理会截图反馈）
   - 需要 → 我可以派子代理用 HTML+CSS 出一个静态 mockup 页面，你审过再开始改 React 代码

---

## 9. Mockup 评审阶段（用户决策前置环节）

> 本阶段是 §10 子代理执行编排的**前置环节**。在用户从 6 个候选方向中选定 signature 之前，不进入 PR #1-#4 代码实施。

### 9.1 目的

文字描述 + 配色 hex 码 + 字体名都无法让用户真实感受"这个方向做出来什么样"。在进入 PR #1-#4 React 代码实施前，先用静态 HTML+CSS mockup 让用户视觉对比 6 个 signature 方向，选定后再开始改 React 代码。避免实施到一半发现方向不对要返工。

### 9.2 6 个 Mockup 方案清单

> 6 个方向的详细论证见对话讨论，本表是速查。所有方案都主动避开 SKILL.md 警示的 3 个 AI 模板默认（cream+serif+terracotta / black+acid-green / broadsheet hairline）。

| ID | 方案 | 核心隐喻 | 主色 | 字体组合 | 风险等级 | 与 Engineer 关联 | 与 AI 视觉对话契合 |
|---|---|---|---|---|---|---|---|
| **A** | 示波器 / Oscilloscope | AI 视觉对话 = 科学仪器测量信号 | 工程灰 `#0a0a0b→#34343c` + 朱砂红 `#C8453C` + 示波器青 `#5eead4` | 思源宋 + 思源黑 + JetBrains Mono | 中 | 强 | 中 |
| **B** | 暗房 / Darkroom | AI 在暗房红安全灯下显影画面 | 安全灯红 `#7a1f1f` + 显影黑 `#0d0a0a` + 相纸米白 `#f4ead5` | Cormorant + Inter + IBM Plex Mono | 中 | 弱 | 强 |
| **C** | 水墨 / Ink Modernism | 东方书法的留白+笔触+印章 | 墨黑 `#1a1d1f` + 宣纸米 `#f5f1e8` + 印章朱砂 `#c8453c` + 金箔 `#c9a961` | 霞鹜文楷 + 思源黑 + JetBrains Mono | 中 | 中（"X"印章感） | 中 |
| **D** | 广播室 / Broadcast Studio | 双模态对话 = 调音台前与电台主播对话 | 深胡桃木 `#2a1810` + 黄铜 `#b08d57` + 暖象牙 `#f5e6d3` + VU 绿 `#4ade80` | Playfair Display + Source Sans + JetBrains Mono | 中高 | 弱 | 强 |
| **E** | 实验室 / Laboratory | AI 是实验员，分析视觉+语音样本 | 医用白 `#fafbfc` + 解剖绿 `#2d5f4e` + 警示橙 `#d97706` + 数据蓝 `#0ea5e9` | Söhne/Inter + 同 + JetBrains Mono | 中 | 强 | 中 |
| **F** | 终端 / Terminal CRT | 工程师图腾 — 磷光绿 CRT 终端 | 磷光绿 `#00ff41` + 深黑 `#0a0e0a` + 琥珀警告 `#ffb000` | 全文 JetBrains Mono（display+body+data） | 高 | 极强 | 弱 |

### 9.3 Mockup 技术规范

**形式**:
- 纯 HTML + 内联 CSS 单文件（`<scheme>.html`），无 React / 无 build / 无外部 JS 依赖
- 字体通过 Google Fonts `<link>` 加载
- 不连真实后端、不调 getUserMedia、不响应点击 — 纯静态展示
- 允许使用 CSS animation / keyframes 模拟动效（如呼吸光、扫描线、波形脉动）

**布局复刻**（所有 6 个 mockup 必须复刻同一布局，仅样式不同）:

```
┌────────────────────────────────────────────────────────────────┐
│ [logo] XEngineer                              [data readouts]  │  Header (h-14)
│        AI Vision Conversation Assistant                        │
├──────────────────────┬─────────────────────────────────────────┤
│                      │                                         │
│   [Camera 4:3]       │  USER: 你好，你能看到我吗？              │
│   取景框 + 角标       │                                         │
│                      │  AI: 是的，我能看到你。你戴着一副...     │
│                      │  (流式中，含光标)                        │
│   [● REC] [测试消息]  │                                         │
│                      │  SYS: 摄像头已开启                       │
│                      │                                         │
│                      │  USER: 好的，那你能听到我说话吗？        │
├──────────────────────┴─────────────────────────────────────────┤
│ WS:CONNECTED │ VAD:SILENT │ AI:IDLE │ 24kHz │ v0.1.0           │  StatusBar
└────────────────────────────────────────────────────────────────┘
```

**signature 元素要求**（每个方案必须实现各自 §2 中列出的全部 signature 元素的静态展示）:
- A 示波器：取景器十字线 + 32 柱波形（CSS animation 模拟）+ 数据读数条
- B 暗房：左上角红色 ambient 光晕（径向渐变）+ Camera 边框胶片穿孔（左右 8 个小方块）+ 流式回复用模糊渐显动效
- C 水墨：印章式 logo（朱砂红方形 + 白文"X"）+ 对话气泡底部"落款"+ Camera 角部墨笔触装饰
- D 广播室：录音按钮设计成物理推子样式 + VU 表针（CSS 旋转动画）+ Camera 边框设计成老式电视框
- E 实验室：light theme + Camera 边框显微镜圆形视野（径向 mask）+ 状态栏表格化（行间分隔 + 序号列）
- F 终端：CRT 扫描线 overlay + 全文 JetBrains Mono + 实心方块光标 + AI 回复每行前 `>` 提示符

**截图要求**:
- 桌面端 1440×900 PNG（必出）
- 移动端 375×812 PNG（必出，验证响应式）

### 9.4 子代理编排

6 个子代理并行执行（互不依赖），每个负责一个方案：

| 子代理 | 方案 | 输出目录 |
|---|---|---|
| subagent-M1 | A 示波器 | `docs/ui-mockups/A-oscilloscope/` |
| subagent-M2 | B 暗房 | `docs/ui-mockups/B-darkroom/` |
| subagent-M3 | C 水墨 | `docs/ui-mockups/C-ink/` |
| subagent-M4 | D 广播室 | `docs/ui-mockups/D-broadcast/` |
| subagent-M5 | E 实验室 | `docs/ui-mockups/E-lab/` |
| subagent-M6 | F 终端 | `docs/ui-mockups/F-terminal/` |

每个子代理的输出文件清单:
- `<scheme>.html` (单文件 mockup, 30-80KB)
- `desktop-1440x900.png` (桌面端截图)
- `mobile-375x812.png` (移动端截图)

**关键约束**:
- 子代理**只创建文件**，不 commit / 不 push（避免 6 个并行 push 冲突）
- 主代理等 6 个子代理全部完成后，统一 `git add docs/ui-mockups/ && git commit && git push`
- 子代理可 Read `/home/z/my-project/skills/frontend-design/SKILL.md` 做设计原则参考
- 子代理可 Read `/home/z/my-project/XEngineer/docs/ui-research/frontend-structure.md` 了解当前 UI 结构

### 9.5 评审流程

1. 主代理 push 6 个 mockup 到 PR #54（feat/improve-ui 分支）
2. 主代理在 PR #54 评论里贴 6 张桌面端截图（GitHub 渲染图片，用户直接看）
3. 用户在 PR 评论里挑选（或在这里告诉主代理）
4. 用户选定后:
   - 主代理更新计划文档 §2，把 signature 概念从"示波器"改为用户选定的方案
   - 主代理更新 §3 design tokens，匹配选定方案
   - 主代理更新 §4 组件级改造清单（如需要）
   - 主代理 commit + push 计划文档更新
5. 进入 §10 子代理执行编排预案，派 subagent-E 开始 PR #1

### 9.6 不入选的 mockup 处理

用户选定后，其他 5 个 mockup 文件**保留在 `docs/ui-mockups/` 中**作为决策档案，不删除。这样后续如果需要切换方向或回看，都有视觉参考。

### 9.7 时间预估

- 6 个子代理并行做 mockup: 约 10-15 分钟（每个子代理独立工作）
- 主代理 push + 用户审阅: 约 5-10 分钟
- 总耗时: 约 15-25 分钟

---

## 10. 子代理执行编排预案

用户在 §9 Mockup 评审中选定方向后，主代理将按以下顺序派子代理（每个 PR 一个子代理，串行执行避免冲突）：

| 子代理 | 任务 | 输入 | 输出 |
|---|---|---|---|
| subagent-E | 实施 PR #1（基础层） | 本计划 §3 + §5-PR1 段 | 代码改动 + build 通过 + 截图 + push + 开 PR |
| subagent-F | 实施 PR #2（signature 层） | 本计划 §4.2 §4.3 §4.8 + §5-PR2 段 + PR #1 已合并 | 同上 |
| subagent-G | 实施 PR #3（组件层） | 本计划 §4.4-4.7 + §5-PR3 段 + PR #1/#2 已合并 | 同上 |
| subagent-H | 实施 PR #4（动效层） | 本计划 §4.6 B7 + §5-PR4 段 + PR #1/#2/#3 已合并 | 同上 + final 截图对比 |

每个子代理的 prompt 将包含:
1. 本计划文档路径（可 Read 全文）
2. frontend-design SKILL.md 路径（可 Read 做细节参考）
3. 该 PR 的具体改造点清单
4. 验证 checklist
5. 必须用 `GH_TOKEN=... gh pr create` 开 PR（避免 gh login scope 问题）
6. 必须把工作记录 append 到 worklog.md

---

## 附录 A: baseline 截图索引

| 截图 | 路径 | 描述 |
|---|---|---|
| 01 主页面 | `/home/z/my-project/download/ui-baseline/01_main_page.png` | 1440×900 初始状态 |
| 02 测试消息后 | `.../02_after_test_msg.png` | 点击"发送测试消息"后含 2 条对话气泡 |
| 03 录音状态 | `.../03_recording_state.png` | 点击"开始录音"后（headless getUserMedia 失败） |
| 04 摄像头状态 | `.../04_camera_state.png` | 点击"开启摄像头"后（headless getUserMedia 失败） |
| 05 标注图 | `.../05_annotated.png` | 带数字标注的交互元素地图 |
| 06 移动端 | `.../06_mobile_375x812.png` | 375×812 窄屏（双栏未断点，问题暴露） |
| 07 全页 | `.../07_full_page.png` | 全页捕获（与 01 一致） |

## 附录 B: 关键代码位置索引

（来自 frontend-structure.md §附录）
- WebSocket URL 与重连: `src/hooks/useWebSocket.ts:4, 22, 35`
- VAD 触发链路: `src/App.tsx:115-128` ⚠️ 改造时勿动
- Barge-in 实现: `src/components/AudioPlayer.tsx:88-100` + `src/App.tsx:119` ⚠️ 改造时勿动
- 7 种 ServerMessage 处理: `src/App.tsx:35-87`
- 消息协议定义: `src/lib/protocol.ts:1-30`
- AudioContext 24kHz 单例: `src/components/AudioPlayer.tsx:28, 108` ⚠️ 改造时勿动
- 摄像头截图 JPEG q=0.6: `src/hooks/useCamera.ts:30`
- VAD 能量阈值 0.02 / 帧计数 3/15: `src/lib/vad.ts:27-39, 52-66`
