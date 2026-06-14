# T11 - Pipeline 编排器端到端串联

## 修改的文件
| 文件 | 操作 |
|------|------|
| `app/pipeline/orchestrator.py` | 重写 |
| `app/main.py` | 重写 |
| `app/config.py` | 新增 `USE_REAL_NODES` 字段 |
| `app/pipeline/vlm_node.py` | 修复字段名兼容 |
| `.env.example` | 新增 `USE_REAL_NODES` 说明 |

## 关键设计说明

### 数据流
```
vad_status(speaking=true)  → orchestrator._start_asr_session()
                           → ASRNode.start_session() [真实节点建连]

audio(data) [重复多次]     → orchestrator.handle_audio()
                           → ASRNode.process() → 火山ASR
                           → _on_interim → asr_interim 推前端

vad_status(speaking=false) → orchestrator._stop_asr_session()
                           → ASRNode.stop_session() → 发送最后一包
                           → 火山ASR 返回最终文本
                           → _on_final(text) → send_to_next({text, image})
                             → VLMNode.process() → Agnes 流式
                               → _on_chunk → llm_chunk 推前端
                               → _on_sentence → TTSNode.process()
                                 → 火山TTS → tts_audio 推前端
```

### USE_REAL_NODES 切换
- `false`（默认）：StubNode，不调用任何外部 API
- `true`：延迟导入真实节点，需要配置正确的火山/Agnes 密钥

### 错误隔离
- `send_to_frontend()` 内部 try/except，WS 断开不抛异常
- `handle_audio()` 包裹 try/except，ASR 错误推 error 消息
- `_start/stop_asr_session()` 包裹 try/except
- `VLMNode.process()` 已有 try/except
- 单个节点失败 → error 消息 → Pipeline 不崩溃

### 图片支持（预留）
- `handle_image()` 保存 base64 到 `_latest_image`
- ASR 最终结果携带 `image` 字段传给 VLM
- VLMNode 兼容 `image` / `image_url` 两种字段名
- 当前纯文本模式（`image_url` 为 None），后续接入静态文件服务即可启用多模态