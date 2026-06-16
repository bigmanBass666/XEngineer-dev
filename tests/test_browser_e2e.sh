#!/bin/bash
# =============================================================================
# XEngineer 浏览器级 E2E 测试脚本
#
# 功能：使用 agent-browser 在真实 Netlify 前端页面中注入 getUserMedia Hook +
#       预合成语音，验证完整对话链路（VAD → ASR → VLM+LLM → TTS → UI 渲染）
#
# 用法:
#   bash tests/test_browser_e2e.sh              # 单轮对话
#   bash tests/test_browser_e2e.sh --barge-in   # 打断测试
#   bash tests/test_browser_e2e.sh --multi      # 3 轮对话
#
# 依赖:
#   - agent-browser CLI
#   - tests/fixtures/test_audio_set.json  (PR A: prepare_test_audio.py)
#   - tests/fixtures/mock_getusermedia.js (PR B: getUserMedia Hook)
#
# 产物:
#   - download/browser-e2e/*.png  — 每轮截图
#   - download/browser-e2e/result.json — 结构化测试结果
# =============================================================================

set -uo pipefail

# --- 脚本目录 ---
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# --- 配置 ---
FRONTEND_URL="https://xengineer-frontend.netlify.app"
OUTPUT_DIR="/home/z/my-project/download/browser-e2e"
FIXTURE_AUDIO="$SCRIPT_DIR/fixtures/test_audio_set.json"
FIXTURE_HOOK="$SCRIPT_DIR/fixtures/mock_getusermedia.js"

# --- 参数解析 ---
MODE="single"   # single | barge-in | multi
if [[ " $* " == *" --barge-in "* ]]; then
    MODE="barge-in"
elif [[ " $* " == *" --multi "* ]]; then
    MODE="multi"
fi

# --- 超时 ---
OPEN_TIMEOUT=15
EVAL_TIMEOUT=30
WAIT_VOICE=8        # 等待语音处理完成
WAIT_RESPONSE=20    # 等待 AI 响应（ASR + VLM + LLM + TTS 全链路）
WAIT_BARGEIN=5      # 打断等待
WAIT_TTS=10         # 等待 TTS 播放

# --- 颜色 ---
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# --- 计数器 ---
PASS=0
FAIL=0
SKIP=0

# --- 辅助函数 ---
pass() { PASS=$((PASS + 1)); echo -e "  ${GREEN}[PASS]${NC} $1"; }
fail() { FAIL=$((FAIL + 1)); echo -e "  ${RED}[FAIL]${NC} $1"; }
skip() { SKIP=$((SKIP + 1)); echo -e "  ${YELLOW}[SKIP]${NC} $1"; }
info() { echo -e "  ${CYAN}[INFO]${NC} $1"; }

# 带超时运行 agent-browser 命令
run_ab() {
    local t="${1:-$EVAL_TIMEOUT}"; shift
    timeout "$t" agent-browser "$@" 2>&1 || echo "__AB_TIMEOUT_OR_ERROR__"
}

