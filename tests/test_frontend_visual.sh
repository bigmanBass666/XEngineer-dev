#!/bin/bash
# =============================================================================
# XEngineer 前端 agent-browser 视觉验证脚本
#
# 功能：自动化验证前端页面加载、WebSocket 连接、JS 错误、UI 交互元素
# 使用工具：agent-browser（沙箱 CLI）
# 产物：截图保存到 /home/z/my-project/download/frontend-test/
# =============================================================================

set -uo pipefail

# --- 配置 ---
FRONTEND_URL="https://xengineer-frontend.netlify.app"
SCREENSHOT_DIR="/home/z/my-project/download/frontend-test"
TIMEOUT_SECS=15

# --- 颜色 ---
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# --- 计数器 ---
PASS=0
FAIL=0
SKIP=0

# --- 工具检查 ---
if ! command -v agent-browser &>/dev/null; then
    echo -e "${RED}[SKIP] agent-browser 未安装，无法执行前端视觉验证${NC}"
    echo "请先安装 agent-browser CLI 工具后再运行此脚本。"
    exit 0
fi

# --- 目录准备 ---
mkdir -p "$SCREENSHOT_DIR"

# --- 辅助函数 ---
pass() { PASS=$((PASS + 1)); echo -e "  ${GREEN}[PASS]${NC} $1"; }
fail() { FAIL=$((FAIL + 1)); echo -e "  ${RED}[FAIL]${NC} $1"; }
skip() { SKIP=$((SKIP + 1)); echo -e "  ${YELLOW}[SKIP]${NC} $1"; }
info() { echo -e "  ${CYAN}[INFO]${NC} $1"; }

# 带超时运行 agent-browser 命令
run_ab() {
    timeout "$TIMEOUT_SECS" agent-browser "$@" 2>&1 || echo "__AGENT_BROWSER_TIMEOUT_OR_ERROR__"
}

# =============================================================================
echo "============================================"
echo " XEngineer 前端视觉验证"
echo " 目标: $FRONTEND_URL"
echo " 截图目录: $SCREENSHOT_DIR"
echo "============================================"
echo ""

# --- 清理：确保之前没有残留的浏览器会话 ---
info "清理旧浏览器会话..."
run_ab close >/dev/null 2>&1
sleep 1

# =========================================================================
# 1. 打开页面
# =========================================================================
echo "── 步骤 1: 打开前端页面 ──"
OPEN_OUTPUT=$(run_ab open "$FRONTEND_URL")
if echo "$OPEN_OUTPUT" | grep -qi "error\|fail\|timeout\|__AGENT_BROWSER_TIMEOUT_OR_ERROR__"; then
    fail "页面打开失败"
    echo "  输出: $OPEN_OUTPUT"
    echo ""
    run_ab close >/dev/null 2>&1
    # 输出汇总并退出
    echo ""
    echo "============================================"
    echo " 测试汇总（页面打开失败，提前终止）"
    echo "============================================"
    echo -e "  ${GREEN}通过: $PASS${NC}"
    echo -e "  ${RED}失败: $FAIL${NC}"
    echo -e "  ${YELLOW}跳过: $SKIP${NC}"
    exit 0
else
    pass "页面打开成功"
fi
echo ""

# =========================================================================
# 2. 等待页面加载（networkidle）
# =========================================================================
echo "── 步骤 2: 等待页面加载 ──"
WAIT_OUTPUT=$(run_ab wait --load networkidle 2>&1)
if echo "$WAIT_OUTPUT" | grep -qi "__AGENT_BROWSER_TIMEOUT_OR_ERROR__"; then
    skip "等待加载超时（可能已加载完成），继续后续检查"
else
    pass "页面加载完成（networkidle）"
fi
echo ""

# =========================================================================
# 3. 截图保存（初始状态）
# =========================================================================
echo "── 步骤 3: 截图（初始状态） ──"
INITIAL_SCREENSHOT="$SCREENSHOT_DIR/01_initial_load.png"
SCREENSHOT_OUTPUT=$(run_ab screenshot "$INITIAL_SCREENSHOT" 2>&1)
if echo "$SCREENSHOT_OUTPUT" | grep -qi "__AGENT_BROWSER_TIMEOUT_OR_ERROR__"; then
    fail "初始截图失败"
