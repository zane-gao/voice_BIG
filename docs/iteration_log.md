# 版本迭代记录

## v0.4.0

- 新增 `/api/narrate-image` 终稿图语音讲解接口，返回 TTS 音频、讲解稿和段落级光标坐标。
- 新增 `sketchvoice.narration_service`，支持 OpenAI、豆包和 mock TTS，并在外部 TTS 失败时尝试 macOS `say` 或 mock WAV 回退。
- 前端 `AI 图像` 标签页新增“语音讲解”控制区，可选择 provider、模板音色、已有 OpenAI custom voice ID 或豆包 `voice_type`。
- 终稿图预览新增讲解光标层，播放音频时按讲解 segment 自动移动。
- 新增浏览器端 WebM 下载，使用 `canvas.captureStream()` 和 `MediaRecorder` 录制终稿图、光标动画和音频。
- 新增 TTS 选型调研 `docs/tts_options.md`，记录 OpenAI、豆包、MiniMax、ElevenLabs、VoxCPM2、CosyVoice2、F5-TTS、Fish Speech 和 Kokoro 的取舍。

## v0.3.0

- 新增三组“真实草图 + 语音”测试案例：CNN 讲解、扩散技术路线、视频生成发展脉络。
- 新增 `scripts/generate_test_cases.py`，支持豆包生成手写草图、OpenAI TTS 生成语音，以及 mock 回退。
- 前端新增演示样例选择区，可一键载入草图、样例语音和 transcript。
- 后端新增 `/api/samples` 与样例草图/音频资产接口。
- 默认图结构化模型升级为 `gpt-5.5`，并支持 `OPENAI_BASE_URL` 中转站配置。
- `data/samples.json` 兼容 `sketch_path`、`audio_path`、`transcript_path`、`topic`、`difficulty` 等新字段。
- `scripts/evaluate_samples.py` 支持读取样例资产路径，默认继续使用 transcript 评测，避免不必要的 ASR 调用。
- 新增 `OPENAI_BASE_URL`、`OPENAI_TTS_MODEL`、`SAMPLE_TTS_PROVIDER`、`DOUBAO_TTS_MODEL` 等配置说明。

## v0.2.0

- 新增 `/api/render-image` 生图接口。
- 新增豆包 Seedream 5.0 lite 实时草稿图：用户停止画图或编辑文本 10 秒后自动触发。
- 新增 OpenAI GPT Image 终稿图生成。
- 前端右侧结果区新增 `AI 图像` 标签页，支持风格选择、状态显示和图片下载。
- 生图服务支持 mock 回退，避免课堂演示被 API 认证、额度或网络问题中断。

## v0.1.0

- 建立 FastAPI + 静态前端 MVP。
- 支持浏览器画草图、录音、上传音频和人工 transcript。
- 支持 OpenAI ASR 与多模态结构化输出。
- 支持 mock 回退，保证课堂演示稳定。
- 输出 Mermaid、SVG 预览和 JSON。
- 补充需求、架构、实验计划、交接文档和 LaTeX 报告。
