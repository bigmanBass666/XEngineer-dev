# 视觉对话端到端闭环测试计划

> 状态：**讨论中，持续更新**
> 最后更新：2026-06-15
> 目标：建立「测试 → 发现问题 → 修复 → 再测试」的自动化闭环，覆盖视觉对话完整链路
> 前置依赖：Phase 0（Git 规范强制执行机制）

---

## Phase 0：从根源解决 Git/PR 规范违规

### 为什么之前没有遵循 PR 规范？

**不是"忘了"，而是项目机制在主动破坏规范。** 具体根因：

| 根因 | 证据 | 后果 |
|------|------|------|
| **① post-commit hook 自动 `git push origin main`** | `.githooks/post-commit` 原始内容：commit 后立即注入 token、push main、失败重试 | 每次 commit 直接上 main，**完全绕开 PR 流程** |
| **② 没有 pre-push hook 拦截直接推 main** | `.githooks/` 只有 post-commit，没有 pre-push | 没有任何机制阻止直接推 main |
| **③ 规则文档没有被工作流强制执行** | `docs/competition-rules.md` 存在，但读不读没有区别 | 约束是"软"的，违反无成本 |
| **④ 我没有"先读约束再动手"的步骤** | 拿到任务直接写代码、直接 push | 缺少结构化的前置检查 |

**一句话：git hooks 在主动破坏 PR 规范，而没有任何机制在保护它。**

### 解决方案：让违规变得不可能（而非依赖记忆）

#### 改动 1：重写 `.githooks/post-commit`

**当前**（已锁定为注释）：`# LOCKED - 比赛已截止，禁止提交`
**原始**（问题根源）：

```bash
# 当前 hook 做的事：
git push origin main  # ← 直接推 main，绕开 PR！
```

**改为**：

```bash
#!/bin/bash
# Post-commit hook: 阻止直接推 main，强制 PR 工作流

BRANCH=$(git rev-parse --abbrev-ref HEAD)
PROTECTED_BRANCHES=("main" "master")

if [[ " ${PROTECTED_BRANCHES[*]} " == *" ${BRANCH} "* ]]; then
    echo "❌ 错误：不能直接 commit 到 ${BRANCH} 分支"
    echo ""
    echo "请使用 PR 工作流："
    echo "  1. git checkout -b feature/你的功能名"
    echo "  2. 修改代码 + commit"
    echo "  3. git push dev feature/你的功能名"
    echo "  4. 在 GitHub 创建 PR → Review → Merge"
    echo ""
    echo "参考：docs/competition-rules.md §PR提交规范"
    # 撤销本次 commit（保留暂存区）
    git reset --soft HEAD~1
    exit 1
fi

echo "✅ Commit 成功（分支: ${BRANCH}）"
echo "💡 提醒：完成后请 push 到 dev remote 并创建 PR"
echo "   git push dev ${BRANCH} -u"
```

#### 改动 2：新增 `.githooks/pre-push`

```bash
#!/bin/bash
# Pre-push hook: 阻止直接推送到 main/master 分支

while read oldrev newrev refname; do
    BRANCH=$(echo "$refname" | sed 's|refs/heads/||')
    
    if [ "$BRANCH" = "main" ] || [ "$BRANCH" = "master" ]; then
        echo "❌ 错误：不能直接 push 到 ${BRANCH}"
        echo ""
        echo "请通过 GitHub PR 合并代码到 ${BRANCH}"
        echo "  git push dev $(git rev-parse --abbrev-ref HEAD) -u"
        echo "  然后在 GitHub 上创建 Pull Request"
        exit 1
    fi
done

exit 0
```

#### 改动 3：更新 `scripts/setup.sh`

在 setup.sh 末尾增加规则提醒步骤：

```bash
# 11. 显示 PR 规范提醒
echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║  ⚠️  Git 工作流提醒（比赛红线规则）               ║"
echo "╠══════════════════════════════════════════════════╣"
echo "║  ❌ 禁止直接 commit/push 到 main                  ║"
echo "║  ✅ 必须：创建 feature 分支 → push → 创建 PR      ║"
echo "║  ✅ PR 需包含：标题/功能描述/实现思路/测试方式    ║"
echo "║  📖 完整规则：docs/competition-rules.md           ║"
echo "╚══════════════════════════════════════════════════╝"
```

#### 改动 4：更新 `worklog.md` 开头

在比赛规则摘录之前，增加操作员前置检查清单：

```markdown
## 操作员前置检查（每次会话开始时执行）

- [ ] 读取 worklog.md 了解上次进度
- [ ] 读取 docs/plans/ 下相关计划文件
- [ ] 确认当前分支不是 main（如在 main 上，先切到 feature 分支）
- [ ] 所有代码改动通过 PR 提交，不直接推 main
```