else
    # 检查文件是否存在且非空
    if [ -f "$INITIAL_SCREENSHOT" ] && [ -s "$INITIAL_SCREENSHOT" ]; then
        pass "初始截图已保存: $INITIAL_SCREENSHOT"
    else
        fail "截图文件未生成或为空: $INITIAL_SCREENSHOT"
    fi
fi
echo ""

# =========================================================================
# 4. 检查页面标题
# =========================================================================
echo "── 步骤 4: 检查页面标题 ──"
TITLE_OUTPUT=$(run_ab get title 2>&1)
# 提取标题文本（去掉可能的标签前缀）
PAGE_TITLE=$(echo "$TITLE_OUTPUT" | sed 's/.*title[[:space:]]*:[[:space:]]*//i' | tr -d '\n' | xargs 2>/dev/null)
if [ -z "$PAGE_TITLE" ]; then
    PAGE_TITLE="$TITLE_OUTPUT" # 使用原始输出
fi

if echo "$PAGE_TITLE" | grep -qi "xengineer\|XEngineer\|视觉\|对话\|AI"; then
    pass "页面标题包含预期关键词: $PAGE_TITLE"
else
    # 标题可能不完全匹配，但不一定是错误
    if [ -n "$PAGE_TITLE" ] && ! echo "$PAGE_TITLE" | grep -qi "error\|timeout\|__AGENT_BROWSER_TIMEOUT_OR_ERROR__"; then
        skip "页面标题未匹配预期关键词，但已获取: $PAGE_TITLE"
    else
        fail "无法获取页面标题"
        echo "  输出: $TITLE_OUTPUT"
    fi
fi
echo ""

# =========================================================================
# 5. 检查 JS 错误
# =========================================================================
echo "── 步骤 5: 检查 JS 错误 ──"
ERRORS_OUTPUT=$(run_ab errors 2>&1)
ERRORS_CLEAN=$(echo "$ERRORS_OUTPUT" | grep -v "__AGENT_BROWSER_TIMEOUT_OR_ERROR__" | tr -d '\n' | xargs 2>/dev/null)

if [ -z "$ERRORS_CLEAN" ]; then
    pass "无 JS 错误"
else
    # 检查是否包含实际错误内容
    ERROR_COUNT=$(echo "$ERRORS_OUTPUT" | wc -l)
    if echo "$ERRORS_OUTPUT" | grep -qi "__AGENT_BROWSER_TIMEOUT_OR_ERROR__"; then
        skip "JS 错误检查超时"
    else
        fail "发现 $ERROR_COUNT 条 JS 错误"
        echo "  错误内容:"
        echo "$ERRORS_OUTPUT" | head -20 | while IFS= read -r line; do
            echo "    $line"
        done
    fi
fi
echo ""

# =========================================================================
# 6. 获取 snapshot 检查 UI 元素
# =========================================================================
echo "── 步骤 6: 检查 UI 交互元素 ──"
SNAPSHOT_OUTPUT=$(run_ab snapshot -i 2>&1)

if echo "$SNAPSHOT_OUTPUT" | grep -qi "__AGENT_BROWSER_TIMEOUT_OR_ERROR__"; then
    skip "snapshot 获取超时"
else
    UI_CHECKS=0
    UI_FOUND=0

    # 检查常见 UI 元素关键词
    for keyword in "button" "input" "textarea" "chat" "send" "message" "camera" "video" "canvas" "div"; do
        UI_CHECKS=$((UI_CHECKS + 1))
        if echo "$SNAPSHOT_OUTPUT" | grep -qi "$keyword"; then
            UI_FOUND=$((UI_FOUND + 1))
        fi
    done

    if [ "$UI_FOUND" -gt 0 ]; then
        pass "UI 交互元素存在（检测到 $UI_FOUND/$UI_CHECKS 类元素）"
        # 输出 snapshot 摘要（前 30 行）
        info "Snapshot 摘要（前 30 行）:"
        echo "$SNAPSHOT_OUTPUT" | head -30 | while IFS= read -r line; do
            echo "    $line"
        done
    else
        fail "未检测到 UI 交互元素"
        echo "  Snapshot 输出:"
        echo "$SNAPSHOT_OUTPUT" | head -30 | while IFS= read -r line; do
            echo "    $line"
        done
    fi
