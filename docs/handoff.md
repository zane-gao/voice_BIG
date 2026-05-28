# 项目交接文档

## 当前状态

项目已具备可演示 Web MVP。核心代码在 `src/sketchvoice/`，前端静态资源在 `src/sketchvoice/static/`，报告在 `report/main.tex`。

## 启动方式

```bash
uv sync --extra dev
uv run uvicorn sketchvoice.main:app --reload --host 127.0.0.1 --port 8000
```

打开 <http://127.0.0.1:8000>。

## 关键配置

- `.env` 存放 `OPENAI_API_KEY` 和 `ARK_API_KEY`，不要提交。
- `OPENAI_BASE_URL` 可选，用于兼容 OpenAI API 的中转站。
- `SKETCHVOICE_MOCK=true` 可强制走 mock 模式。
- `OPENAI_GRAPH_MODEL` 默认 `gpt-5.5`；账号不支持时可切到 `gpt-5-mini` 或 `gpt-4o-mini`。
- `DOUBAO_DRAFT_IMAGE_MODEL` 默认 `doubao-seedream-5-0-lite-260128`。
- `OPENAI_FINAL_IMAGE_MODEL` 默认 `gpt-image-2`。
- `OPENAI_TTS_MODEL` 默认 `gpt-4o-mini-tts`，用于生成测试样例语音。
- `SAMPLE_TTS_PROVIDER=openai|doubao|auto` 控制样例语音 provider。
- `DOUBAO_TTS_MODEL` 默认 `doubao-seed-2-0-pro-260215`，仅用于样例语音的豆包尝试分支。
- `IMAGE_FALLBACK_TO_MOCK=true` 可让图像 API 失败时自动返回 mock 图。

## 图像生成说明

- 豆包草稿图由前端 10 秒 debounce 自动触发，请求 `/api/render-image` 且 `mode=draft`。
- OpenAI 终稿图由“生成终稿图”按钮触发，请求 `/api/render-image` 且 `mode=final`。
- 前端不会接触任何 provider key；所有生图调用都在 `sketchvoice.image_service` 中完成。
- 若 OpenAI key 无效或豆包 key 不可用，默认 mock fallback 会生成本地占位图。

## 测试样例资产

- 三组演示样例在 `data/cases/`：CNN 讲解、扩散路线、视频生成脉络。
- `scripts/generate_test_cases.py` 会生成 `sketch.png`、语音文件、`transcript.txt`、`gold.json` 并更新 `data/samples.json`。
- 草图优先调用豆包 Seedream；失败时用 PIL 生成白板草图。
- 语音默认调用 OpenAI TTS；`--tts-provider auto` 会再尝试豆包语音分支，API 全部失败后用 macOS `say` 写入 `speech.wav`。
- 当前机器若使用无效 OpenAI key，语音可能是 mock；替换 `.env` 的 `OPENAI_API_KEY` 和 `OPENAI_BASE_URL` 后可重新运行：

```bash
uv run python scripts/generate_test_cases.py --force --tts-provider auto
```

## 后续可扩展

- 加入本地 ASR 模型作为离线后端。
- 用 OCR/视觉检测模型替换当前端到端多模态结构化。
- 增加 PPTX 导出。
- 扩展样例集，加入更多手写风格、口音和跨语言样例。
- 增加真实图像质量评测，例如文字可读性、结构一致性和用户主观评分。
