#!/bin/bash
# XEngineer 环境初始化脚本
# clone 仓库后运行一次：bash scripts/setup.sh

cd /home/z/my-project/XEngineer || exit 1

echo "=== XEngineer 环境初始化 ==="

# 1. 设置 git hooks 路径
git config core.hooksPath .githooks
echo "[OK] core.hooksPath = .githooks"

# 2. 设置 hook 可执行权限
chmod +x .githooks/* 2>/dev/null
echo "[OK] hook 权限已设置"

# 3. 检查 .env 文件
if [ -f .env ]; then
    echo "[OK] .env 文件存在"
else
    echo "[WARN] .env 文件不存在！请手动创建 .env 并填入 API Keys"
    echo "       参考模板：.env.example（如存在）"
fi

# 4. 设置 remote URL（不含 token，hook 会动态注入）
git remote set-url origin https://github.com/bigmanBass666/XEngineer-temp.git 2>/dev/null
echo "[OK] remote URL 已标准化"

# 5. 清理旧的 .git/hooks 中的同名 hook（避免冲突）
if [ -f .git/hooks/post-commit ]; then
    mv .git/hooks/post-commit .git/hooks/post-commit.bak 2>/dev/null
    echo "[INFO] 旧的 .git/hooks/post-commit 已备份为 .bak"
fi

# 6. 恢复 GitHub CLI (gh) — 容器重置后可能丢失
if command -v gh &>/dev/null; then
    echo "[OK] GitHub CLI 已安装: $(gh --version 2>/dev/null | head -1)"
else
    GH_DEB="/home/z/my-project/upload/gh_2.46.0-3_amd64.deb"
    if [ -f "$GH_DEB" ]; then
        echo "[INFO] GitHub CLI 未找到，正在从备份恢复..."
        dpkg-deb -x "$GH_DEB" /tmp/gh-extract 2>/dev/null && \
        cp /tmp/gh-extract/usr/local/bin/gh /usr/local/bin/gh 2>/dev/null && \
        rm -rf /tmp/gh-extract
        if command -v gh &>/dev/null; then
            echo "[OK] GitHub CLI 已恢复: $(gh --version 2>/dev/null | head -1)"
        else
            echo "[WARN] GitHub CLI 恢复失败，请手动安装"
        fi
    else
        echo "[WARN] GitHub CLI 未找到，且备份 deb 包不存在于 upload/"
        echo "       手动恢复：curl -sLO http://deb.debian.org/debian/pool/main/g/gh/gh_2.46.0-3_amd64.deb"
        echo "                 dpkg-deb -x gh_2.46.0-3_amd64.deb /tmp/gh && cp /tmp/gh/usr/local/bin/gh /usr/local/bin/gh"
    fi
fi

# 7. 安装 Railway CLI（如果未安装）
if command -v railway &>/dev/null; then
    echo "[OK] Railway CLI 已安装: $(railway --version 2>/dev/null | head -1)"
else
    echo "[INFO] 安装 Railway CLI..."
    npm install -g @railway/cli 2>/dev/null
    if command -v railway &>/dev/null; then
        echo "[OK] Railway CLI 安装成功"
    else
        echo "[WARN] Railway CLI 安装失败"
    fi
fi

# 8. Railway token 认证（通过 RAILWAY_TOKEN 环境变量）
if [ -f .secrets/tokens.env ]; then
    source .secrets/tokens.env 2>/dev/null
    export RAILWAY_TOKEN
    if railway status &>/dev/null; then
        echo "[OK] Railway 认证成功"
    else
        echo "[WARN] Railway token 无效或已过期"
    fi
else
    echo "[WARN] .secrets/tokens.env 不存在，Railway 认证跳过"
fi

# 9. 安装 Netlify CLI（如果未安装）
if command -v netlify &>/dev/null; then
    echo "[OK] Netlify CLI 已安装: $(netlify --version 2>/dev/null | head -1)"
else
    echo "[INFO] 安装 Netlify CLI..."
    npm install -g netlify-cli 2>/dev/null
    if command -v netlify &>/dev/null; then
        echo "[OK] Netlify CLI 安装成功"
    else
        echo "[WARN] Netlify CLI 安装失败"
    fi
fi

# 10. Netlify token 认证
if [ -f .secrets/tokens.env ]; then
    source .secrets/tokens.env 2>/dev/null
    export NETLIFY_AUTH_TOKEN
    if netlify status 2>/dev/null; then
        echo "[OK] Netlify 认证成功"
    else
        echo "[WARN] Netlify token 无效或已过期"
    fi
else
    echo "[WARN] .secrets/tokens.env 不存在，Netlify 认证跳过"
fi

echo ""
echo "=== 初始化完成 ==="
echo "后续 commit 将自动 push 到远程（post-commit hook）"

# 11. 显示 PR 规范提醒
echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║  Git 工作流提醒（比赛红线规则）                   ║"
echo "╠══════════════════════════════════════════════════╣"
echo "║  禁止直接 commit/push 到 main                     ║"
echo "║  必须：创建 feature 分支 -> push -> 创建 PR       ║"
echo "║  PR 需包含：标题/功能描述/实现思路/测试方式        ║"
echo "║  完整规则：docs/competition-rules.md               ║"
echo "╚══════════════════════════════════════════════════╝"