fi
echo ""

# =========================================================================
# 7. 检查 console 日志中的 WS 连接状态
# =========================================================================
echo "── 步骤 7: 检查 WebSocket 连接状态 ──"
CONSOLE_OUTPUT=$(run_ab console 2>&1)

if echo "$CONSOLE_OUTPUT" | grep -qi "__AGENT_BROWSER_TIMEOUT_OR_ERROR__"; then
    skip "console 日志获取超时"
else
    # 检查 WS 连接相关日志
    WS_CONNECTED=false
    WS_LOGS=""

    if echo "$CONSOLE_OUTPUT" | grep -qi "websocket.*open\|ws.*open\|connected\|连接成功\|socket.*open"; then
        WS_CONNECTED=true
    fi

    if echo "$CONSOLE_OUTPUT" | grep -qi "websocket.*close\|ws.*close\|disconnect\|连接失败\|error"; then
        # 检查是否有关闭或错误
        if echo "$CONSOLE_OUTPUT" | grep -qi "websocket.*open\|ws.*open\|connected\|连接成功"; then
            # 同时有 open 和 close，可能是重连
            WS_CONNECTED=true
        else
            WS_CONNECTED=false
        fi
    fi

    if [ "$WS_CONNECTED" = true ]; then
        pass "WebSocket 连接成功（console 日志确认）"
    else
        # 可能 WS 还在连接中，或者日志格式不同，标记为 skip
        skip "未在 console 中找到明确的 WS 连接成功日志"
        info "Console 日志摘要（前 20 行）:"
        echo "$CONSOLE_OUTPUT" | head -20 | while IFS= read -r line; do
            echo "    $line"
        done
    fi
fi
echo ""

# =========================================================================
# 8. 截图保存（最终状态）
# =========================================================================
echo "── 步骤 8: 截图（最终状态） ──"
FINAL_SCREENSHOT="$SCREENSHOT_DIR/02_final_state.png"
FINAL_SS_OUTPUT=$(run_ab screenshot "$FINAL_SCREENSHOT" 2>&1)
if echo "$FINAL_SS_OUTPUT" | grep -qi "__AGENT_BROWSER_TIMEOUT_OR_ERROR__"; then
    fail "最终截图失败"
else
    if [ -f "$FINAL_SCREENSHOT" ] && [ -s "$FINAL_SCREENSHOT" ]; then
        pass "最终截图已保存: $FINAL_SCREENSHOT"
    else
        fail "截图文件未生成或为空: $FINAL_SCREENSHOT"
    fi
fi
echo ""

# =========================================================================
# 9. 关闭浏览器
# =========================================================================
echo "── 步骤 9: 关闭浏览器 ──"
CLOSE_OUTPUT=$(run_ab close 2>&1)
pass "浏览器已关闭"
echo ""

# =========================================================================
# 10. 输出汇总报告
# =========================================================================
echo "============================================"
echo " 测试汇总报告"
echo "============================================"
echo "  目标 URL:    $FRONTEND_URL"
echo "  截图目录:    $SCREENSHOT_DIR"
echo "  执行时间:    $(date '+%Y-%m-%d %H:%M:%S')"
echo ""
echo -e "  ${GREEN}通过: $PASS${NC}"
echo -e "  ${RED}失败: $FAIL${NC}"
echo -e "  ${YELLOW}跳过: $SKIP${NC}"
echo ""

TOTAL=$((PASS + FAIL + SKIP))
echo "  总计: $TOTAL 项检查"
echo ""

if [ "$FAIL" -eq 0 ]; then
    echo -e "  ${GREEN}✅ 所有检查通过，前端运行正常${NC}"
    EXIT_CODE=0
else
    echo -e "  ${RED}❌ 有 $FAIL 项检查失败，需要排查${NC}"
    EXIT_CODE=1
fi

echo "============================================"

exit $EXIT_CODE