# SketchVoice Product Defense - Design Spec

> Human-readable design narrative — rationale, audience, style, color choices, content outline.
>
> Machine-readable execution contract: `spec_lock.md`.

## I. Project Information

| Item | Value |
| ---- | ----- |
| **Project Name** | SketchVoice Product Defense |
| **Canvas Format** | PPT 16:9 (1280x720) |
| **Page Count** | 14 |
| **Design Style** | Product-defense story with research-method support; soft-rounded visual style |
| **Target Audience** | 语音信息处理课程答辩教师与同学 |
| **Use Case** | 课程结项答辩，8-12 分钟，强调产品闭环和科研支撑 |
| **Created Date** | 2026-06-14 |

Eight confirmations were approved by the user: `ppt169`, 14 pages, course-defense audience, product story first, blue-green restrained palette, built-in `tabler-outline` icons, CJK-first typography, existing report figure only. Formula handling was upgraded on request to render all visible formula-worthy expressions through LaTeX assets.

---

## II. Canvas Specification

| Property | Value |
| -------- | ----- |
| **Format** | PPT 16:9 |
| **Dimensions** | 1280x720 |
| **viewBox** | `0 0 1280 720` |
| **Margins** | 52px left/right, 44px top, 36px bottom |
| **Content Area** | 1176x600 after header/footer reservation |

---

## III. Visual Theme

### Theme Style

- **Mode**: custom
- **Mode behavior**: Three-act product-defense narrative. Act 1 starts from user workflow and product pain. Act 2 presents the research problem, related-work gap, formal task, MMSB-Graph method, evaluation protocol, and truthful result boundary. Act 3 closes with project knowledge graph and multi-dimensional value. Titles should sound like claims rather than chapter labels.
- **Visual style**: soft-rounded
- **Theme**: Light theme
- **Tone**: 产品答辩感、清晰、克制、可演示，同时保留科研可信度。

### Color Scheme

| Role | HEX | Purpose |
| ---- | --- | ------- |
| **Background** | `#F8FAFC` | page background |
| **Secondary bg** | `#FFFFFF` | panels and cards |
| **Primary** | `#155E75` | titles, product flow, key nodes |
| **Accent** | `#0F766E` | success path, semantic anchors |
| **Secondary accent** | `#2563EB` | product actions and links |
| **Body text** | `#172033` | main text |
| **Secondary text** | `#475569` | annotations |
| **Tertiary text** | `#94A3B8` | footer and page numbers |
| **Border/divider** | `#CBD5E1` | separators and card borders |
| **Success** | `#16A34A` | validated capability |
| **Warning** | `#F59E0B` | boundary and caveat |
| **Soft teal** | `#CCFBF1` | light semantic fills |
| **Soft blue** | `#E0F2FE` | product capability fills |
| **Soft amber** | `#FEF3C7` | limitation fills |
| **Soft green** | `#DCFCE7` | contribution fills |

### Gradient Scheme

Use subtle linear gradients only on bridge arrows and hero strips.

```xml
<linearGradient id="tealBlue" x1="0%" y1="0%" x2="100%" y2="0%">
  <stop offset="0%" stop-color="#155E75"/>
  <stop offset="100%" stop-color="#0F766E"/>
</linearGradient>
```

---

## IV. Typography System

### Font Plan

Typography direction: CJK-first product-research sans, with monospace only for graph variables, JSON, and formulas.

| Role | Chinese | English | Fallback tail |
| ---- | ------- | ------- | ------------- |
| **Title** | `"Microsoft YaHei"` | `Arial` | `sans-serif` |
| **Body** | `"Microsoft YaHei"` | `Arial` | `sans-serif` |
| **Emphasis** | `SimHei` | `Arial` | `sans-serif` |
| **Code** | - | `Consolas`, `"Courier New"` | `monospace` |

**Per-role font stacks**:

- Title: `"Microsoft YaHei", Arial, sans-serif`
- Body: `"Microsoft YaHei", Arial, sans-serif`
- Emphasis: `SimHei, "Microsoft YaHei", Arial, sans-serif`
- Code: `Consolas, "Courier New", monospace`

### Font Size Hierarchy

Baseline: Body font size = 20px.

