# 移动端音频路由修复计划

## 问题描述

用户在手机浏览器（Android Chrome / iOS Safari）上访问 optalk.netlify.app 时：

1. 语音交互正常（识别、回复、播放）
2. **但** TTS 播放期间，手机音量键显示"通话音量"（而非媒体音量）
3. 调节音量键**无法影响** TTS 实际播放音量
4. 声音本身从扬声器输出，但音量控制通道不对

### 根因

当页面**同时**满足以下两个条件时，手机 OS 会将音频会话识别为"语音通话"：

- `getUserMedia({ audio: true })` 持续活跃（麦克风采集）
- 同时播放音频（TTS `<audio>` 播放）

这导致 OS 将音量控制路由到"通话音量"通道，而非"媒体音量"通道。

---

## 技术调研结果

### 方案对比

| # | 方案 | 可靠性 | 平台支持 | 缺点 |
|---|------|--------|---------|------|
| A | TTS 播放时暂停麦克风（`track.stop()` + 释放 MediaStream） | ⭐⭐⭐⭐⭐ 最高 | Android + iOS 通用 | TTS 期间无法 VAD |
| B | `navigator.audioSession.type` 动态切换 | ⭐⭐⭐⭐ | **仅 iOS Safari 16.4+**，Android 无此 API | 不解决 Android |
| C | `echoCancellation: false` | ⭐⭐⭐ | **仅 Android Chrome**（Chromium 工程师确认） | 产生回声 |
| D | 软件音量滑块（GainNode） | ⭐⭐ | 通用，但需 UI 改动 | 不改变硬件音量行为 |
| E | `setSinkId()` | ❌ | iOS 不支持，Android 无音频输出设备列表 | 不可行 |

### 方案 A 详细分析（推荐）

**原理**：TTS 播放期间完全释放麦克风 MediaStream，让 OS 退出"通话模式"，恢复"媒体播放"模式。

**生命周期**：
```
用户说话 → VAD=speaking → 麦克风活跃
  → barge-in 打断 TTS（已有机制）
  → AI 回复 → TTS 开始播放
    → 暂停麦克风（track.stop()）
    → 音频走扬声器，音量键恢复正常
  → tts_end → 恢复麦克风（重新 getUserMedia）
```

**优点**：
- 彻底解决"通话音量"问题，Android + iOS 通用
- 与已有 barge-in 机制一致（TTS 播放时本来就不需要录音）
- 无平台兼容性问题

**缺点**：
- TTS 播放期间无法做 VAD（但 barge-in 是通过 `audioPlayer.stop()` 实现的，不依赖 VAD）
- 重新 `getUserMedia` 需要时间（约 100-500ms），可能有短暂延迟

### 方案 B 详细分析（iOS 补充）

**原理**：使用 `navigator.audioSession.type` API 控制 iOS 的音频会话类型。

**可用值**：
| 值 | 行为 |
|---|------|
| `auto` | 默认，Safari 映射为 ambient（受静音开关影响） |
| `playback` | 媒体播放，忽略静音开关，音量键正常 |
| `play-and-record` | 录音+播放同时进行（RTC 模式） |
| `transient` | 短暂通知音效 |

**关键**：必须在 `getUserMedia()` **之前**设置才有效。

**注意**：此 API **仅 iOS Safari 16.4+** 支持，Android Chrome 无此 API。

### 方案 C 详细分析（Android 补充）

**原理**：`getUserMedia({ audio: { echoCancellation: false } })` 阻止 Chrome 进入 `MODE_IN_COMMUNICATION`。

