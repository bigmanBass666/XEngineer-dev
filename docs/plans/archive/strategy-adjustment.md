> 已归档 - 此计划已完成，仅供历史参考

# 策略调整：直接在当前仓库进行全流程开发

> 2026-06-14 — 从"准备→开新仓库"改为"直接在 XEngineer-temp 全流程开发"

---

## 一、背景

原计划：XEngineer-temp（私有，准备工作）→ 比赛开新公开仓库（orphan branch 压成干净 commit）

现实：没时间开新仓库了，直接在当前仓库进行全流程。

## 二、当前仓库状态分析

| 项目 | 当前值 | 是否需要调整 |
|------|--------|-------------|
| 仓库名 | `bigmanBass666/XEngineer-temp` | ⚠️ 见下方讨论 |
| 可见性 | public | ✅ 已改为公开 |
| 分支 | main（直接在 main 上开发） | ⚠️ 比赛要求 GitHub flow（PR） |
| Commit 规范 | `<type>: <中文描述>` | ✅ 可保留 |
| 现有 commit | 37+ 个（含文档准备工作） | ⚠️ 时间戳合规问题 |
| post-commit hook | ✅ 已部署 | ✅ 正常工作 |
| 根目录 pre-commit hook | ✅ 已部署 | ✅ 正常工作 |

## 三、比赛规则红线（必须满足）

1. **全周期持续交付，严禁突击提交** — 持续 PR 记录和 commit，最后一天一次性导入 = 无效
2. **commit 时间戳必须在 6.12-6.14 之间** — 超出视为无效
3. **代码重复率 >50% = 取消资格 + 招聘黑名单**
4. **每个 PR 只做一件事**，粒度尽可能细
5. **PR 标题 + 描述**必须包含：功能描述、实现思路、测试方式
6. **PR 合并后主分支保持可运行状态**
7. **公开 GitHub 仓库** + demo 视频 + README（含依赖说明）

## 四、需要调整的事项

### 4.1 仓库可见性：private → public ✅ 已完成

**状态：** 已改为 public。
- 好处：不需要开新仓库，所有 commit 历史保留
- 坏处：仓库名叫 "XEngineer-temp" 不够正式（但比赛没要求仓库名）
- 风险：准备阶段的 commit 都是文档调研，不涉及代码，评委看到也无妨
- 额外好处：public 仓库免费账户可以开启分支保护功能（private 仓库需要 GitHub Pro）

### 4.2 开发模式：直接 main → GitHub flow（分支 + PR）

**问题：** 当前所有 commit 直接在 main 上，比赛要求 PR 流程。

**调整方案：**

```
main (受保护)
  ↑ merge PR
  │
  feat/xxx (功能分支)
  fix/xxx  (修复分支)
  docs/xxx (文档分支)
```

**具体流程：**
1. 创建功能分支：`git checkout -b feat/asr-integration`
2. 在功能分支上开发、commit
3. 推送到远程：`git push origin feat/asr-integration`
4. 在 GitHub 上创建 PR（main ← feat/asr-integration）
5. PR 描述包含：功能描述 + 实现思路 + 测试方式
6. 合并 PR（squash merge 或 merge commit 均可）
7. 合并后 main 保持可运行

**单人参赛 PR 的特殊性：**
- 没有代码审查（自己写自己合）
- PR 的价值在于：展示开发过程、commit 分布、功能拆分思路
- 评委看的是 PR 数量/质量/commit 分布合理性（占评分 40%）

### 4.3 Commit 时间戳合规

**问题：** 已有 37+ 个 commit，大部分是准备阶段文档。

**分析：**
- 当前时间已在 6.12-6.14 窗口内 ✅
- 准备阶段的文档 commit 也是有价值的——它们展示了**调研过程和持续交付**
- 文档 commit 本身不涉及代码相似度问题
- 评委看的是"开发过程与质量"，持续的文档调研 commit 反而是加分项

**结论：** 保留现有 commit 历史，不做 squash。准备工作的 commit 展示了"全周期持续交付"，符合比赛精神。

### 4.4 Commit 规范调整

现有规范已基本可用，但需要补充 PR 相关的 branch naming：