| Purpose | Ratio to body | Current Project | Weight |
| ------- | ------------- | --------------- | ------ |
| Cover title | 2.8-3.4x | 58-68px | Bold |
| Page title | 1.7-1.9x | 34-38px | Bold |
| Subtitle | 1.2-1.4x | 24-28px | SemiBold |
| **Body content** | **1x** | **20px** | Regular |
| Annotation / caption | 0.7-0.85x | 14-16px | Regular |
| Page number / footnote | 0.6x | 12px | Regular |

Formula policy: `render-all for formula-worthy expressions`. All visible mathematical expressions are written in canonical LaTeX and rendered as transparent PNG assets, for example `\hat{G}=(\hat{V},\hat{E})`, `c(G_t,G_{t+1})`, and `E(G_{0:T})=\frac{1}{T}\sum_{t=0}^{T-1}c(G_t,G_{t+1})^2`.

---

## V. Layout Principles

### Page Structure

- **Header area**: 44-88px, page title and optional section tag.
- **Content area**: 560-600px, varies by page rhythm.
- **Footer area**: 24-36px, project label and page number.

### Layout Pattern Library

| Pattern | Suitable Scenarios |
| ------- | ----------------- |
| **Product journey strip** | User input to export workflow, 5-6 stages with arrows |
| **Soft capability cards** | Product features and system modules |
| **Asymmetric split** | One product claim plus supporting architecture or result |
| **Layered architecture** | Frontend, API, model services, output layers |
| **Bridge path** | MMSB-Graph edit path from candidate graph to target graph |
| **Metric table + figure band** | Experimental result table with diagnostic figure |
| **Closing triad** | Product, method, system contributions |

### Spacing Specification

**Universal**

| Element | Recommended Range | Current Project |
| ------- | ---------------- | --------------- |
| Safe margin from canvas edge | 40-60px | 52px |
| Content block gap | 24-40px | 28px |
| Icon-text gap | 8-16px | 12px |

**Card-based layouts**

| Element | Recommended Range | Current Project |
| ------- | ---------------- | --------------- |
| Card gap | 20-32px | 24px |
| Card padding | 18-28px | 22px |
| Card border radius | 8-16px | 8px |
| Three-column card width | 350-370px | 360px |

**Non-card containers**

- Use thin divider lines and large whitespace for breathing pages.
- Rounded rectangles never exceed 8px radius unless used as small tags.
- Avoid nested cards; repeated items may be cards, page sections should not be boxed as giant cards.

---

## VI. Icon Usage Specification

### Source

- Built-in icon library: `tabler-outline`
- Stroke width: 2
- Usage method: SVG placeholder `<use data-icon="tabler-outline/icon-name" .../>`

### Recommended Icon List

| Purpose | Icon Path | Page |
| ------- | --------- | ---- |
| 草图输入 | `tabler-outline/pencil` | P02, P03, P05 |
| 语音输入 | `tabler-outline/microphone` | P02, P03, P05 |
| 结构图/知识图 | `tabler-outline/network` | P03, P05, P07 |
| 产品旅程 | `tabler-outline/route-2` | P03 |
| 浏览器工作台 | `tabler-outline/device-desktop` | P04, P06 |
| 可导出结果 | `tabler-outline/file-export` | P03, P04 |
| JSON/代码输出 | `tabler-outline/json` | P04, P06 |
| 图像生成 | `tabler-outline/photo` | P04 |
| 语音讲解 | `tabler-outline/speakerphone` | P04 |
| 数据集 | `tabler-outline/database` | P11 |
| 评测结果 | `tabler-outline/chart-dots` | P11, P12 |
| 实验验证 | `tabler-outline/test-pipe` | P12 |
| 多模态融合 | `tabler-outline/layers-linked` | P08, P10 |
| 服务端架构 | `tabler-outline/server` | P06 |
| 图编辑路径 | `tabler-outline/git-branch` | P10 |
| 目标任务 | `tabler-outline/target` | P05, P14 |
| 核心贡献 | `tabler-outline/bulb` | P14 |
| 自动生成 | `tabler-outline/wand` | P03, P04 |
| 演示与答辩 | `tabler-outline/presentation` | P01 |
| 视频讲解 | `tabler-outline/video` | P04 |

---

## VII. Visualization Reference List

Catalog read: 71 templates