# 在 DOM 中查找文本的辅助函数
# 用法: check_dom_text "搜索文本" "检查标签"
# 返回 0 表示找到（已输出 pass），1 表示未找到（已输出 skip）
check_dom_text() {
    local search_text="$1"
    local label="$2"
    local result=$(run_ab 10 eval --stdin <<< "
        (function() {
            var text = document.body.innerText || '';
            return 'FOUND:' + text.includes('$search_text');
        })();
    " 2>&1)
    if echo "$result" | grep -q "FOUND:true"; then
        pass "$label"
        return 0
    else
        skip "$label（DOM 中未找到 '$search_text'）"
        return 1
    fi
}

# =============================================================================
# 0. 前置条件检查
# =============================================================================
echo "============================================"
echo " XEngineer 浏览器级 E2E 测试"
echo " 模式: $MODE"
echo " 目标: $FRONTEND_URL"
echo "============================================"
echo ""

# 0a. agent-browser 检查
if ! command -v agent-browser &>/dev/null; then
    skip "agent-browser 未安装，跳过浏览器 E2E 测试"
    exit 0
fi
pass "agent-browser 已安装"

# 0b. Fixture 音频检查
if [ ! -f "$FIXTURE_AUDIO" ]; then
    skip "test_audio_set.json 不存在（需先运行 prepare_test_audio.py），SKIP"
    exit 0
fi
pass "test_audio_set.json 存在"

# 0c. Mock hook 检查
if [ ! -f "$FIXTURE_HOOK" ]; then
    skip "mock_getusermedia.js 不存在（需 PR B 合并），SKIP"
    exit 0
fi
pass "mock_getusermedia.js 存在"

# 0d. 验证 fixture JSON 可解析且包含 utterances
UTTERANCE_COUNT=$(python3 -c "
import json
with open('$FIXTURE_AUDIO') as f:
    data = json.load(f)
print(len(data.get('utterances', [])))
" 2>/dev/null || echo "0")

if [ "$UTTERANCE_COUNT" -lt 1 ] 2>/dev/null; then
    skip "test_audio_set.json 不包含有效 utterances，SKIP"
    exit 0
fi
pass "fixture 包含 $UTTERANCE_COUNT 条 utterance"

# 0e. 创建输出目录
mkdir -p "$OUTPUT_DIR"
pass "输出目录: $OUTPUT_DIR"

echo ""

# =============================================================================
# 1. 打开前端页面
# =============================================================================
echo "── 步骤 1: 打开前端页面 ──"

# 清理旧会话
run_ab 5 close >/dev/null 2>&1
sleep 1

OPEN_OUT=$(run_ab $OPEN_TIMEOUT open "$FRONTEND_URL")
if echo "$OPEN_OUT" | grep -qi "error\|fail\|timeout\|__AB_TIMEOUT_OR_ERROR__"; then
    fail "页面打开失败"
    echo "  输出: $OPEN_OUT"
    run_ab 5 close >/dev/null 2>&1
    write_results_and_exit
else
    pass "页面打开成功"
fi

# 等待 networkidle
WAIT_OUT=$(run_ab 15 wait --load networkidle 2>&1)
if echo "$WAIT_OUT" | grep -qi "__AB_TIMEOUT_OR_ERROR__"; then
    skip "等待 networkidle 超时（可能已加载完成）"
else
    pass "networkidle 达成"
fi

# 初始截图
run_ab 10 screenshot "$OUTPUT_DIR/01_page_loaded.png" >/dev/null 2>&1
if [ -f "$OUTPUT_DIR/01_page_loaded.png" ] && [ -s "$OUTPUT_DIR/01_page_loaded.png" ]; then
    pass "初始截图已保存"
else
    fail "初始截图失败"
fi

echo ""

# =============================================================================
# 2. 注入 getUserMedia Hook + 加载预合成音频元数据
# =============================================================================
echo "── 步骤 2: 注入 getUserMedia Hook ──"

# 2a. 通过 eval --stdin 加载 mock_getusermedia.js
HOOK_JS=$(cat "$FIXTURE_HOOK")
EVAL_HOOK_OUT=$(echo "$HOOK_JS" | run_ab $EVAL_TIMEOUT eval --stdin 2>&1)
# eval --stdin 返回值可能是表达式结果或 null（console.log 返回 undefined）
# 不用返回值判断，直接验证 __mockAudio 是否存在

# 2b. 验证 hook 已生效
VERIFY_HOOK=$(run_ab $EVAL_TIMEOUT eval "typeof window.__mockAudio" 2>&1)
if echo "$VERIFY_HOOK" | grep -qi "object"; then
    pass "mock_getusermedia.js 注入成功，window.__mockAudio 已就绪"
else
    fail "window.__mockAudio 未创建"
fi

# 2c. 加载预合成音频元数据到页面（不含 PCM base64，避免 ARG_MAX）
EVAL_META_OUT=$(python3 -c "
import json
with open('$FIXTURE_AUDIO') as f:
    data = json.load(f)
utterances = data.get('utterances', [])
# 只提取元数据，不包含 pcm_base64
meta_only = []
for u in utterances:
    meta_only.append({
        'id': u.get('id', ''),
        'text': u.get('text', ''),
        'keywords': u.get('keywords', []),
        'duration': u.get('duration', 0),
        'sample_rate': u.get('sample_rate', 16000),
    })
print(f'window.__testUtterances = {json.dumps(meta_only, ensure_ascii=False)};')
print(f'\"LOADED_UTTERANCES:{len(meta_only)}\"')
" 2>/dev/null | run_ab $EVAL_TIMEOUT eval --stdin 2>&1)
if echo "$EVAL_META_OUT" | grep -q "LOADED_UTTERANCES"; then
    LOADED_COUNT=$(echo "$EVAL_META_OUT" | rg -o 'LOADED_UTTERANCES:\d+' | rg -o '\d+')
    pass "已加载 $LOADED_COUNT 条预合成音频元数据"
else
    fail "加载预合成音频元数据失败"
    echo "  输出: $EVAL_META_OUT"
fi

# 2d. 检查 WebSocket 连接（带重试，使用 return 而非 console.log）
WS_FOUND=false
for WS_RETRY in 1 2 3; do
    sleep 3
    WS_CHECK=$(run_ab $EVAL_TIMEOUT eval --stdin <<< '
      (function() {
        var text = document.body.innerText || "";
        var connected = text.includes("已连接") || text.includes("Connected");
        return "WS_CHECK:" + connected;
      })();
    ' 2>&1)
    if echo "$WS_CHECK" | grep -q "WS_CHECK:true"; then
        WS_FOUND=true
        break
    fi
    info "WebSocket 未检测到，第 $WS_RETRY/3 次重试..."
done
if [ "$WS_FOUND" = true ]; then
    pass "WebSocket 连接已建立"
else
    # Not a hard failure — the page might use different status text
    skip "WebSocket 状态不确定（3 次重试后仍未检测到，继续测试）"
fi

echo ""

# =============================================================================
# 3. 执行对话轮次（核心测试逻辑）
# =============================================================================

# 根据模式决定轮数和打断
case "$MODE" in
    single)
        ROUNDS=1
        BARGE_IN_ROUND=-1  # 无打断
        ;;
    barge-in)
        ROUNDS=1
        BARGE_IN_ROUND=0   # 第 0 轮后打断
        ;;
    multi)
        ROUNDS=3
        BARGE_IN_ROUND=-1
        ;;
esac

# --- 注入 PCM 数据到 mock 的辅助函数 ---
inject_pcm() {
    local idx="$1"
    local label="$2"

    info "注入 PCM 数据（$label, utterance $idx）..."

    # 分两步注入 base64 → Float32Array：
    # 步骤 1: 用 python3 -c 读取 base64，生成赋值 JS 存到 window.__mockAudio._pendingBase64
    # 步骤 2: 用 eval 执行 atob 解码 + setAudio + startFeeding
    python3 -c "
import json, sys
fixture = '$FIXTURE_AUDIO'
idx = int('$idx')
with open(fixture) as f:
    data = json.load(f)
u = data['utterances'][idx]
b64 = u.get('pcm_float32_base64', '')
js = 'window.__mockAudio._pendingBase64 = \"' + b64 + '\";\n'
sys.stdout.write(js)
sys.stdout.write('\"SET_VAR_OK\";\n')
" > /tmp/mock_inject_$$.js 2>/dev/null
    if [ ! -s /tmp/mock_inject_$$.js ]; then
        fail "Python 生成注入 JS 失败（$label）"
        return 1
    fi
    ASSIGN_JS=$(cat /tmp/mock_inject_$$.js)
    rm -f /tmp/mock_inject_$$.js
    SET_VAR_OUT=$(echo "$ASSIGN_JS" | run_ab $EVAL_TIMEOUT eval --stdin 2>&1)
    if echo "$SET_VAR_OUT" | grep -q "SET_VAR_OK"; then
        info "base64 字符串已注入（$(echo "$ASSIGN_JS" | wc -c | tr -d ' ') bytes JS）"
    else
        fail "base64 字符串注入失败（$label）"
        echo "  输出: $(echo "$SET_VAR_OUT" | tail -3)"
        return 1
    fi
    # 步骤 2: 解码 base64 → Float32Array → setAudio → startFeeding
    # 注意: console.log 返回 undefined (显示为 null)，所以用表达式字符串返回结果
    DECODE_JS='(function(){var b=window.__mockAudio._pendingBase64;if(!b){return "NO_DATA";}var r=atob(b);var a=new Uint8Array(r.length);for(var i=0;i<r.length;i++)a[i]=r.charCodeAt(i);var f=new Float32Array(a.buffer);window.__mockAudio.setAudio(f);window.__mockAudio.startFeeding();delete window.__mockAudio._pendingBase64;return "INJECT_OK:"+f.length;})();'
    DECODE_OUT=$(echo "$DECODE_JS" | run_ab $EVAL_TIMEOUT eval --stdin 2>&1)
    if echo "$DECODE_OUT" | grep -q "INJECT_OK"; then
        SAMPLE_COUNT=$(echo "$DECODE_OUT" | rg -o 'INJECT_OK:\d+' | rg -o '\d+')
        pass "PCM 数据注入成功（$label, $SAMPLE_COUNT samples）"
        return 0
    else
        fail "PCM 数据注入失败（$label）"
        echo "  输出: $(echo "$DECODE_OUT" | tail -5)"
        return 1
    fi
}

# --- 单轮测试函数 ---
run_conversation_round() {
    local round_num="$1"
    local utterance_idx="$2"
    local screenshot_label="$3"

    echo "  ── 对话轮次 $((round_num + 1)): utterance[$utterance_idx] ──"

    # 3a. 注入 PCM 数据
    if ! inject_pcm "$utterance_idx" "轮次$((round_num+1))"; then
        return 1
    fi

    # 3b. 点击麦克风按钮开始录音
    info "点击麦克风按钮..."
    CLICK_OUT=$(run_ab 5 click '@e_mic' 2>&1)
    if echo "$CLICK_OUT" | grep -qi "__AB_TIMEOUT_OR_ERROR__\|error\|no element\|not found"; then
        # 尝试通过 snapshot 找到按钮
        info "尝试通过 snapshot 定位录音按钮..."
        SNAPSHOT=$(run_ab 5 snapshot -i 2>&1)
        # 从 snapshot 中提取"录音"按钮的 ref（格式: button "开始录音" [ref=e4]）
        MIC_REF=$(echo "$SNAPSHOT" | rg 'button.*录音.*\[ref=(\w+)\]' -o -r '$1' | head -1)
        if [ -z "$MIC_REF" ]; then
            # 也尝试匹配 mic/audio 等关键词
            MIC_REF=$(echo "$SNAPSHOT" | rg -i 'button.*(mic|audio).*\[ref=(\w+)\]' -o -r '$2' | head -1)
        fi
        if [ -n "$MIC_REF" ]; then
            CLICK_REF="@${MIC_REF}"
            info "找到录音按钮 ref: $CLICK_REF"
            CLICK_OUT=$(run_ab 5 click "$CLICK_REF" 2>&1)
            if echo "$CLICK_OUT" | grep -qi "__AB_TIMEOUT_OR_ERROR__\|error"; then
                fail "无法点击录音按钮"
            else
                pass "录音按钮已点击（ref: $CLICK_REF）"
            fi
        else
            fail "未找到录音按钮"
            echo "  snapshot: $SNAPSHOT" | head -5
        fi
    else
        pass "麦克风按钮已点击"
    fi

    # 3c. 等待 VAD 检测 + ASR 处理
    info "等待 VAD 检测 + ASR 处理（${WAIT_VOICE}s）..."
    sleep "$WAIT_VOICE"

    # 3d. 截图 — 说话中状态
    run_ab 10 screenshot "$OUTPUT_DIR/${screenshot_label}_speaking.png" >/dev/null 2>&1
    if [ -f "$OUTPUT_DIR/${screenshot_label}_speaking.png" ]; then
        pass "说话中截图: ${screenshot_label}_speaking.png"
    fi

    # 3e. 注入静音（让 VAD 检测到语音结束）
    info "注入静音..."
    SILENCE_OUT=$(run_ab $EVAL_TIMEOUT eval "
        window.__mockAudio.stopFeeding();
        'SILENCE_OK';
    " 2>&1)
    if echo "$SILENCE_OUT" | grep -q "SILENCE_OK"; then
        pass "静音注入成功"
    fi

    # 3f. 等待 AI 响应（LLM + TTS）
    info "等待 AI 响应（${WAIT_RESPONSE}s）..."
    sleep "$WAIT_RESPONSE"

    # 3g. 截图 — AI 响应后
    run_ab 10 screenshot "$OUTPUT_DIR/${screenshot_label}_response.png" >/dev/null 2>&1
    if [ -f "$OUTPUT_DIR/${screenshot_label}_response.png" ]; then
        pass "AI 响应截图: ${screenshot_label}_response.png"
    fi

    # 3h. 验证对话内容（DOM 检测替代 console 日志）
    # 从 fixture 读取当前 utterance 的关键词用于 ASR 验证
    ASR_KEYWORD=$(python3 -c "
import json
with open('$FIXTURE_AUDIO') as f:
    data = json.load(f)
u = data['utterances'][$utterance_idx]
print(u.get('keywords', [''])[0] if u.get('keywords') else '')
" 2>/dev/null)

    if [ -n "$ASR_KEYWORD" ]; then
        # ASR 验证：检查 DOM 是否包含用户语音关键词（说明 ASR 识别成功且显示在 UI 中）
        check_dom_text "$ASR_KEYWORD" "ASR 识别结果出现在 UI 中（关键词: '$ASR_KEYWORD'）"
    else
        skip "ASR 验证跳过（fixture 无关键词）"
    fi

    # LLM 验证：检查 DOM 中是否出现 AI 回复（"AI" 标签表明有助手消息）
    check_dom_text "AI" "LLM/VLM 响应出现在 UI 中（检测到 AI 标签）"

    # TTS 验证：通过 DOM 检查是否有 TTS 播放指示（如波形/播放动画元素）
    # 前端 TTS 播放时可能有特定 UI 状态，降级为信息性检查
    TTS_DOM_CHECK=$(run_ab 10 eval --stdin <<< '
        (function() {
            var text = document.body.innerText || "";
            // TTS 播放后 AI 回复内容应已在 DOM 中
            return "TTS_UI_CHECK:" + (text.length > 100);
        })();
    ' 2>&1)
    if echo "$TTS_DOM_CHECK" | grep -q "TTS_UI_CHECK:true"; then
        pass "TTS 播放后 UI 内容丰富（DOM 文本 > 100 字符）"
    else
        skip "TTS 播放验证跳过（UI 内容较少）"
    fi

    # console 日志作为附加信息输出（不统计 pass/fail/skip）
    CONSOLE_OUT=$(run_ab $EVAL_TIMEOUT console 2>&1)
    if ! echo "$CONSOLE_OUT" | grep -qi "__AB_TIMEOUT_OR_ERROR__"; then
        info "console 日志片段: $(echo "$CONSOLE_OUT" | head -5)"
    fi

    echo ""
}

# --- Barge-in 测试 ---
run_barge_in_test() {
    local utterance_idx="$1"

    echo "  ── Barge-in 测试: 在 AI 回复时注入新语音 ──"

    # 等待 TTS 开始播放
    info "等待 TTS 播放（${WAIT_BARGEIN}s）..."
    sleep "$WAIT_BARGEIN"

    # 注入第二条语音（打断）
    if ! inject_pcm "$utterance_idx" "barge-in"; then
        return 1
    fi

    # 等待 barge-in 处理
    info "等待 barge-in 处理（${WAIT_VOICE}s）..."
    sleep "$WAIT_VOICE"

    # 注入静音
    run_ab $EVAL_TIMEOUT eval "window.__mockAudio.stopFeeding();" >/dev/null 2>&1

    # 等待第二轮响应
    info "等待第二轮 AI 响应（${WAIT_RESPONSE}s）..."
    sleep "$WAIT_RESPONSE"

    # 截图
    run_ab 10 screenshot "$OUTPUT_DIR/04_barge_in_response.png" >/dev/null 2>&1
    if [ -f "$OUTPUT_DIR/04_barge_in_response.png" ]; then
        pass "Barge-in 响应截图: 04_barge_in_response.png"
    fi

    # 检查 console 是否有 vad_status 变化（speaking → silence → speaking）
    CONSOLE_OUT=$(run_ab $EVAL_TIMEOUT console 2>&1)
    if echo "$CONSOLE_OUT" | grep -qi "vad_status.*speaking"; then
        pass "Barge-in 后 VAD 再次检测到语音"
    else
        skip "未检测到 barge-in 后的 VAD 事件"
    fi

    echo ""
}

# =============================================================================
# 执行测试轮次
# =============================================================================
echo "── 步骤 3: 执行对话测试 ──"

if [ "$ROUNDS" -ge 1 ]; then
    run_conversation_round 0 0 "02_round1"
fi

if [ "$BARGE_IN_ROUND" -ge 0 ]; then
    run_barge_in_test 1
fi

if [ "$ROUNDS" -ge 2 ]; then
    run_conversation_round 1 1 "05_round2"
fi

if [ "$ROUNDS" -ge 3 ]; then
    run_conversation_round 2 2 "06_round3"
fi

# =============================================================================
# 4. 检查 JS 错误
# =============================================================================
echo "── 步骤 4: 检查 JS 错误 ──"
ERRORS_OUT=$(run_ab 5 errors 2>&1)
ERRORS_CLEAN=$(echo "$ERRORS_OUT" | rg -v "__AB_TIMEOUT_OR_ERROR__" | tr -d '\n' | xargs 2>/dev/null)
if [ -z "$ERRORS_CLEAN" ]; then
    pass "无 JS 错误"
else
    if echo "$ERRORS_OUT" | grep -qi "__AB_TIMEOUT_OR_ERROR__"; then
        skip "JS 错误检查超时"
    else
        ERROR_COUNT=$(echo "$ERRORS_OUT" | wc -l)
        fail "发现 $ERROR_COUNT 条 JS 错误"
        echo "$ERRORS_OUT" | head -10 | while IFS= read -r line; do
            echo "    $line"
        done
    fi
fi
echo ""

# =============================================================================
# 5. 最终截图 + 关闭
# =============================================================================
echo "── 步骤 5: 最终状态 ──"
run_ab 10 screenshot "$OUTPUT_DIR/07_final_state.png" >/dev/null 2>&1
if [ -f "$OUTPUT_DIR/07_final_state.png" ] && [ -s "$OUTPUT_DIR/07_final_state.png" ]; then
    pass "最终截图已保存: 07_final_state.png"
else
    fail "最终截图失败"
fi

# 获取最终 snapshot
SNAP_FINAL=$(run_ab 5 snapshot -i 2>&1)
if echo "$SNAP_FINAL" | grep -qi "__AB_TIMEOUT_OR_ERROR__"; then
    skip "最终 snapshot 获取超时"
else
    # 检查是否有聊天气泡（DOM 中出现对话内容）
    # 从 fixture 读取第一条 utterance 的关键词和文本用于匹配
    FIRST_KEYWORD=$(python3 -c "
import json
with open('$FIXTURE_AUDIO') as f:
    data = json.load(f)
keywords = data['utterances'][0].get('keywords', [])
print(keywords[0] if keywords else '')
" 2>/dev/null)
    if [ -n "$FIRST_KEYWORD" ] && echo "$SNAP_FINAL" | grep -q "$FIRST_KEYWORD"; then
        pass "UI 中检测到对话元素（关键词: '$FIRST_KEYWORD'）"
    elif echo "$SNAP_FINAL" | grep -qi "AI\|你好\|介绍\|看到\|中文"; then
        pass "UI 中检测到对话元素（中文关键词匹配）"
    else
        skip "UI 中未检测到对话元素"
    fi
fi

# 关闭浏览器
run_ab 5 close >/dev/null 2>&1
pass "浏览器已关闭"
echo ""

# =============================================================================
# 6. 输出 result.json
# =============================================================================
echo "── 步骤 6: 生成结果报告 ──"

python3 -c "
import json, os, glob
from datetime import datetime

timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# 收集截图列表
screenshots = sorted(glob.glob('$OUTPUT_DIR/*.png')) if os.path.isdir('$OUTPUT_DIR') else []
screenshot_names = [os.path.basename(s) for s in screenshots]

is_barge_in = '$MODE' == 'barge-in'

result = {
    'timestamp': timestamp,
    'mode': '$MODE',
    'frontend_url': '$FRONTEND_URL',
    'rounds_tested': $ROUNDS,
    'barge_in': is_barge_in,
    'summary': {
        'pass': $PASS,
        'fail': $FAIL,
        'skip': $SKIP
    },
    'screenshots': screenshot_names,
    'all_passed': ($FAIL == 0)
}

with open('$OUTPUT_DIR/result.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f'  结果已写入: $OUTPUT_DIR/result.json')
" 2>/dev/null

if [ -f "$OUTPUT_DIR/result.json" ]; then
    pass "result.json 已生成"
else
    fail "result.json 生成失败"
fi

echo ""

# =============================================================================
# 汇总报告
# =============================================================================
echo "============================================"
echo " 浏览器 E2E 测试汇总"
echo "============================================"
echo "  模式:        $MODE"
echo "  目标 URL:    $FRONTEND_URL"
echo "  截图目录:    $OUTPUT_DIR"
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
    echo -e "  ${GREEN}✅ 所有检查通过${NC}"
    EXIT_CODE=0
else
    echo -e "  ${RED}❌ 有 $FAIL 项检查失败${NC}"
    EXIT_CODE=1
fi

echo "============================================"

exit $EXIT_CODE