| 规范项 | 现有 | 调整后 |
|--------|------|--------|
| Commit message | `<type>: <中文描述>` | ✅ 保持不变 |
| Branch naming | 无 | 新增：`feat/<功能名>`、`fix/<描述>`、`docs/<描述>` |
| PR 标题 | 无 | 新增：`[feat/fix/docs] <功能描述>` |
| PR 描述 | 无 | 新增：必须包含功能描述、实现思路、测试方式 |

### 4.5 文档更新需求

| 文件 | 需要更新的内容 |
|------|---------------|
| `README.md` | 仓库名去掉 "-temp" 感（或改名后更新），更新开发模式为 GitHub flow |
| `devplan.md` | 废弃"开新仓库"计划，更新为"直接在当前仓库全流程" |
| `docs/git-hardening-plan.md` | 状态全部标记完成 |
| worklog 规范 | 补充分支命名 + PR 规范 |

## 五、根目录 pre-commit hook 兼容性

当前根目录 hook 拦截 XEngineer/ 文件提交到根 git。这不受策略调整影响，保持不变。

但需要注意：如果将来在根目录也进行开发（fullstack 等），根 git 的 pre-commit hook 可能需要调整。

## 六、讨论记录

### 6.1 仓库改名
- [x] **决定：不改名**，保持 `XEngineer-temp`
- 原因：比赛没要求仓库名，改名需要更新 remote URL，增加不必要的复杂度

### 6.2 是否保护 main 分支（要求 PR 合并）

**选项分析：**

**如果开启 main 保护（Require a pull request before merging）：**
- ✅ 我（AI）不需要用户手动 merge — 可以通过 GitHub API 自动创建 PR + merge PR
- ✅ 单人参赛，不开 "Require approvals"（代码审查），所以不会卡在审批环节
- ✅ 不需要 CI（不开 "Require status checks"），不会卡在 CI 上
- ⚠️ 增加了复杂度：每次功能完成需要额外调用 GitHub API 创建+合并 PR
- ⚠️ 如果 API 调用出问题（token、网络等），PR 卡着合不进去，需要用户手动处理
- ⚠️ 之前已经有 token 失效 + push 静默失败的前科，再加一层 API 操作就是再加一层风险

**如果不保护：**
- ✅ 流程简单：分支开发 → push → 手动在网页创建 PR → 网页点击 merge
- ✅ 少一个故障点
- ❌ 万一我或子代理忘记创建分支直接在 main 上 commit，不会报错（靠规范约束）
- ❌ 评委如果查看 commit 历史可能看到没有 PR 记录的 commit（但当前的文档 commit 本来就没有 PR）

**结论：开启分支保护。** 理由：系统强制比靠纪律可靠，且我可以通过 GitHub CLI 自动操作 PR，不需要用户手动 merge。

**执行状态：**
1. ✅ 安装 GitHub CLI（`gh` v2.46.0）
2. ✅ 配置认证（`GH_TOKEN` 环境变量，scope: repo）
3. ✅ 开启 main 分支保护（Require PR + enforce_admins=true）
4. ✅ 更新 post-commit hook：`git push HEAD` 推送当前分支
5. ✅ 验证：PR #1 创建+ squash merge 成功，admin 直接 push 被拒绝

### 6.3 PR 用 squash merge 还是 merge commit

**我的建议：squash merge。**

理由：
1. **main 历史更干净** — 每个 PR 压成一个 commit，main 上的 commit 历史就是 PR 列表的镜像，评委一眼就能看出开发节奏
2. **分支内的试错 commit 不会污染 main** — 开发过程中可能有 `fix: 修了个typo`、`chore: 调试` 这种无意义 commit，squash 后只保留 PR 级别的语义 commit
3. **评委看的是 PR 数量和分布**，不是分支内的细粒度 commit。分支内 commit 细粒度是为了自己调试方便，main 上 commit 细粒度是为了评委好看——squash 两者兼得
4. merge commit 在单人参赛下没有意义（没有分支合并冲突解决的记录价值）
5. GitHub 默认勾选 squash merge，操作上也更方便
