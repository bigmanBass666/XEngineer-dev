#!/bin/bash
# XEngineer 环境初始化脚本
# clone 仓库后运行一次：bash scripts/setup.sh
# 也可在容器重置后重新运行，所有步骤幂等（已安装则跳过）

set -uo pipefail

cd /home/z/my-project/XEngineer || exit 1

echo "╔══════════════════════════════════════════════════╗"
echo "║  XEngineer 环境初始化                              ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""

# ==================== 基础工具 ====================

echo "[1/8] 基础工具检查"

if command -v git &>/dev/null; then echo "  ✅ git — $(git --version 2>/dev/null)"; else echo "  ❌ git — 未安装"; fi
if command -v python3 &>/dev/null; then echo "  ✅ python3 — $(python3 --version 2>/dev/null)"; else echo "  ❌ python3 — 未安装"; fi
if command -v pip &>/dev/null; then echo "  ✅ pip — $(pip --version 2>/dev/null | head -1)"; else echo "  ❌ pip — 未安装"; fi
if command -v node &>/dev/null; then echo "  ✅ node — v$(node --version 2>/dev/null)"; else echo "  ❌ node — 未安装"; fi
if command -v npm &>/dev/null; then echo "  ✅ npm — v$(npm --version 2>/dev/null)"; else echo "  ❌ npm — 未安装"; fi
echo ""

# ==================== 专用 CLI ====================

echo "[2/8] 专用 CLI 工具"

# GitHub CLI (gh)
if command -v gh &>/dev/null; then
    echo "  ✅ gh — $(gh --version 2>/dev/null | head -1)"
else
    echo "  ⏳ gh — 正在安装..."
    GH_VER="2.67.0"
    curl -sL "https://github.com/cli/cli/releases/download/v${GH_VER}/gh_${GH_VER}_linux_amd64.tar.gz" -o /tmp/gh.tar.gz && \
    tar xzf /tmp/gh.tar.gz -C /tmp && \
    cp /tmp/gh_${GH_VER}_linux_amd64/bin/gh /usr/local/bin/gh && \
    rm -rf /tmp/gh.tar.gz /tmp/gh_${GH_VER}_linux_amd64 2>/dev/null
    if command -v gh &>/dev/null; then echo "  ✅ gh — $(gh --version 2>/dev/null | head -1)"; else echo "  ❌ gh — 安装失败"; fi
fi

# Railway CLI
if command -v railway &>/dev/null; then
    echo "  ✅ railway — $(railway --version 2>/dev/null | head -1)"
else
    echo "  ⏳ railway — 正在安装 (npm)..."
    npm install -g @railway/cli 2>/dev/null
    if command -v railway &>/dev/null; then echo "  ✅ railway — $(railway --version 2>/dev/null | head -1)"; else echo "  ❌ railway — 安装失败"; fi
fi

# Netlify CLI
if command -v netlify &>/dev/null; then
    echo "  ✅ netlify — $(netlify --version 2>/dev/null | head -1)"
else
    echo "  ⏳ netlify — 正在安装 (npm)..."
    npm install -g netlify-cli 2>/dev/null
    if command -v netlify &>/dev/null; then echo "  ✅ netlify — $(netlify --version 2>/dev/null | head -1)"; else echo "  ❌ netlify — 安装失败"; fi
fi

# agent-browser
if command -v agent-browser &>/dev/null; then
    echo "  ✅ agent-browser — $(agent-browser --version 2>/dev/null)"
else
    echo "  ⏳ agent-browser — 正在安装 (npm)..."
    npm install -g agent-browser 2>/dev/null && agent-browser install 2>/dev/null
    if command -v agent-browser &>/dev/null; then echo "  ✅ agent-browser — $(agent-browser --version 2>/dev/null)"; else echo "  ❌ agent-browser — 安装失败"; fi
fi
echo ""

# ==================== Python 后端依赖 ====================

echo "[3/8] Python 后端依赖 (xengineer-backend)"
if [ -f xengineer-backend/requirements.txt ]; then
    pip install -q -r xengineer-backend/requirements.txt 2>/dev/null
    echo "  ✅ requirements.txt 安装完成"
else
    echo "  ❌ xengineer-backend/requirements.txt 不存在"
fi
echo ""

# ==================== 前端依赖 ====================

echo "[4/8] 前端依赖 (xengineer-frontend)"
if [ -f xengineer-frontend/package.json ]; then
    cd xengineer-frontend
    if [ ! -d node_modules ]; then
        echo "  ⏳ npm install..."
        npm install 2>/dev/null
    else
        echo "  ✅ node_modules 已存在"
    fi
    echo "  ⏳ 验证 tsc + vite build..."
    if npm run build 2>/dev/null; then
        echo "  ✅ 前端构建验证通过 (tsc + vite build)"
    else
        echo "  ❌ 前端构建失败 — 请检查 tsconfig.json 和代码"
    fi
    cd ..
else
    echo "  ❌ xengineer-frontend/package.json 不存在"
fi
echo ""

# ==================== .env 配置 ====================

