# 实验计划

## 样例集

当前样例集包含基础 mock 样例和 3 组可演示“草图 + 语音”案例。

基础样例：

1. 线性流程：输入数据、预处理、模型、输出。
2. 多模态融合：语音、草图、文本特征、融合模块、方法图。
3. 带评测闭环：生成结果、用户修订、指标评测和迭代。

演示样例位于 `data/cases/`：

1. `cnn_explainer`：卷积神经网络讲解，覆盖输入图像、卷积核、特征图、ReLU、池化、Flatten、全连接和 Softmax。
2. `diffusion_roadmap`：扩散技术发展路线，覆盖 DDPM、DDIM、Classifier-Free Guidance、Latent Diffusion、Stable Diffusion、ControlNet、DiT 和快速采样。
3. `video_generation_timeline`：视频生成模型发展脉络，覆盖早期 GAN/RNN、Video Diffusion Models、Imagen Video、Phenaki、VideoLDM、时空 Transformer、Lumiere 和 Sora。

每个样例包含：

- 草图图片。
- 语音文件和 transcript 文本标注。
- 目标节点列表。
- 目标边列表。

生成命令：

```bash
uv run python scripts/generate_test_cases.py --force --tts-provider auto
```

若外部图像 API 不可用，脚本会写入 PIL 草图；若外部语音 API 不可用，macOS 环境会用 `say` 生成 WAV 语音。所有回退原因都会记录到每个 `gold.json` 的 `warnings` 中，保证评测链路仍可运行。

## 指标

- ASR：中文使用 CER，英文使用 WER。
- 节点识别：precision、recall、F1。
- 边识别：precision、recall、F1。
- 图结构还原度：节点和边 F1 的平均值。
- 生成耗时：ASR、图结构化和端到端耗时。
- 生图耗时：草稿图和终稿图生成时间。
- 图像一致性：生图是否保留 Mermaid 的主要节点和连线。
- 图像可读性：节点文字是否可读、版式是否适合论文或汇报。
- 讲解可用性：TTS 是否生成非空音频，讲解稿是否覆盖主要节点。
- 光标同步：播放时光标是否落在 0 到 1 坐标范围内，并按段落顺序移动。
- WebM 导出：浏览器录制结果是否非空，是否包含终稿图、光标动画和音频轨。
- 主观评分：可读性、可编辑性、是否符合论文方法图风格。

## 最小验证

当前仓库提供 mock 样例和单元测试，用于确认接口、schema 和 Mermaid 转换正确。真实 OpenAI 评测可在 `.env` 配置 key 后追加运行。

```bash
uv run python scripts/evaluate_samples.py --mock
uv run python scripts/evaluate_samples.py --include-audio
node --check src/sketchvoice/static/app.js
```

默认评测使用 transcript，避免每次运行都触发 ASR 费用；需要验证真实音频转写时再加 `--include-audio`。

终稿图讲解最小验证：

```bash
uv run pytest tests/test_narration_service.py tests/test_api.py::test_narrate_image_mock_returns_cursor_segments
```

真实 TTS 评测建议先使用短文本和 mock 终稿图验证参数，再切换真实 OpenAI/豆包 key，避免反复消耗额度。

## 科研侧 MMSB-Graph 实验

科研侧新增 24 个小样本方法图 case，位于 `data/research_cases/`，清单为 `data/research_samples.json`。每个 case 包含：

- `sketch.png`：确定性生成的手绘风格草图。
- `speech.wav`：确定性占位音频，真实 ASR 评测前需要替换。
- `transcript.txt`：语音文本标注。
- `gold.json`：目标节点、目标边、`node_spans`、`speech_anchors`、`sketch_regions`、`layout` 和 `difficulty`。
- `gold_mermaid.mmd` 与 `gold_render.png`：标准方法图源码和渲染图。

生成与评测命令：

```bash
uv run python scripts/prepare_research_cases.py
uv run python scripts/evaluate_research_cases.py --samples data/research_samples.json --output docs/research_eval_results.json
```

当前 `evaluate_research_cases.py` 使用合成条件图做 sanity check，不调用外部模型。论文中只能把这些数字表述为可控验证，不能写成真实 VLM/ASR 性能。