**来源**：Chromium 工程师在 [issue 40866811](https://issues.chromium.org/40866811) 确认。

**缺点**：TTS 声音会被麦克风拾取产生回声。

---

## 推荐实施方案

采用 **方案 A 为主 + 方案 B 作为 iOS 优化补充**：

### Step 1：创建 `useAudioSession` hook

新建 `xengineer-frontend/src/hooks/useAudioSession.ts`：

```typescript
/**
 * 音频会话管理 hook
 * 
 * 核心职责：
 * 1. TTS 播放时暂停麦克风（方案 A），解决"通话音量"问题
 * 2. iOS 上使用 audioSession API 优化音频路由（方案 B）
 * 3. TTS 结束后恢复麦克风
 */
```

### Step 2：修改 `AudioRecorder` / `useVAD` 支持暂停/恢复

- `AudioRecorder` 新增 `pauseMic()` / `resumeMic()` 方法
- `pauseMic()`：停止所有 MediaStream tracks，释放 getUserMedia
- `resumeMic()`：重新调用 `getUserMedia({ audio: true })`，恢复 VAD

### Step 3：修改 `AudioPlayer` 通知麦克风状态

- `AudioPlayer` 开始播放第一个 TTS chunk 时 → 调用 `pauseMic()`
- `AudioPlayer` 播放队列清空（或被 barge-in stop）时 → 调用 `resumeMic()`

### Step 4：添加 `navigator.audioSession` 支持（iOS 优化）

在 `useAudioSession` 中：

```typescript
// getUserMedia 之前设置（iOS Safari 16.4+）
if ('audioSession' in navigator) {
  navigator.audioSession.type = 'play-and-record';
}

// TTS 播放期间切换（iOS 优化）
if ('audioSession' in navigator) {
  navigator.audioSession.type = 'playback';
}

// TTS 结束恢复
if ('audioSession' in navigator) {
  navigator.audioSession.type = 'auto';
}
```

### Step 5：`App.tsx` 集成

```typescript
const { pauseMic, resumeMic } = useAudioSession();

// AudioPlayer 回调
const handleTTSPlay = useCallback(() => { pauseMic(); }, [pauseMic]);
const handleTTSStop = useCallback(() => { resumeMic(); }, [resumeMic]);
```

---

## 修改文件清单

| 文件 | 改动类型 | 说明 |
|------|---------|------|
| `xengineer-frontend/src/hooks/useAudioSession.ts` | **新建** | 音频会话管理 hook |
| `xengineer-frontend/src/hooks/useVAD.ts` | 修改 | 暴露 pauseMic/resumeMic |
| `xengineer-frontend/src/components/AudioRecorder.tsx` | 修改 | 接收 pauseMic/resumeMic 回调 |
| `xengineer-frontend/src/components/AudioPlayer.tsx` | 修改 | 播放/停止时通知麦克风状态 |
| `xengineer-frontend/src/App.tsx` | 修改 | 集成 useAudioSession，串联组件 |
| `xengineer-frontend/src/lib/protocol.ts` | 可能修改 | 如需新增消息类型 |

---

## 风险评估

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| 重新 getUserMedia 延迟 | TTS 结束后 ~100-500ms 麦克风不可用 | 接受此延迟（用户感知很小） |
| iOS 静音开关 | audioSession 不支持时音频可能被静音 | 方案 B 作为 iOS 优化补充 |
| 某些 Android 手机不释放通话模式 | 即使停止 mic 仍走通话音量 | 方案 C（echoCancellation:false）作为 fallback |
| Barge-in 时序 | stop TTS → resumeMic 可能有竞态 | 在 barge-in 时立即 resumeMic（与 stop 同步） |

---

## 参考资料

- [WebKit Bug 218012 — iOS 音量降低](https://bugs.webkit.org/show_bug.cgi?id=218012)
- [Chromium Issue 40866811 — Android 音量键错误通道](https://issues.chromium.org/40866811)
- [MDN: AudioSession.type](https://developer.mozilla.org/en-US/docs/Web/API/AudioSession/type)
- [SO: iOS Safari getUserMedia 音频路由](https://stackoverflow.com/questions/76083738)
- [W3C Audio Session Spec](https://www.w3.org/TR/audio-session/)
- [amd/gaia #896 — 相同用例](https://github.com/amd/gaia/issues/896)