| Page | Template | Path | Summary-quote (verbatim from `charts_index.json`) | Usage |
| ---- | -------- | ---- | ------------------------------------------------- | ----- |
| P03 | basic_table | `templates/charts/basic_table.svg` | "Pick for plain tabular text/number grid, 3-8 columns. Skip if cells need visual bars (use consulting_table) or qualitative scores (use harvey_balls_table)." | Competitive positioning matrix |
| P04 | icon_grid | `templates/charts/icon_grid.svg` | "Pick for 4-9 parallel features/capabilities/services as icon cards — feature grid, service lineup, benefits matrix, brand values, product highlights. Skip for sequential ordering (use numbered_steps) or hierarchical layers (use pyramid_chart)." | Product capability map |
| P05 | pipeline_with_stages | `templates/charts/pipeline_with_stages.svg` | "Pick for 3-5 horizontal pipeline stages, each = title + 1-line description + output artifact, connected by arrows (data pipelines, ETL, build pipelines). Skip if any stage lacks an artifact (use process_flow or numbered_steps)." | Live demo flow from sketch to WebM |
| P06 | layered_architecture | `templates/charts/layered_architecture.svg` | "Pick for 3-4 horizontal architecture layers (presentation/service/data), 2-4 module cards per layer, each card = title + 1-line description (description required, even if source brief). Skip if no per-module descriptions (use icon_grid) or no horizontal layering (use module_composition)." | System architecture |
| P07 | vertical_list | `templates/charts/vertical_list.svg` | "Pick for 3-6 numbered key points each with a short description — design principles, core tenets, action items, key takeaways, recommendations, executive summary points. Skip for icon-style cards (use icon_grid) or sequential steps (use numbered_steps)." | Research positioning and modality assumptions |
| P08 | hub_inward_arrows | `templates/charts/hub_inward_arrows.svg` | "Pick for 1 center subject + 4-5 surrounding forces with arrows pointing inward — Porter's Five Forces (central rivalry, threat of new entrants/substitutes, bargaining power of buyers/suppliers), threat-model with central asset, pressure-on-core diagrams. Skip for outward radiation from center capability (use hub_spoke) or non-directional cluster (use mind_map)." | Related-work gap and research opening |
| P09 | process_flow | `templates/charts/process_flow.svg` | "Pick for 3-8 sequential steps connected by simple arrows — approval workflows, customer onboarding, request handling, lifecycle stages. Skip if cyclical (use circular_stages) or stages produce named outputs (use pipeline_with_stages)." | Formal task definition |
| P10 | process_flow | `templates/charts/process_flow.svg` | "Pick for 3-8 sequential steps connected by simple arrows — approval workflows, customer onboarding, request handling, lifecycle stages. Skip if cyclical (use circular_stages) or stages produce named outputs (use pipeline_with_stages)." | MMSB-Graph method and edit-cost formulation |
| P11 | basic_table | `templates/charts/basic_table.svg` | "Pick for plain tabular text/number grid, 3-8 columns. Skip if cells need visual bars (use consulting_table) or qualitative scores (use harvey_balls_table)." | Dataset, protocol, baselines, and metrics |
| P12 | basic_table | `templates/charts/basic_table.svg` | "Pick for plain tabular text/number grid, 3-8 columns. Skip if cells need visual bars (use consulting_table) or qualitative scores (use harvey_balls_table)." | Controlled results, limits, and future work |
| P13 | mind_map | `templates/charts/mind_map.svg` | "Pick for one core topic radiating into 3-6 brainstorm branches. Skip for capability hub-and-spoke (use hub_spoke) or strict hierarchy (use top_down_tree)." | Project knowledge graph |

**Runners-up considered**

- `journey_map` | rejected for P05: live demo is a linear generation pipeline, not a customer-experience matrix with emotions and pain points.
- `module_composition` | rejected for P06: the system has clear horizontal layers, so `layered_architecture` is more precise.
- `comparison_table` | rejected for P11: the page reports metrics rather than dense feature rows.

---

## VIII. Image Resource List

