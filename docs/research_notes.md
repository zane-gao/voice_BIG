# 调研记录

## OpenAI 能力

- Speech to text 可用于音频转写，默认规划模型为 `gpt-4o-mini-transcribe`。
- Responses API 支持结构化输出，可让模型直接返回符合 Pydantic schema 的 JSON。
- 多模态输入可同时提供文本和草图图像，适合将语音语义和图像结构联合解释。
- GPT Image 系列可用于生成或编辑终稿图；本项目把它放在“终稿生图”阶段，而不是替代 Mermaid/SVG。

## 豆包 Seedream

- 火山方舟图片生成 API 使用 `POST https://ark.cn-beijing.volces.com/api/v3/images/generations`。
- Seedream 5.0 lite 支持 `image` 参考图、`response_format=b64_json`、`output_format`、`watermark` 和 `sequential_image_generation` 等参数。
- 本项目用豆包承担 10 秒静默后自动触发的低清草稿图，强调速度和构图预览。

## 报告写法

参考 `venue-templates` 中 ML 会议论文写法：摘要说明问题、方法和结果；引言给出动机；方法部分明确系统架构、schema 和生成流程；实验部分强调指标、样例和局限。
