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
- 主观评分：可读性、可编辑性、是否符合论文方法图风格。

## 最小验证

当前仓库提供 mock 样例和单元测试，用于确认接口、schema 和 Mermaid 转换正确。真实 OpenAI 评测可在 `.env` 配置 key 后追加运行。

```bash
uv run python scripts/evaluate_samples.py --mock
uv run python scripts/evaluate_samples.py --include-audio
```

默认评测使用 transcript，避免每次运行都触发 ASR 费用；需要验证真实音频转写时再加 `--include-audio`。
