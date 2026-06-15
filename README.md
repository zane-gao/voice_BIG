# SketchVoice 方法图工坊

这是一个“语音 + 草图”多模态科研方法图实时生成系统 MVP。用户可以在浏览器里画草图、录音或上传音频，系统通过 OpenAI API 完成转写与结构化建模，输出 Mermaid、SVG 预览、JSON、AI 生成的论文风格图像，以及终稿图语音讲解 WebM。

## 快速启动

```bash
uv sync --extra dev
uv run uvicorn sketchvoice.main:app --reload --host 127.0.0.1 --port 8000
```

打开 <http://127.0.0.1:8000>。

## 配置

复制 `.env.example` 为 `.env`，填入 `OPENAI_API_KEY` 和 `ARK_API_KEY`。如果没有 key，或想离线演示：

```bash
SKETCHVOICE_MOCK=true
```

默认模型：

- 语音转写：`gpt-4o-mini-transcribe`
- 图结构化：`gpt-5.5`
- 实时草稿生图：`doubao-seedream-5-0-lite-260128`
- 终稿生图：`gpt-image-2`

如果账号不支持默认模型，可在 `.env` 中把 `OPENAI_GRAPH_MODEL` 改成 `gpt-5-mini` 或 `gpt-4o-mini`。

图像生成相关配置：

- `ARK_API_KEY`：豆包/火山方舟 API key，只在服务端读取。
- `OPENAI_BASE_URL`：可选。使用兼容 OpenAI API 的中转站时填写，例如 `https://gmn.chuangzuoli.com`；服务端会自动规范为 `/v1` 客户端地址，不改前端。
- `OPENAI_IMAGE_API_KEY`、`OPENAI_IMAGE_BASE_URL`：可选。终稿生图需要和结构化/语音使用不同 OpenAI 兼容网关时填写；为空时复用 `OPENAI_API_KEY` 和 `OPENAI_BASE_URL`。
- `IMAGE_FALLBACK_TO_MOCK=true`：图像 API 失败时返回 mock 图，保证演示不断。
- `SKETCHVOICE_MOCK=true`：全局 mock，结构图与生图都不调用外部 API。

终稿生图不会直接把手绘草图作为 image edit 输入照搬，而是根据结构化 JSON / Mermaid 重新生成论文级知识信息图。若外部生图 API 失败，mock fallback 也会按结构化 JSON / Mermaid 渲染节点和边，避免退化成固定占位图。

测试样例语音相关配置：

- `OPENAI_TTS_MODEL=gpt-4o-mini-tts`、`OPENAI_TTS_VOICE=coral`：默认用 OpenAI TTS 生成样例语音。
- `SAMPLE_TTS_PROVIDER=openai|doubao|auto`：`auto` 会先试 OpenAI，再试豆包兼容语音分支；API 都失败时，macOS 会用 `say` 生成 WAV 兜底。
- `DOUBAO_TTS_MODEL=doubao-seed-2-0-pro-260215`：保留给豆包语音分支使用；若账号或端点不支持，会自动回退。

终稿图讲解相关配置：

- `NARRATION_TTS_PROVIDER=openai|doubao|mock`：控制 `/api/narrate-image` 默认 TTS provider。
- `NARRATION_OPENAI_VOICE=coral`：OpenAI 模板音色；也可在前端选择 `marin`、`cedar` 等内置音色。
- `NARRATION_CUSTOM_VOICE_ID=`：已有 OpenAI custom voice ID；第一版不在系统内创建新音色。
- `NARRATION_DOUBAO_VOICE_TYPE=`：已有豆包声音复刻或模板 `voice_type`。
- 更多 TTS 方案取舍见 `docs/tts_options.md`，其中包含 VoxCPM2、CosyVoice2、MiniMax、ElevenLabs 等候选。

## 演示流程

1. 在左侧画布手绘科研流程草图。
2. 也可以在“演示样例”中选择 CNN、扩散路线或视频生成脉络，一键载入草图和语音。
3. 点击“开始录音”口头描述思路，或上传已有音频。
4. 可在中间文本框补充或修改转写文本。
5. 点击“生成方法图”。
6. 在右侧查看 Mermaid、图形预览、AI 图像和 JSON，并下载结果。
7. 停止画图或编辑文本 10 秒后会自动生成豆包草稿图；点击“生成终稿图”可生成 OpenAI 高清终稿图。
8. 终稿图生成后，在“语音讲解”区域选择音源/音色，点击“生成讲解”，播放时光标会跟随讲解段落移动，也可下载浏览器录制的 WebM。

## 测试与报告

```bash
uv run pytest
uv run python scripts/generate_test_cases.py --force --tts-provider auto
uv run python scripts/evaluate_samples.py --mock
node --check src/sketchvoice/static/app.js
latexmk -xelatex -cd report/main.tex
```

三组演示样例位于 `data/cases/`，覆盖 CNN 讲解、扩散技术路线、视频生成发展脉络。每组包含 `sketch.png`、语音文件、`transcript.txt` 和 `gold.json`；API TTS 成功时语音为 `speech.mp3`，本机兜底时为 `speech.wav`。

报告源文件位于 `report/main.tex`，项目文档位于 `docs/`。
