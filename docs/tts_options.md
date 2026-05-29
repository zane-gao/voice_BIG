# TTS 选型调研

更新日期：2026-05-29

## 结论

第一版继续保持低风险路线：默认使用 OpenAI `gpt-4o-mini-tts` 模板音色，支持用户填入已有 custom voice ID；国内或中文讲解可选豆包语音 `voice_type`；演示和断网场景保留 mock / macOS `say` fallback。

若后续要做“本地个人音色”或“无需外部 API 的复现”，优先预留 `voxcpm2` provider。VoxCPM2 的能力覆盖文本音色设计、短音频克隆、带参考文本的高相似度克隆和流式生成；官方 PyTorch 路线依赖 CUDA，本机 Apple Silicon 可评估 MLX 版本。

## 方案对比

| 方案 | 类型 | 个人音色 | 中文/多语种 | 本项目建议 |
| --- | --- | --- | --- | --- |
| OpenAI `gpt-4o-mini-tts` | 云 API | 支持已有 custom voice ID | 多语种可用，声音主要按英文优化 | 第一版默认，接口最简单 |
| 豆包语音 | 云 API | 支持声音复刻后的 `voice_type` | 中文音色丰富 | 第一版可选，适合中文演示 |
| MiniMax Speech | 云 API | 支持快速克隆、音色设计和 T2A voice_id | 40+ 语言 | 第二阶段候选，中文/低延迟不错 |
| ElevenLabs | 云 API | Instant / Professional voice cloning | 32+ 语言，表现力强 | 海外高质量候选，成本和合规需评估 |
| VoxCPM2 | 本地/自托管 | 短参考音频克隆、参考文本高保真克隆 | 30 语种、中文方言覆盖 | 本地化优先候选，先做 provider 预留 |
| CosyVoice2 / Fun-CosyVoice | 本地/自托管 | zero-shot / cross-lingual cloning | 中英日等与中文方言强 | 本地候选，中文生态成熟 |
| F5-TTS | 本地/自托管 | zero-shot voice cloning | 多语种衍生版本活跃 | 研究候选，适合实验对比 |
| Fish Speech S2 | 本地/自托管/API | 多语种、情绪/韵律控制 | 80+ 语言资料训练说明 | 高质量候选，但许可证需单独审查 |
| Kokoro-82M | 本地/自托管 | 不主打克隆 | 轻量、速度快 | 兜底朗读候选，不适合个人音色主线 |

## VoxCPM2 备注

- 官方模型卡称 VoxCPM2 是 tokenizer-free diffusion autoregressive TTS，2B 参数，30 语言，48kHz 输出，训练数据超过 200 万小时。
- 支持三类关键用法：文本描述生成新音色、短音频可控克隆、参考音频加精确 transcript 的高相似度克隆。
- 官方 PyTorch 快速开始要求 Python 3.10+、PyTorch 2.5+、CUDA 12+，标称约 8GB VRAM。
- `mlx-community/VoxCPM2-bf16` 提供 Apple Silicon MLX 版本，包含 bf16、8-bit、4-bit 体积与 RTF 参考；适合在本机做离线验证。
- 风险：本项目当前是轻量 Web MVP，不宜把 2B 本地模型依赖直接塞进默认安装；更稳的是先设计 provider 插口，单独用 `codex-train-mlx` 或独立环境验证。

## 实施建议

1. 第一版 provider：`openai`、`doubao`、`mock`。
2. 请求字段保留 `custom_voice_id` / `doubao_voice_type`，不在前端做声音克隆训练。
3. 新增文档说明：用户必须确认拥有声音使用权，AI 语音需要明确标识。
4. 第二阶段新增 `local_voxcpm2` provider：
   - 不加入默认依赖。
   - 通过环境变量指向本地 HTTP 服务或 CLI。
   - 音频参考文件和 transcript 走单独接口，避免污染第一版 `/api/narrate-image`。

## 参考来源

- OpenAI Text to speech：`https://developers.openai.com/api/docs/guides/text-to-speech`
- 火山引擎豆包语音参数说明：`https://www.volcengine.com/docs/6561/79823`
- 火山引擎豆包语音开发参考：`https://www.volcengine.com/docs/6561/1257536`
- VoxCPM2 Hugging Face：`https://huggingface.co/openbmb/VoxCPM2`
- VoxCPM2 MLX：`https://huggingface.co/mlx-community/VoxCPM2-bf16`
- MiniMax Speech API：`https://platform.minimax.io/docs/api-reference/api-overview`
- ElevenLabs TTS 文档：`https://elevenlabs.io/docs/overview/capabilities/text-to-speech`
- Azure Text to speech：`https://learn.microsoft.com/en-us/azure/ai-services/Speech-Service/text-to-speech`
- Google Cloud TTS voices：`https://cloud.google.com/text-to-speech/docs/voices`
- CosyVoice2 Hugging Face：`https://huggingface.co/FunAudioLLM/CosyVoice2-0.5B`
- Fish Speech：`https://github.com/fishaudio/fish-speech`
- Kokoro：`https://github.com/hexgrad/kokoro`
- F5-TTS paper：`https://arxiv.org/abs/2410.06885`