### Phase 0 PR 规划

| PR | 标题 | 包含文件 |
|----|------|---------|
| PR-A | `fix: 重写 git hooks 强制 PR 工作流，禁止直接推 main` | `.githooks/post-commit`, `.githooks/pre-push` |
| PR-B | `chore: setup.sh 增加 PR 规范提醒步骤` | `scripts/setup.sh` |
| PR-C | `docs: worklog 增加操作员前置检查清单` | `worklog.md` |

### Phase 0 验收

| # | 验证项 | 验证方式 |
|---|--------|---------|
| 1 | 在 main 分支 commit 被拒绝 | `git commit` → 输出错误信息 + 自动 reset |
| 2 | 直接 push main 被拒绝 | `git push dev main` → hook 拦截 |
| 3 | feature 分支 commit 正常 | `git checkout -b feature/test && git commit` → 成功 |
| 4 | setup.sh 显示 PR 提醒 | `bash scripts/setup.sh` → 输出提醒框 |

---

## 一、背景与问题

### 1.1 当前测试能力

已实现的测试手段：

| 工具 | 能力 | 已验证 |
|------|------|--------|
| `curl` | 后端 health check | ✅ |
| Python `websockets` 脚本 | WS 连接、echo、VAD 会话 | ✅ |
| 合成正弦波 PCM | 音频传输协议 | ✅（但 ASR 无法识别） |
| `agent-browser` | 前端截图、console log 抓取 | ✅ |
| `railway logs` | 后端运行时日志 | ✅ |

### 1.2 当前链路断裂（已发现）

| # | 断裂点 | 位置 | 影响 |
|---|--------|------|------|
| D1 | 图片未传入 VLM | `orchestrator.py` handle_image() 只保存 base64，未调用 `vlm_node.update_image()` | VLM 始终无图，产品是"纯文本对话"而非"视觉对话" |
| D2 | VLM 期望 image_url 而非 base64 | `vlm_node.py` 第 54 行读 `image_url`，但 ASR 传来的是 `image: base64数据` | 即使修了 D1，VLM 拿到的也是无效的 base64 字符串当 URL |
| D3 | 合成测试数据无真实语音 | 正弦波 440Hz 不是语音，ASR 识别不出文字 | 无法验证 ASR→VLM→TTS 完整链路 |
| D4 | agent-browser 无摄像头/麦克风 | headless 浏览器无法获取硬件设备 | 无法模拟真实视频通话场景 |

### 1.3 目标闭环

```
  ┌─────────────────────────────────────────────────┐
  │                  测试闭环                          │
  │                                                   │
  │  合成语音(TTS) ──→ ASR识别 ──→ VLM+LLM(带图片)   │
  │       ↑                            ↓              │
  │       └──────── TTS输出 ←─────────┘              │
  │                                                   │
  │  agent-browser 打开前端 ──→ 截图 ──→ console检查  │
  │                                                   │
  │  发现问题 → 修代码 → push PR → 部署 → 重测        │
  └─────────────────────────────────────────────────┘
```

---

## 二、计划分步

### Phase 1：修通图片链路（D1 + D2）

**目标**：让 Camera 截图真正流入 VLM，实现多模态理解

**涉及文件**：
- `xengineer-backend/app/pipeline/orchestrator.py` — handle_image() 改为调用 vlm_node
- `xengineer-backend/app/pipeline/vlm_node.py` — 支持接收 base64 图片（而非仅 URL）

**技术方案（两个选项，待讨论）**：

| 方案 | 做法 | 优点 | 缺点 |
|------|------|------|------|
| A. base64 直传 | orchestrator 把 base64 直接传给 VLM，VLM 构建 `data:image/jpeg;base64,...` 内联 URL | 零外部依赖，纯内存 | base64 体积大，每帧 ~100KB |
| B. 临时图床 | orchestrator 把 base64 存到 Railway volume / S3 / imgbb，拿到公网 URL 再传给 VLM | 图片体积小，URL 可缓存 | 多一个外部依赖 |

**推荐方案 A** — Agnes API 支持内联 base64 URL，无需外部服务。

**改动要点**：
1. `orchestrator.handle_image()` → 调用 `self.vlm_node.update_image(data)` 传入 base64
2. `vlm_node.process()` → 构造 `data:image/jpeg;base64,{base64_data}` 作为 image_url
3. `asr_node._on_final()` → 传递 `{"text": text, "image": self._latest_image}`（已有，需确认 orchestrator 会把 image 传下来）

**PR 规划**：
- PR 标题：`fix: 修复图片未传入 VLM 的断裂，实现多模态对话`
- 包含文件：orchestrator.py, vlm_node.py
- 测试：发送图片 + 文字，验证 LLM 回复包含画面相关描述