| Filename | Dimensions | Ratio | Purpose | Type | Layout pattern | Acquire Via | Status | Reference | text_policy | page_role |
| -------- | ---------- | ----- | ------- | ---- | -------------- | ----------- | ------ | --------- | ----------- | --------- |
| mmsb_diagnostics.png | 3514x1309 | 2.68 | Report diagnostic figure for structural recovery, GED distribution, and bridge load | Diagram | #6 Bottom-band image + top title + middle text + #70 Image with thin colored matte frame | user | Existing | `report/figures/mmsb_diagnostics.png` copied into project images | none | local |
| formula_07_main.png | 475x60 | 7.92 | P07 formal task formula | Latex Formula | formula-block | formula | Rendered | `S + U \longrightarrow \hat{G}=(\hat{V},\hat{E})` | none | research |
| formula_09_mapping.png | 268x60 | 4.47 | P09 mapping formula | Latex Formula | formula-block | formula | Rendered | `F(S,U)=\hat{G}` | none | research |
| formula_09_s.png | 30x36 | 0.83 | P09 sketch input variable | Latex Formula | formula-inline | formula | Rendered | `S` | none | research |
| formula_09_u.png | 34x35 | 0.97 | P09 speech input variable | Latex Formula | formula-inline | formula | Rendered | `U` | none | research |
| formula_09_graph.png | 236x60 | 3.93 | P09 output graph formula | Latex Formula | formula-block | formula | Rendered | `\hat{G}=(\hat{V},\hat{E})` | none | research |
| formula_10_gs.png | 51x43 | 1.19 | P10 sketch graph symbol | Latex Formula | formula-inline | formula | Rendered | `G_s` | none | research |
| formula_10_gu.png | 56x43 | 1.30 | P10 speech graph symbol | Latex Formula | formula-inline | formula | Rendered | `G_u` | none | research |
| formula_10_gf.png | 56x50 | 1.12 | P10 fused graph symbol | Latex Formula | formula-inline | formula | Rendered | `G_f` | none | research |
| formula_10_path.png | 438x51 | 8.59 | P10 graph path formula | Latex Formula | formula-block | formula | Rendered | `G_{0:T}=\{G_0,\ldots,G_T\}` | none | research |
| formula_10_ghat.png | 36x48 | 0.75 | P10 output graph symbol | Latex Formula | formula-inline | formula | Rendered | `\hat{G}` | none | research |
| formula_10_cost.png | 952x124 | 7.68 | P10 edit cost formula | Latex Formula | formula-block | formula | Rendered | `\begin{aligned}c(G_t,G_{t+1})=&\ c_{\mathrm{GED}}+\lambda_{\mathrm{label}}c_{\mathrm{label}}+\lambda_{\mathrm{dir}}c_{\mathrm{direction}}\\&+\lambda_{\mathrm{layout}}c_{\mathrm{layout}}-\lambda_{\mathrm{speech}}r_{\mathrm{coverage}}\end{aligned}` | none | research |
| formula_10_energy.png | 617x142 | 4.35 | P10 path energy formula | Latex Formula | formula-block | formula | Rendered | `E(G_{0:T})=\frac{1}{T}\sum_{t=0}^{T-1}c(G_t,G_{t+1})^2` | none | research |
| formula_11_metrics_1.png | 527x55 | 9.58 | P11 structural metrics formula line | Latex Formula | formula-block | formula | Rendered | `F_1^{N}\cdot F_1^{E}\cdot A_{\mathrm{dir}}\cdot GED_{\mathrm{norm}}` | none | research |
| formula_11_metrics_2.png | 634x52 | 12.19 | P11 usability metrics formula line | Latex Formula | formula-block | formula | Rendered | `C_{\mathrm{speech}}\cdot P_{\mathrm{layout}}\cdot C_{\mathrm{edit}}\cdot E(G_{0:T})` | none | research |
| formula_12_sketch.png | 348x46 | 7.57 | P12 sketch-only result | Latex Formula | formula-inline | formula | Rendered | `\mathrm{Edge}\ F_1=0.387` | none | research |
| formula_12_speech.png | 348x46 | 7.57 | P12 speech-only result | Latex Formula | formula-inline | formula | Rendered | `\mathrm{Edge}\ F_1=0.564` | none | research |
| formula_12_node.png | 351x43 | 8.16 | P12 early-fusion node result | Latex Formula | formula-inline | formula | Rendered | `\mathrm{Node}\ F_1=0.929` | none | research |
| formula_12_edge.png | 348x46 | 7.57 | P12 early-fusion edge result | Latex Formula | formula-inline | formula | Rendered | `\mathrm{Edge}\ F_1=0.577` | none | research |
| formula_12_greedy.png | 346x46 | 7.52 | P12 greedy result | Latex Formula | formula-inline | formula | Rendered | `\mathrm{Edge}\ F_1=0.842` | none | research |
| formula_12_mmsb.png | 493x50 | 9.86 | P12 MMSB-Graph result | Latex Formula | formula-inline | formula | Rendered | `N/E/D=1,\ \mathrm{GED}=0` | none | research |
| formula_13_metrics.png | 330x45 | 7.33 | P13 evaluation node formula | Latex Formula | formula-inline | formula | Rendered | `F_1,\ \mathrm{GED},\ \mathrm{Cost}` | none | closing |
| formula_14_metrics.png | 401x50 | 8.02 | P14 evaluation value formula | Latex Formula | formula-inline | formula | Rendered | `\mathrm{GED},\ F_1,\ E(G_{0:T})` | none | closing |

