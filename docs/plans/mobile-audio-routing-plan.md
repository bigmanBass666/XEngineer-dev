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
| A | TTS 播放时暂停麦克风（`track.stop()` + 释放 MediaStream） | ⭐⭐⭐⭐⭐ 最高 | Android + iOS 通用 | ❌ **破坏 barge-in**，TTS 期间无法 VAD 打断 |
| B | `navigator.audioSession.type` 动态切换 | ⭐⭐⭐⭐ | **仅 iOS Safari 16.4+**，Android 无此 API | 不解决 Android |
| C | `echoCancellation: false` | ⭐⭐⭐ | **仅 Android Chrome**（Chromium 工程师确认） | 产生回声 |
| D | 软件音量滑块（GainNode） | ⭐⭐ | 通用，但需 UI 改动 | 不改变硬件音量行为 |
| E | `setSinkId()` | ❌ | iOS 不支持，Android 无音频输出设备列表 | 不可行 |

### 方案 A 详细分析（~~推荐~~ 已否决）

> ⚠️ **此方案会破坏 barge-in，已被否决。保留记录供参考。**

**原理**：TTS 播放期间完全释放麦克风 MediaStream，让 OS 退出"通话模式"，恢复"媒体播放"模式。

**否决原因 — barge-in 依赖链**：
```
barge-in 链路：
  用户说话 → 麦克风采集 → useVAD 检测 speaking → audioPlayer.stop()
                                              ↑
                               如果 mic 被停止，VAD 无输入，这条链路断裂
```

**结论**：方案 A 的 mic 停止会导致 VAD 无法检测用户说话，barge-in 完全失效。不可接受。

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

## 推荐实施方案（v2 — 保持 barge-in）

采用 **方案 B（iOS）+ 方案 C（Android）组合，不停止麦克风**：

### 核心原则

**麦克风始终活跃，barge-in 完整保留。** 通过平台原生 API 在不释放 MediaStream 的情况下修复音量路由。

### Step 1：创建 `useAudioSession` hook

新建 `xengineer-frontend/src/hooks/useAudioSession.ts`：

```typescript
/**
 * 音频会话管理 hook
 * 
 * 核心职责：
 * 1. iOS：通过 navigator.audioSession.type 控制音频路由
 * 2. Android：通过 echoCancellation:false 阻止 MODE_IN_COMMUNICATION
 * 3. 不停止麦克风，完整保留 barge-in 能力
 */
```

### Step 2：修改 `useVAD.ts` — 添加 Android echoCancellation:false

```typescript
// getUserMedia 约束
const constraints: MediaStreamConstraints = {
  audio: {
    // Android：阻止 Chrome 进入 MODE_IN_COMMUNICATION
    // iOS：不影响 audioSession API 行为
    echoCancellation: isAndroid ? false : true,
  }
};
```

### Step 3：`useAudioSession` hook 实现

```typescript
export function useAudioSession(onTTSPlay: () => void, onTTSStop: () => void) {
  useEffect(() => {
    // iOS：getUserMedia 之前设置音频会话类型
    if ('audioSession' in navigator) {
      navigator.audioSession.type = 'play-and-record';
    }
  }, []);

  // TTS 播放时切换音频路由
  const handleTTSPlay = useCallback(() => {
    if ('audioSession' in navigator) {
      // iOS：强制媒体播放路由，音量键恢复正常
      navigator.audioSession.type = 'playback';
    }
    onTTSPlay();
  }, [onTTSPlay]);

  // TTS 结束时恢复
  const handleTTSStop = useCallback(() => {
    if ('audioSession' in navigator) {
      navigator.audioSession.type = 'play-and-record';
    }
    onTTSStop();
  }, [onTTSStop]);

  return { handleTTSPlay, handleTTSStop };
}
```

### Step 4：修改 `AudioPlayer.tsx` 暴露播放/停止回调

- 新增 `onPlayStateChange?: (playing: boolean) => void` prop
- 入队首个 chunk 时调用 `onPlayStateChange(true)`
- 队列清空或被 barge-in stop 时调用 `onPlayStateChange(false)`

### Step 5：`App.tsx` 集成

```typescript
// 不需要 pauseMic/resumeMic
const audioSession = useAudioSession();

// AudioPlayer 的 onPlayStateChange 触发 audioSession 切换
<AudioPlayer onPlayStateChange={audioSession.handleTTSPlay || audioSession.handleTTSStop} />
```

---

## 修改文件清单

| 文件 | 改动类型 | 说明 |
|------|---------|------|
| `xengineer-frontend/src/hooks/useAudioSession.ts` | **新建** | 音频会话管理 hook（iOS audioSession + Android 检测） |
| `xengineer-frontend/src/hooks/useVAD.ts` | 修改 | Android 加 echoCancellation:false |
| `xengineer-frontend/src/components/AudioPlayer.tsx` | 修改 | 暴露 onPlayStateChange 回调 |
| `xengineer-frontend/src/App.tsx` | 修改 | 集成 useAudioSession，绑定 AudioPlayer 回调 |

---

## 风险评估

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| iOS mic 活跃时 playback 类型被覆盖 | 音频仍走通话通道 | 需实测验证；若不行则方案 A 降级（仅 iOS，接受 barge-in 延迟） |
| Android echoCancellation=false 回声 | TTS 声音被麦克风拾取 | 可在 TTS 播放时短暂 `track.enabled = false` 静音（仅 Android） |
| iOS audioSession API 不支持（<Safari 16.4） | 无法控制音频路由 | 检测 `'audioSession' in navigator`，不支持则 graceful degrade |
| 各 Android ROM 差异 | 某些厂商 ROM 不遵循 Chromium 行为 | echoCancellation:false 是 Chromium 工程师确认的，覆盖主流 ROM |
| Barge-in | ✅ **不受影响** | mic 始终活跃，VAD 正常工作 |

---

## 参考资料

- [WebKit Bug 218012 — iOS 音量降低](https://bugs.webkit.org/show_bug.cgi?id=218012)
- [Chromium Issue 40866811 — Android 音量键错误通道](https://issues.chromium.org/40866811)
- [MDN: AudioSession.type](https://developer.mozilla.org/en-US/docs/Web/API/AudioSession/type)
- [SO: iOS Safari getUserMedia 音频路由](https://stackoverflow.com/questions/76083738)
- [W3C Audio Session Spec](https://www.w3.org/TR/audio-session/)
- [amd/gaia #896 — 相同用例](https://github.com/amd/gaia/issues/896)
