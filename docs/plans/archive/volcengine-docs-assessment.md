> 已归档 - 此计划已完成，仅供历史参考

# 火山引擎语音文档 - 摸底评估 & 抓取计划

> 站点入口：https://www.volcengine.com/docs/6561
> 评估时间：2026-06-13（Hackathon赛前准备阶段）

---

## 一、站点整体规模

| 指标 | 数值 |
|------|------|
| 总文档量 | 约113-131篇（三个子代理统计有差异，分类边界不同，实际约120篇） |
| 三大Tab | 文档指南(~35篇)、API参考(~77篇)、产品计费(~6篇) |
| 文档平均长度 | 5000-8500字符/篇 |
| 总字符量 | 约65-85万字符 |
| 超大页面 | 音色列表(3.9万字符)、产品动态(2.5万字符) |

---

## 二、Hackathon核心文档筛选结论

**我们不需要全部文档。** 对Hackathon有用的核心文档约20篇，按优先级分5组。

---

## 三、第二阶段抓取计划（5个子代理并行）

### 总体原则

- 每个子代理**独立完成「访问→提取markdown原文→写盘」全流程**，只向主代理返回摘要
- 统一保存目录：`/home/z/my-project/XEngineer/docs/api/volcengine/`
- 文件命名按功能，小写+连字符

### 抓取方式

1. 用 agent-browser 打开目标文档页面
2. 点击页面上的「复制页面」按钮旁的小箭头 → 选择「复制 markdown 页面」
3. 通过 JS 读取剪贴板拿到 markdown 原文
4. 直接保存为 .md 文件到上述目录
5. 向主代理返回：保存的文件列表 + 每篇的一句话备注 + 相关性评分(1-5)

### 子代理分工

| # | 分组 | 目标文档 | 产出文件 | 预估篇数 |
|---|------|---------|---------|---------|
| **1** | ASR + 接入 | ASR大模型流式API（Seed-ASR）| `seed-asr-streaming.md` | ~4 |
| | | 鉴权/认证说明 | `auth-guide.md` | |
| | | 快速入门/接入指南 | `quickstart.md` | |
| | | ASR其他配置/参数 | `asr-config.md` | |
| **2** | TTS | TTS HTTP流式API | `tts-http-streaming.md` | ~3 |
| | | TTS WebSocket流式API | `tts-websocket-streaming.md` | |
| | | TTS音色/参数说明 | `tts-voices-params.md` | |
| **3** | 端到端语音 | 端到端实时语音大模型（Speech2Speech）| `speech-to-speech.md` | ~3 |
| | | 播客生成/同传API（如有）| `podcast-interpreter.md` | |
| | | 实时对话场景配置 | `realtime-conversation.md` | |
| **4** | 平台能力 | 热词管理API | `hotword-management.md` | ~4 |
| | | 自学习平台 | `self-learning-platform.md` | |
| | | 计费说明 | `billing.md` | |
| | | 控制台API Key使用 | `api-key-guide.md` | |
| **5** | 补充 | 支持的模型列表 | `model-list.md` | ~6 |
| | | 音色列表（摘要版）| `voice-list-summary.md` | |
| | | WebSocket协议/错误码 | `protocol-errors.md` | |
| | | 其他补充文档 | `misc.md` | |

### 隐含优先级（分组即优先级）

- Agent 1（ASR）& Agent 3（端到端语音）= **最高**
- Agent 2（TTS）= **高**
- Agent 4（平台能力）= **中**
- Agent 5（补充）= **低**

### 超大页面处理

- 音色列表（3.9万字符）：保存完整 markdown 原文
- 如果单文件超过5万字符，保留完整原文但额外生成一个摘要文件

### 预期产出

- `/home/z/my-project/XEngineer/docs/api/volcengine/` 下约 **20个 .md 文件**
- 总磁盘占用预估：约 2-5 MB（纯文本）

---

## 四、Git 故障复盘与防护措施

### 故障链

1. **Remote URL 被篡改** — 某次操作（疑似 fullstack 初始化脚本）将 XEngineer 的 remote 从 `XEngineer-temp` 改为 `sceneforge`
2. **GitHub Token 失效** — 旧 token `ghp_cHkP1...` 被撤销，push 静默失败
3. **post-commit hook `2>/dev/null`** — 所有 push 错误被吞掉，无人知晓
4. **Bash 工具 `cd` 不持久** — 每次 Bash 调用都回到根目录 `/home/z/my-project/`，在根目录执行的 `git remote set-url` 修改的是根目录的 sceneforge 仓库，不是 XEngineer 的

### 已实施的修复

- [x] 更新 GitHub Token（新 token 存入 `.env`）
- [x] 修正 XEngineer remote URL（用 `GIT_DIR` 显式操作）
- [x] 重写 post-commit hook：从 `.env` 动态读取 token，错误记录到 `.git/push-error.log`，不再静默
- [x] Force push 同步了全部 37 个 commit

### 防护规则（写入 worklog 规范）

1. **操作 XEngineer git 时必须用绝对路径或 GIT_DIR**，因为 Bash `cd` 不持久：
   ```bash
   cd /home/z/my-project/XEngineer && git add <file> && git commit -m "msg"
   ```
   或：
   ```bash
   GIT_DIR=/home/z/my-project/XEngineer/.git git status
   ```
2. **子代理操作 XEngineer git 同理**，指令中必须包含完整路径
3. **post-commit hook 从 .env 读取 token**，不再硬编码在 remote URL 中
4. **push 错误不再静默**，写入 `.git/push-error.log`

---

## 五、执行状态

- [x] 第一阶段：站点规模摸底完成
- [x] 第二阶段：核心文档抓取完成（19个文件，~608KB）
- [x] Git 故障修复完成