No AI-generated images are used. Formula assets are deterministic LaTeX renders produced from `images/formula_manifest.json`.

---

## IX. Content Outline

### Part 1: Product Story - from messy expression to reusable output

#### Slide 01 - SketchVoice：把“边说边画”变成可编辑知识图

- **Layout**: Anchor cover; large title left, right side abstract product-flow motif.
- **Title**: SketchVoice：把“边说边画”变成可编辑知识图
- **Core message**: 这个项目不是只做一个模型，而是做一个从自然表达输入到结构化输出的多模态产品原型。
- **Content**: 课程答辩 / 语音引导的知识草图结构化 / MMSB-Graph / 2026.

#### Slide 02 - 产品出发点：科研讨论结束后，信息很难复用

- **Layout**: Three pain cards plus a small user scene.
- **Title**: 产品出发点：科研讨论结束后，信息很难复用
- **Core message**: 用户真正的问题不是“不会画图”，而是草图、语音和最终方法图之间缺少可复用的结构桥梁。
- **Content**: 草图保留了空间关系，但标签、箭头和语义经常不完整；语音说清了节点含义和因果意图，但没有二维布局；讨论结束后，用户还需要手动整理 Mermaid、图像、JSON 和讲解稿。

#### Slide 03 - 用户旅程：从画布和录音到多格式交付

- **Layout**: 5-stage horizontal pipeline with output artifacts.
- **Title**: 用户旅程：从画布和录音到多格式交付
- **Core message**: SketchVoice 的产品闭环把一次口头讲解转化为一组可查看、可下载、可讲解的交付物。
- **Visualization**: pipeline_with_stages.
- **Content**: 画草图 / 录音或上传音频 / 结构化建模 / Mermaid、SVG、JSON 预览 / 终稿图与语音讲解 WebM。每一步都对应用户能看见和能下载的产物。

#### Slide 04 - 产品能力：不只是生成图，而是生成“工作台”

- **Layout**: 2x3 capability grid.
- **Title**: 产品能力：不只是生成图，而是生成“工作台”
- **Core message**: 产品侧价值来自完整操作面，而不是单次模型调用。
- **Visualization**: icon_grid.
- **Content**: 输入侧支持草图画布、录音、上传音频和文本补充；生成侧输出结构化图、Mermaid、AI 草稿图和终稿图；交付侧支持下载 JSON/SVG/Mermaid/图像/WebM；演示侧提供 mock 模式和样例数据，保证课堂展示不断。

#### Slide 05 - 现场演示流程：从一张草图到可讲解交付物

- **Layout**: Six-step horizontal demo pipeline with a bottom presenter script.
- **Title**: 现场演示流程：从一张草图到可讲解交付物
- **Core message**: 演示重点不是单次生成图片，而是展示输入、结构化、渲染、讲解和下载的完整链路。
- **Visualization**: pipeline_with_stages.
- **Content**: 画一个“输入数据 → 模型 → 评测指标”的简单草图；口头补充中间其实有语音转写、草图解析和多模态融合；点击生成后展示 Mermaid、SVG、JSON；再生成论文风格终稿图和语音讲解 WebM，证明系统是输入、生成、展示、导出闭环。

### Part 2: Research engine behind the product

#### Slide 06 - 系统架构：前端交互、后端服务和模型能力分层

