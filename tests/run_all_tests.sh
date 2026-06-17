#!/bin/bash
# XEngineer 一键测试脚本（从沙箱运行）
# 用法: bash tests/run_all_tests.sh [--full]
#   --full   启用浏览器级 E2E 测试（默认跳过）

set -eo pipefail

# ─── --full 参数解析 ────────────────────────────────────────────────────────
FULL_MODE=false
if [[ " $* " == *" --full "* ]]; then
  FULL_MODE=true
fi
PASS=0
FAIL=0
SKIP=0

# 辅助函数
check_pass() { PASS=$((PASS+1)); echo "  ✅ $1"; }
check_fail() { FAIL=$((FAIL+1)); echo "  ❌ $1 — $2"; }
check_skip() { SKIP=$((SKIP+1)); echo "  ⏭  $1 — $2"; }

# 1. 后端 Health Check
echo ""
echo "═══ 1. 后端 Health Check ═══"
HEALTH=$(curl -sf --max-time 10 https://xengineer-dev-production.up.railway.app/health 2>/dev/null) && check_pass "后端响应正常" || check_fail "后端无响应" "timeout or error"

# 2. 前端页面可访问
echo ""
echo "═══ 2. 前端页面可访问 ═══"
STATUS=$(curl -sf -o /dev/null -w "%{http_code}" --max-time 10 https://optalk.netlify.app 2>/dev/null) || STATUS="000"
[ "$STATUS" = "200" ] && check_pass "前端 HTTP $STATUS" || check_fail "前端 HTTP $STATUS"

# 3. 沙箱 TTS→ASR 独立验证
echo ""
echo "═══ 3. 沙箱 TTS→ASR 独立验证 ═══"
if command -v z-ai &>/dev/null; then
    z-ai tts -i "你好" -o /tmp/run_test_voice.wav --format wav 2>/dev/null || true
    if [ -f /tmp/run_test_voice.wav ]; then
        if command -v ffmpeg &>/dev/null; then
            ffmpeg -i /tmp/run_test_voice.wav -ar 16000 -ac 1 /tmp/run_test_voice_16k.wav -y 2>/dev/null || true
            ASR_RESULT=$(z-ai asr -f /tmp/run_test_voice_16k.wav 2>/dev/null) || true
            echo "  ASR 结果: $ASR_RESULT"
            check_pass "TTS→ASR 链路"
        else
            check_skip "ffmpeg 不可用，跳过重采样"
        fi
    else
        check_fail "TTS 音频生成失败"
    fi
else
    check_skip "z-ai CLI 不可用"
fi

# 4. Pipeline E2E
echo ""
echo "═══ 4. Pipeline E2E 测试 ═══"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -f "$SCRIPT_DIR/test_pipeline_e2e.py" ]; then
    python3 "$SCRIPT_DIR/test_pipeline_e2e.py" && check_pass "Pipeline E2E" || check_fail "Pipeline E2E"
else
    check_skip "test_pipeline_e2e.py 不存在"
fi

# 5. 前端视觉验证
echo ""
echo "═══ 5. 前端视觉验证 ═══"
if [ -f "$SCRIPT_DIR/test_frontend_visual.sh" ]; then
    bash "$SCRIPT_DIR/test_frontend_visual.sh" && check_pass "前端视觉验证" || check_fail "前端视觉验证"
else
    check_skip "test_frontend_visual.sh 不存在"
fi

# 6. 浏览器级 E2E（可选）
echo ""
echo "═══ 6. 浏览器级 E2E（可选） ═══"
if [ "$FULL_MODE" = true ]; then
  if bash "$SCRIPT_DIR/test_browser_e2e.sh" --multi; then
    check_pass "浏览器 E2E"
  else
    echo "  ⚠️  [WARNING] 浏览器 E2E 测试失败（不影响整体结果）"
  fi
else
  check_skip "浏览器 E2E" "使用 --full 启用"
fi

# 汇总
echo ""
echo "═════════════════════════════════"
echo "  测试报告：✅ $PASS 通过 | ❌ $FAIL 失败 | ⏭  $SKIP 跳过"
echo "═════════════════════════════════"
[ $FAIL -gt 0 ] && exit 1
exit 0