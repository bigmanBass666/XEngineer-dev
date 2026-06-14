> 已归档 - 此计划已完成，仅供历史参考

# Git 稳定性根治方案

> 2026-06-13 — 修复 push 静默失败问题后的根治讨论

---

## 一、已修复（但都是治标）

| 问题 | 修复方式 | 治标/根治 |
|------|---------|----------|
| Remote URL 被篡改 | 手动改回 | 治标 |
| GitHub Token 失效 | 更新新 token | 不可避免的操作，但配置方式有隐患 |
| hook `2>/dev/null` | 改成写日志 | 治标（能看到错误，但错误还是会发生）|
| Bash `cd` 不持久 | worklog 规范要求绝对路径 | 靠纪律，非系统机制 |

## 二、根治方案

### 方案1：Remote URL 自动校验+修正 ✅ 确认

**问题：** fullstack init 脚本或其他操作可能再次篡改 remote URL

**根治：** 在 post-commit hook 最前面加入 URL 校验：
- 从 .env 读取正确的 user/repo/token
- 与当前 origin URL 对比
- 不一致则自动修正再继续 push

**产出：** 更新 `.git/hooks/post-commit`

### 方案2：Token 单一真相源 ✅ 确认

**问题：** Token 写在 remote URL 和 .env 两处，过期后要改两处

**根治：**
- remote URL 只存不含 token 的地址：`https://github.com/bigmanBass666/XEngineer-temp.git`
- hook 从 .env 动态拼装带 token 的 push URL
- Token 过期只需改 `.env` 一处

**产出：** 更新 remote URL + 重写 hook

### 方案3：Push 自动重试 ✅ 确认

**问题：** 网络抖动等瞬时故障导致 push 偶尔失败

**根治：** hook 里 push 失败后等待 3 秒自动重试一次，仍失败再写日志。

**产出：** 更新 hook

### 方案4：路径混淆（Bash cd 不持久）❓ 待讨论

**问题：** 每次 Bash 调用都回到根目录，子代理执行 git 命令可能误操作根目录的 git

**原方案（xgit 包装脚本）：** ❌ 被否决 — 本质还是靠提醒 Agent 使用 xgit，纪律约束不可靠

**待讨论的替代方案：**

- **方案A：pre-commit hook 校验工作目录**
  - 在 .git/hooks/pre-commit 中检查 `pwd` 是否为 `/home/z/my-project/XEngineer`
  - 如果不是，拒绝 commit 并报错
  - 好处：自动生效，不需要任何人的纪律
  - 坏处：只能保护 commit 操作，git add 时路径错了还是会在错误的 repo 里 staged

- **方案B：不额外防护，接受现状**
  - worklog 规范已有明确路径要求，所有 Agent 都会读
  - 之前的问题已经修了（remote URL 已正确，不会再误推到 sceneforge）
  - 即使子代理在根目录执行 git 命令，由于 .gitignore 已排除 XEngineer/，不会影响根目录的 git 跟踪
  - 风险已经大幅降低

- **方案C：其他？待补充**

## 三、状态

- [ ] 方案1：hook URL 自动校验+修正
- [ ] 方案2：remote 去 token + hook 动态注入
- [ ] 方案3：push 自动重试
- [ ] 方案4：路径混淆 — 待讨论确认方案