- **Layout**: Layered architecture with four horizontal bands.
- **Title**: 系统架构：前端交互、后端服务和模型能力分层
- **Core message**: 产品闭环由浏览器工作台、FastAPI 接口、结构化模型、图像/语音服务共同完成。
- **Visualization**: layered_architecture.
- **Content**: 前端负责画布、录音、上传、标签页预览、下载和光标讲解；后端暴露 `/api/generate`、`/api/render-image`、`/api/narrate-image`；模型侧负责 ASR、多模态结构化、图像生成和 TTS；输出层统一为 Mermaid、SVG、JSON、终稿图和 WebM。

#### Slide 07 - 科研定位：语音引导的知识草图结构化

- **Layout**: Three-column modality cards with a formal input-output definition and hypothesis strip.
- **Title**: 科研定位：语音引导的知识草图结构化
- **Core message**: 这不是“语音生成图片”，而是从手绘草图与同步语音中恢复可编辑知识图。
- **Visualization**: vertical_list.
- **Content**: 输入是手绘知识草图 `$S$` 与同步语音描述 `$U$`，输出是 `$\hat{G}=(\hat{V},\hat{E})$`。草图提供空间先验，语音提供语义锚点和关系顺序；研究假设包括语音补全节点标签、口头顺序纠正边方向、显式图编辑路径降低用户修改成本并提供诊断信号。

#### Slide 08 - 相关工作：三条路线都没有同时覆盖我们的场景

- **Layout**: Three related-work cards plus a bottom positioning strip.
- **Title**: 相关工作：三条路线都没有同时覆盖我们的场景
- **Core message**: 现有工作分别处理草图结构、静态图代码化或图迁移理论，但缺少同步语音下的知识图结构恢复与诊断。
- **Visualization**: hub_inward_arrows.
- **Content**: SketchAgent/Sketch2Diagram 代表草图到结构图路线，但缺同步语音；Flowchart2Mermaid 代表静态图到可编辑代码路线，但场景封闭；Schrödinger Bridge / DDSBM 提供离散图结构迁移理论支点。我们的切入点是 Sketch + Speech → Structured Knowledge Graph → Graph Editing Diagnosis。

#### Slide 09 - 任务定义：Speech-Guided Sketch-to-Knowledge-Graph

- **Layout**: Input-to-output process flow with metric bar.
- **Title**: 任务定义：Speech-Guided Sketch-to-Knowledge-Graph
- **Core message**: 将产品链路形式化为可比较、可复现实验的结构恢复任务。
- **Visualization**: process_flow.
- **Content**: 手绘草图包含框、箭头、布局和手写文字；同步语音包含节点名、关系顺序和设计意图。系统恢复候选节点、候选边、方向、标签和布局，最终输出 Mermaid/SVG/JSON/论文风格图像。评测关注 `$\mathrm{Node}\ F_1$`、`$\mathrm{Edge}\ F_1$`、`$\mathrm{Direction\ Accuracy}$`、`$\mathrm{Speech\ Coverage}$`、`$\mathrm{Layout\ Preservation}$`、`$\mathrm{Normalized\ GED}$` 和 `$\mathrm{Edit\ Cost}$`。

### Part 3: Evaluation, loop, and final value

#### Slide 10 - MMSB-Graph：多模态约束下的离散图编辑桥

- **Layout**: Method process flow plus edit action and cost panels.
- **Title**: MMSB-Graph：多模态约束下的离散图编辑桥
- **Core message**: 核心不是 one-shot generation，而是把候选图沿低代价编辑路径修复为目标知识图。
- **Visualization**: process_flow.
- **Content**: 方法链路为 `$S \rightarrow G_s$`、`$U \rightarrow G_u$`、`$(G_s,G_u)\rightarrow G_f$`、`$G_f \rightarrow \hat{G}$`。编辑动作包括删多余节点、插缺失节点、删错误边、插目标边与修方向。代价函数由 `$c_{\mathrm{GED}}$`、标签距离、方向惩罚、布局保持和语音覆盖奖励组成，路径能量用于解释修复难度。

#### Slide 11 - 数据与实验：把 demo 标注成可评测样例

