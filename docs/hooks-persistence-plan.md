# Hook 持久化根治方案

> 2026-06-14 — hook 反复消失（clone 恢复后丢失）的根治讨论

---

## 一、问题本质

`.git/hooks/` 目录**不被 git 跟踪**。每次 clone 或从远程恢复仓库，hooks 就丢了。

**已发生次数：** 至少 2 次（上次容器重置、这次从远程 clone 恢复）

**当前"修复"方式：** 手动重新写入 hook 脚本 → 典型的抑制而非根治。

**与此问题同根的还有 `.env` 文件：** 同样不被 git 跟踪，clone 后丢失。但 .env 是安全隔离（不能提交敏感信息到公开仓库），hook 没有这个借口。

---

## 二、根治方案：`core.hooksPath`

Git 有一个配置项 `core.hooksPath`，可以让 git 从**仓库内的一个目录**（而不是 `.git/hooks/`）读取 hook 脚本。

**原理：**
```bash
git config core.hooksPath .githooks
```

这样 git 会从 `.githooks/` 目录读取 hook，而 `.githooks/` 是普通目录，**可以被 git 跟踪**。

**好处：**
- Hook 脚本被 git 跟踪 → clone 后自动存在 ✅
- 不需要符号链接或其他间接层 ✅
- Git 原生支持，不是 hack ✅
- 修改 hook 也能被 commit 跟踪 ✅

**唯一的"缺点"：** `core.hooksPath` 是本地 git config，不被 git 跟踪。clone 后需要执行一次 `git config core.hooksPath .githooks`。

---

## 三、完整方案

### Step 1：在仓库内创建 `.githooks/` 目录（被 git 跟踪）

```
XEngineer/
  .githooks/
    post-commit    # push 自动化
    pre-commit     # （预留）
    commit-msg     # （预留）
```

### Step 2：把 hook 脚本从 `.git/hooks/` 迁移到 `.githooks/`

- `post-commit` → `.githooks/post-commit`（内容不变）
- 脚本开头保持 `#!/bin/bash`
- 需要 `chmod +x`（git 不跟踪文件权限，需要 setup 步骤）

### Step 3：创建 `scripts/setup.sh` 一键初始化脚本

```bash
#!/bin/bash
# 一键设置：git config + chmod hooks
cd /home/z/my-project/XEngineer
git config core.hooksPath .githooks
chmod +x .githooks/*
echo "✅ hooks 已配置"
```

clone 后只需运行一次 `bash scripts/setup.sh`。

### Step 4：post-commit hook 中自动设置 hooksPath（自举）

更进一步——在 `.githooks/post-commit` 的最前面加入自检：

```bash
#!/bin/bash
# 自举：如果 core.hooksPath 没有指向 .githooks，自动修正
CURRENT_HOOKS_PATH=$(git config core.hooksPath)
if [ "$CURRENT_HOOKS_PATH" != ".githooks" ]; then
    git config core.hooksPath .githooks
    echo "[INFO] core.hooksPath 已自动设置为 .githooks"
fi
# ... 后面是原来的 push 逻辑
```

但这有个鸡生蛋的问题：如果 hooksPath 没有设置，这个 hook 不会被触发。

**解决：** 在 setup.sh 中设置一次就够了。以后不会再丢失。

---

## 四、`.env` 的处理

.env 不能被 git 跟踪（敏感信息 + 公开仓库）。这个问题无法根治，只能：
1. 从安全的备份位置恢复（如用户手动提供）
2. 或者在 setup.sh 中从加密的备份解密（过度设计）

**结论：** .env 保持现状，clone 后需要用户重新提供。这是安全要求的代价，不是 bug。

---

## 五、根目录 git 的 hook（pre-commit 拦截）

根目录 `/home/z/my-project/.git/` 是平台系统的 git，我们不完全控制它（fullstack 脚本可能会重置）。

**方案：** 和 XEngineer 同理，用 `core.hooksPath`：
- 在 `/home/z/my-project/.githooks/` 创建根目录的 hook
- `git config core.hooksPath .githooks`
- 但根目录的 .githooks 会被根 git 跟踪，而根 git 可能被 fullstack 脚本覆盖

**结论：** 根目录 hook 用同样的 core.hooksPath 方案，但接受它可能被 fullstack 脚本重置的风险。setup.sh 中一并设置即可。

---

## 六、待确认

- [ ] 是否同意 `.githooks/` 方案？
- [ ] setup.sh 是否需要包含根目录 hooks 的初始化？
- [ ] post-commit hook 中是否需要自举逻辑（自动修正 hooksPath）？

## 七、状态

- [ ] 创建 `.githooks/` 目录 + 迁移 hook 脚本
- [ ] 创建 `scripts/setup.sh`
- [ ] 更新 worklog 规范（加入 clone 后运行 setup.sh 的提醒）
- [ ] 验证：删除 .git/hooks 下的旧 hook，确认 .githooks 生效
