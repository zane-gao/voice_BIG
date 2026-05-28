# 系统架构

## 总体流程

```mermaid
flowchart LR
  User[用户] --> Canvas[浏览器草图画布]
  User --> Audio[录音或音频上传]
  Samples[演示样例资产] --> Canvas
  Samples --> Audio
  Canvas --> API[FastAPI /api/generate]
  Audio --> API
  API --> ASR[OpenAI 语音转写]
  API --> Vision[草图图像输入]
  ASR --> Fusion[结构化输出模型]
  Vision --> Fusion
  Fusion --> Normalize[图结构规整]
  Normalize --> Mermaid[Mermaid 生成]
  Mermaid --> UI[Mermaid / SVG / JSON 预览]
  Mermaid --> ImgAPI[/api/render-image]
  Canvas --> ImgAPI
  ImgAPI --> Doubao[豆包 Seedream 草稿图]
  ImgAPI --> OpenAIImage[OpenAI 终稿图]
  Doubao --> UI
  OpenAIImage --> UI
```

## 模块划分

- `sketchvoice.main`：FastAPI 应用、静态资源、接口入口。
- `sketchvoice.config`：环境变量与模型配置。
- `sketchvoice.models`：结构化图的 Pydantic schema。
- `sketchvoice.openai_service`：语音转写、多模态结构化和 mock 回退。
- `sketchvoice.image_service`：豆包草稿生图、OpenAI 终稿生图、prompt 构造、mock 图像回退。
- `sketchvoice.mermaid`：节点 id 规整、悬空边过滤、Mermaid 转换。
- `static/`：画布、录音、上传、结构图预览、AI 图像预览和下载交互。
- `data/cases/`：可选演示样例，包含草图、语音、transcript 和 gold 标注。

## API

### `GET /health`

返回服务状态、是否 mock、语音模型、图模型和音频大小限制。

### `GET /api/samples`

返回可选演示样例列表。前端用它填充“演示样例”下拉框，并展示样例主题、难度、transcript、草图 URL、音频 URL、标准节点和标准边。

### `GET /api/samples/{sample_id}/sketch`

返回样例草图图片。

### `GET /api/samples/{sample_id}/audio`

返回样例语音文件。

### `POST /api/generate`

请求类型：`multipart/form-data`

字段：

- `sketch`：PNG/JPEG 草图文件，可为空。
- `audio`：音频文件，可为空。
- `transcript`：人工文本，可为空；非空时优先使用。
- `direction`：`LR` 或 `TD`。

返回：

- `transcript`
- `graph`
- `mermaid`
- `timings_ms`

### `POST /api/render-image`

请求类型：`multipart/form-data`

字段：

- `mode`：`draft` 或 `final`。
- `sketch`：当前画布 PNG。
- `transcript`：转写或人工文本。
- `mermaid`：当前 Mermaid 源码。
- `graph_json`：当前结构化图 JSON。
- `style`：`paper`、`slides`、`nature` 或 `mono`。

返回：

- `mode`
- `provider`
- `model`
- `image_b64`
- `mime_type`
- `prompt`
- `timings_ms`
- `cached`
- `warnings`