---

### Phase 2：TTS 反向合成测试语音（D3）

**目标**：用 TTS API 合成中文语音 → 转 PCM → 喂给 ASR → 跑通完整链路

**技术方案**：

```
Volcengine TTS API
  "你好，请介绍一下你自己"
       ↓
    MP3 音频
       ↓
ffmpeg decode → PCM 16kHz mono
       ↓
base64 encode → WebSocket 发送
       ↓
ASR 识别 → VLM（带图片）→ LLM 回复 → TTS 输出
```

**涉及文件**：
- `tests/test_pipeline_e2e.py` — 新增 TTS 合成 + 转码逻辑

**依赖检查**：
- `ffmpeg` 是否可用（沙箱 + Railway 都需要）
- Volcengine TTS API 是否能从沙箱调用（需 APP_ID + ACCESS_TOKEN）

**PR 规划**：
- PR 标题：`test: 添加 TTS→ASR 合成语音端到端测试`
- 包含文件：tests/test_pipeline_e2e.py
- 测试：脚本自动跑通，10/10 全部通过

---

### Phase 3：前端 agent-browser 视觉验证

**目标**：用 agent-browser 打开线上前端，验证 WebSocket 连接 + UI 状态

**测试流程**：
```
agent-browser open https://xengineer-frontend.netlify.app
  → screenshot（保存到 download/）
  → console log（检查 WS 连接状态）
  → errors（检查 JS 异常）
  → wait [WS] Connected（确认连接成功）
  → screenshot（显示 connected 状态）
```

**涉及文件**：
- `tests/test_frontend_visual.py` — 新增 agent-browser 自动化测试脚本（或 shell 脚本）

**限制**：
- headless 无摄像头，无法测试 Camera 组件
- headless 无麦克风，无法测试 AudioRecorder
- 可验证：页面加载、WS 连接、UI 渲染、console 无异常

**PR 规划**：
- PR 标题：`test: 添加前端 agent-browser 视觉验证脚本`
- 包含文件：tests/test_frontend_visual.sh

---

### Phase 4：一键测试脚本 + CI 集成

**目标**：一个命令跑完所有测试，输出报告

**脚本设计**：`tests/run_all_tests.sh`

```bash
#!/bin/bash
# XEngineer 一键测试
echo "=== 1. 后端 Health Check ==="
curl -sf https://xengineer-dev-production.up.railway.app/health | jq .

echo "=== 2. Pipeline E2E ==="
python3 tests/test_pipeline_e2e.py

echo "=== 3. 前端视觉验证 ==="
bash tests/test_frontend_visual.sh

echo "=== 4. Railway 日志检查 ==="
railway logs --service XEngineer-dev | tail -20

echo "=== 测试完成 ==="
```

**PR 规划**：
- PR 标题：`chore: 添加一键测试脚本 run_all_tests.sh`
- 包含文件：tests/run_all_tests.sh

---

## 三、已知限制

| 限制 | 原因 | 影响 | 缓解方案 |
|------|------|------|---------|
| 无法测试真实摄像头 | headless 无硬件 | Camera 组件未经验证 | 用户手动测试 + 录屏 |
| 无法测试真实麦克风 | headless 无硬件 | AudioRecorder + VAD 未验证 | TTS 合成语音替代 |
| 无法听到 TTS 音频 | 无声卡/扬声器 | 音频播放效果未知 | 验证 base64 数据格式有效 |
| TTS→ASR 音质有损 | MP3→PCM 转码 | ASR 识别率可能低于真实语音 | 多条测试语句，取最优结果 |
| Railway 冷启动延迟 | 免费套餐休眠 | 首次请求可能超时 | 测试前先发 health check 唤醒 |

---

## 四、执行顺序与依赖

```
Phase 1 (修图片链路) ← 无依赖，可立即开始
    ↓
Phase 2 (TTS合成语音) ← 依赖 Phase 1（图片通了才有意义）
    ↓
Phase 3 (前端视觉验证) ← 可与 Phase 2 并行
    ↓
Phase 4 (一键脚本) ← 依赖 Phase 2 + Phase 3 完成
```

---

## 五、验收标准

| # | 标准 | 验证方式 |
|---|------|---------|
| A | 图片传入 VLM，LLM 回复包含画面描述 | 发测试图片 + "请描述你看到了什么" |
| B | TTS→ASR→VLM→TTS 完整链路 10/10 通过 | 自动测试脚本 |
| C | 前端 WS 连接稳定，console 无 error | agent-browser 测试 |
| D | 所有改动通过 PR 提交，符合比赛规范 | GitHub PR 列表 |
| E | 主分支可运行，任意时间查看可复现 | Railway + Netlify 部署验证 |
