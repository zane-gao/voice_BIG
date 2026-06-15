# 演示图片资源

前端离线生成流程会从这个目录读取现成图片，不再调用生图接口。

放置规则：

- 通用回退图放在 `src/sketchvoice/static/offline/`。
- 样例专属图放在 `src/sketchvoice/static/offline/<sample_id>/`。

当前默认样例 ID 是：

- `cnn_explainer`
- `diffusion_roadmap`
- `video_generation_timeline`

每个目录都放两张图：

- 方法图：`method.png`，也可用 `method.jpg`、`method.jpeg` 或 `method.webp`。
- 终稿图：`final.png`，也可用 `final.jpg`、`final.jpeg` 或 `final.webp`。

点击页面顶部的“生成方法图”时，会优先读取当前样例目录下的 `method.*`，找不到时回退到根目录 `method.*`。

点击“AI 图像”页里的“生成终稿图”时，会优先读取当前样例目录下的 `final.*`，找不到时回退到根目录 `final.*`。

默认生成等待时间由随机种子决定，范围为 40 到 60 秒；测试时可用 `?offlineDelayMs=1000` 之类的查询参数缩短等待。
