# 终稿图片语音讲解 + 跟随光标

## Summary
在现有“AI 图像”终稿结果上新增讲解模式：用户生成终稿图后，可选择模板音色或填写已有个人音色 ID，系统生成一段讲解音频和光标时间轴；前端播放时光标随讲解内容在终稿图上移动，并支持下载浏览器录制的 WebM 视频。

依据：OpenAI TTS 支持 `gpt-4o-mini-tts`、内置音色和符合条件账号的自定义声音 ID；自定义声音创建需要同意录音和样本录音，第一版不在本系统内做完整克隆流程，只支持使用已创建的 voice ID。豆包语音文档中复刻音色可通过 `voice_type` 使用声音 ID。参考：OpenAI [Text to speech](https://developers.openai.com/api/docs/guides/text-to-speech)、火山引擎 [豆包语音参数说明](https://www.volcengine.com/docs/6561/79823)。

## Key Changes
- 后端新增讲解服务：
  - 新增 `POST /api/narrate-image`。
  - 输入：终稿图、`graph_json`、`mermaid`、`transcript`、音色 provider、模板音色或个人音色 ID。
  - 输出：`audio_b64`、`mime_type`、`script`、`segments`、`provider`、`model`、`timings_ms`、`warnings`。
  - `segments` 使用归一化坐标 `{text, target_label, x, y, emphasis}`，前端按音频总时长和文本长度分配播放时间。
- 讲解规划：
  - 使用结构图和终稿图生成 `NarrationPlan`：讲解稿、分段、每段光标位置。
  - 有 OpenAI 可用时用视觉/结构化模型生成坐标；失败时按节点顺序生成左到右 fallback 坐标。
- TTS：
  - 模板音色默认走 OpenAI `gpt-4o-mini-tts`。
  - 个人音色 ID 支持 OpenAI custom voice ID 和豆包 `voice_type` ID；不在第一版内创建/训练新音色。
  - TTS 失败时本地演示 fallback 到 macOS `say`，再失败则返回 mock WAV 和 warning。
- 前端：
  - 在 `AI 图像` tab 内新增“语音讲解”控制区。
  - 控件包括音色来源、模板音色、个人音色 ID、生成讲解、播放/暂停、下载 WebM。
  - 终稿图预览层叠加一个光标点/光圈；播放时按 `segments` 自动移动。
  - WebM 下载用浏览器 `canvas.captureStream()` + `MediaRecorder` 录制终稿图、光标动画和音频，不引入服务端视频编码依赖。
- 配置与文档：
  - 新增 `NARRATION_TTS_PROVIDER`、`NARRATION_OPENAI_VOICE`、`NARRATION_CUSTOM_VOICE_ID`、`NARRATION_DOUBAO_VOICE_TYPE` 等环境变量。
  - 更新 README、架构文档、实验计划、交接文档和迭代记录。

## Test Plan
- 单元测试：
  - mock 讲解接口返回合法 `audio_b64` 和归一化 cursor segments。
  - 无终稿图、非法 provider、非法坐标时返回明确错误或 fallback。
  - OpenAI 模板音色、custom voice ID、豆包 voice_type 参数解析可测。
- 前端验证：
  - Playwright 打开页面，生成/注入 mock 终稿图，点击“生成讲解”，确认音频播放器出现、光标元素随播放状态更新。
  - 点击“下载 WebM”，确认生成非空 blob；浏览器不支持 MediaRecorder 时显示不可下载提示。
- 回归验证：
  - `uv run pytest`
  - `uv run python scripts/evaluate_samples.py --mock`
  - `node --check src/sketchvoice/static/app.js`

## Assumptions
- 第一版交付“网页播放 + WebM 下载”，不做服务端 MP4。
- 第一版支持“模板音色 + 已有个人音色 ID”，不做完整声音克隆创建流程。
- 光标位置以讲解段落级同步为目标，不做逐词/音素级精确打轴。
- 讲解只绑定终稿图；草稿图不做语音讲解。