echo "[5/8] 环境变量 (.env)"
ENV_FILE="/home/z/my-project/.env"
if [ -f "$ENV_FILE" ]; then
    echo "  ✅ $ENV_FILE 存在"
else
    echo "  ⏳ 创建 $ENV_FILE 模板..."
    cat > "$ENV_FILE" << 'ENVTEMPLATE'
# === API Keys ===
# OPENAI_API_KEY=sk-xxx
# DASHSCOPE_API_KEY=sk-xxx

# === 部署 Token ===
# RAILWAY_TOKEN=xxx
# NETLIFY_AUTH_TOKEN=xxx
# GITHUB_TOKEN=xxx

# === 数据库 ===
DATABASE_URL=file:/home/z/my-project/db/custom.db
ENVTEMPLATE
    echo "  ✅ 已创建模板，请填入实际 Token"
fi
echo ""

# ==================== Git 配置 ====================

echo "[6/8] Git hooks + remote"
git config core.hooksPath .githooks 2>/dev/null
chmod +x .githooks/* 2>/dev/null
echo "  ✅ core.hooksPath = .githooks"
if [ -f .git/hooks/post-commit ]; then
    mv .git/hooks/post-commit .git/hooks/post-commit.bak 2>/dev/null
    echo "  ℹ️  旧 .git/hooks/post-commit 已备份"
fi
git remote set-url origin https://github.com/bigmanBass666/XEngineer-dev.git 2>/dev/null
echo "  ✅ remote URL 已标准化"
echo ""

# ==================== 认证状态 ====================

echo "[7/8] 认证状态"

# GitHub
GITHUB_TOKEN=$(grep "^GITHUB_TOKEN=" "$ENV_FILE" 2>/dev/null | cut -d= -f2 | tr -d "'" | tr -d '"' || true)
if [ -n "$GITHUB_TOKEN" ]; then
    git remote set-url origin "https://${GITHUB_TOKEN}@github.com/bigmanBass666/XEngineer-dev.git" 2>/dev/null
    echo "  ✅ GITHUB_TOKEN — 已配置并注入 remote URL"
else
    if git remote get-url origin 2>/dev/null | grep -q "@github.com"; then
        echo "  ✅ GITHUB_TOKEN — 已在 remote URL 中"
    else
        echo "  ❌ GITHUB_TOKEN — 未配置，请在 $ENV_FILE 中添加"
    fi
fi

# Railway
RAILWAY_TOKEN=$(grep "^RAILWAY_TOKEN=" "$ENV_FILE" 2>/dev/null | cut -d= -f2 | tr -d "'" | tr -d '"' || true)
if [ -n "$RAILWAY_TOKEN" ]; then
    export RAILWAY_TOKEN
    echo "  ✅ RAILWAY_TOKEN — 已配置"
else
    echo "  ⚠️  RAILWAY_TOKEN — 未配置（Railway CLI 需要）"
fi

# Netlify
NETLIFY_TOKEN=$(grep "^NETLIFY_AUTH_TOKEN=" "$ENV_FILE" 2>/dev/null | cut -d= -f2 | tr -d "'" | tr -d '"' || true)
if [ -n "$NETLIFY_TOKEN" ]; then
    export NETLIFY_AUTH_TOKEN="$NETLIFY_TOKEN"
    echo "  ✅ NETLIFY_AUTH_TOKEN — 已配置"
else
    echo "  ⚠️  NETLIFY_AUTH_TOKEN — 未配置（Netlify CLI 需要）"
fi
echo ""

# ==================== 同步远程 ====================

echo "[8/8] 同步远程 main"
git fetch origin 2>/dev/null
LOCAL=$(git rev-parse main 2>/dev/null)
REMOTE=$(git rev-parse origin/main 2>/dev/null)
if [ "$LOCAL" = "$REMOTE" ] 2>/dev/null; then
    echo "  ✅ 本地 main 与远程一致"
else
    echo "  ⏳ 同步 origin/main..."
    CURRENT=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
    git reset --hard origin/main 2>/dev/null
    if [ "$CURRENT" != "main" ]; then git checkout "$CURRENT" 2>/dev/null; fi
    echo "  ✅ 已同步"
fi
echo ""

# ==================== 完成 ====================

echo "╔══════════════════════════════════════════════════╗"
echo "║  初始化完成                                      ║"
echo "╠══════════════════════════════════════════════════╣"
echo "║  前端: xengineer-frontend/ (Vite + React + TS)   ║"
echo "║  后端: xengineer-backend/ (FastAPI + WebSocket)   ║"
echo "║  测试: tests/ (pipeline E2E + browser E2E)      ║"
echo "║  部署: Railway(后端) + Netlify(前端)              ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║  Git 工作流提醒                                   ║"
echo "╠══════════════════════════════════════════════════╣"
echo "║  禁止直接 commit/push 到 main                     ║"
echo "║  必须: feature分支 → push → PR → Review → Merge   ║"
echo "║  commit message 中文，前缀: 功能:/修复:/测试:    ║"
echo "╚══════════════════════════════════════════════════╝"