- **Layout**: Dataset card, baseline table, metric grid, and controlled-validation warning.
- **Title**: 数据与实验：把 demo 标注成可评测样例
- **Core message**: 我们把原型演示转化为 24 个带金标准的可控知识草图样例，并建立多指标评测协议。
- **Visualization**: basic_table.
- **Content**: 样例覆盖线性流程、多分支融合、反馈闭环、模型架构和实验流程；每例包含草图、语音、转写、目标节点边、语音锚点、草图区、布局坐标与难度标签。对照包括 Sketch-only、Speech-only、Early Fusion、Greedy Repair 和 MMSB-Graph。当前实验是合成条件图可控验证，不调用真实 VLM/ASR。

#### Slide 12 - 结果边界：验证的是图桥行为，不是大规模 SOTA

- **Layout**: Method result table with boundary and future-work panels.
- **Title**: 结果边界：验证的是图桥行为，不是大规模 SOTA
- **Core message**: 展示已经做出的结构恢复结果，同时明确受控实验边界和后续科研深化路线。
- **Visualization**: basic_table.
- **Content**: Sketch-only `$\mathrm{Edge}\ F_1=0.387$`，Speech-only `$\mathrm{Edge}\ F_1=0.564$`，Early Fusion `$\mathrm{Node}\ F_1=0.929$` / `$\mathrm{Edge}\ F_1=0.577$`，Greedy Repair `$\mathrm{Edge}\ F_1=0.842$`，MMSB-Graph 在可控条件下 `$\mathrm{N}/\mathrm{E}/\mathrm{D}=1.000,\ \mathrm{GED}=0$`。边界是未接入真实 ASR/VLM、不能代表真实世界端到端泛化；未来接入真人草图、用户修改轨迹、语义嵌入检索和可训练 edit policy。

#### Slide 13 - 项目知识图谱：我们实际完成了哪些节点

- **Layout**: Knowledge graph with SketchVoice at the center.
- **Title**: 项目知识图谱：我们实际完成了哪些节点
- **Core message**: 把应用侧、科研侧和工程侧放到同一张图里，展示成果之间的依赖关系。
- **Visualization**: mind_map.
- **Content**: 节点包括产品原型、结构输出、终稿与讲解、科研任务、方法模型、数据资产、评测结果、工程保障和可解释轨迹。每个节点都对应真实实现，而不是只停留在概念命名。中心是 SketchVoice，外圈展示的是项目做成了什么。

#### Slide 14 - 总结：把自然表达升级为可研究的知识结构生产线

- **Layout**: Five-value summary with closing claim.
- **Title**: 总结：把自然表达升级为可研究的知识结构生产线
- **Core message**: SketchVoice 不是单点 demo，而是“应用闭环 + 科研模型 + 评测协议 + 可解释诊断”的完整链路。
- **Content**: 产品层上，它完成了可操作工作台和多格式交付；科研层上，它定义了语音引导知识草图结构化与 MMSB-Graph；评测层上，它提供 24 个可控样例和多指标协议；工程层上，它具备可替换服务和 mock fallback；应用层上，它能把课堂和科研讲解沉淀为结构化资产。最后的结论是：这个项目既有能演示的应用成果，也有可继续深化的科研问题和实验框架。

---

## X. Speaker Notes Requirements

One speaker note file per page, saved to `notes/`:

- **Filename**: match SVG name, e.g. `01_title.md`.
- **Duration**: 8-12 minutes.
- **Style**: formal but conversational Chinese, product story first, then research support.
- **Purpose**: persuade and report; avoid over-claiming experiment generalization.
- **Split rule**: `notes/total.md` uses slide headings; split note files must not contain heading lines.

---

## XI. Technical Constraints Reminder

### SVG Generation Must Follow

1. viewBox: `0 0 1280 720`
2. Background uses `<rect>` elements.
3. Text wrapping uses `<tspan>`; `<foreignObject>` is forbidden.
4. Transparency uses `fill-opacity` / `stroke-opacity`; `rgba()` is forbidden.
5. Forbidden: `<style>`, `class`, `textPath`, `animate*`, `script`, `<iframe>`, `<g opacity>`.
6. Icons must use only `tabler-outline` placeholders listed in Section VI.
7. Images must reference files listed in Section VIII.
8. Chinese text stays as raw UTF-8 characters. XML-reserved characters must be escaped.

### PPT Compatibility Rules

- Do not use group opacity.
- Do not use CSS classes or external CSS.
- Keep important content inside the 52px safe margin.
- Use rounded rectangles with radius <= 8px for cards.
