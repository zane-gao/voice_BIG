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

Eight confirmations were approved by the user: `ppt169`, 14 pages, course-defense audience, product story first, blue-green restrained palette, built-in `tabler-outline` icons, CJK-first typography, mixed formula policy, existing report figure only.

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
- **Mode behavior**: Three-act product-defense narrative. Act 1 starts from a real user workflow and product pain: people explain research by drawing and speaking, but the result is hard to reuse. Act 2 introduces MMSB-Graph as the structural engine that makes the product reliable, editable, and diagnosable. Act 3 closes with evaluation, engineering loop, boundary, and contributions. Titles should sound like claims rather than chapter labels.
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

Formula policy: `mixed`. This deck keeps simple notation editable as text (`G_hat = (V, E)`, `c(Gt, Gt+1)`, `E(G0:T) = 1/T Σ c^2`) and does not require rendered formula PNG assets.

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
| 图像生成 | `tabler-outline/photo` | P04, P12 |
| 语音讲解 | `tabler-outline/speakerphone` | P04, P12 |
| 数据集 | `tabler-outline/database` | P10 |
| 评测结果 | `tabler-outline/chart-dots` | P10, P11 |
| 实验验证 | `tabler-outline/test-pipe` | P11 |
| 多模态融合 | `tabler-outline/layers-linked` | P07, P08 |
| 服务端架构 | `tabler-outline/server` | P06 |
| 图编辑路径 | `tabler-outline/git-branch` | P09 |
| 目标任务 | `tabler-outline/target` | P05, P14 |
| 核心贡献 | `tabler-outline/bulb` | P14 |
| 自动生成 | `tabler-outline/wand` | P03, P04 |
| 演示与答辩 | `tabler-outline/presentation` | P01 |
| 视频讲解 | `tabler-outline/video` | P04, P12 |

---

## VII. Visualization Reference List

Catalog read: 71 templates

| Page | Template | Path | Summary-quote (verbatim from `charts_index.json`) | Usage |
| ---- | -------- | ---- | ------------------------------------------------- | ----- |
| P03 | basic_table | `templates/charts/basic_table.svg` | "Pick for plain tabular text/number grid, 3-8 columns. Skip if cells need visual bars (use consulting_table) or qualitative scores (use harvey_balls_table)." | Competitive positioning matrix |
| P04 | icon_grid | `templates/charts/icon_grid.svg` | "Pick for 4-9 parallel features/capabilities/services as icon cards — feature grid, service lineup, benefits matrix, brand values, product highlights. Skip for sequential ordering (use numbered_steps) or hierarchical layers (use pyramid_chart)." | Product capability map |
| P05 | pipeline_with_stages | `templates/charts/pipeline_with_stages.svg` | "Pick for 3-5 horizontal pipeline stages, each = title + 1-line description + output artifact, connected by arrows (data pipelines, ETL, build pipelines). Skip if any stage lacks an artifact (use process_flow or numbered_steps)." | Live demo flow from sketch to WebM |
| P06 | layered_architecture | `templates/charts/layered_architecture.svg` | "Pick for 3-4 horizontal architecture layers (presentation/service/data), 2-4 module cards per layer, each card = title + 1-line description (description required, even if source brief). Skip if no per-module descriptions (use icon_grid) or no horizontal layering (use module_composition)." | System architecture |
| P07 | vertical_list | `templates/charts/vertical_list.svg` | "Pick for 3-6 numbered key points each with a short description — design principles, core tenets, action items, key takeaways, recommendations, executive summary points. Skip for icon-style cards (use icon_grid) or sequential steps (use numbered_steps)." | Research task definition bridge |
| P08 | hub_inward_arrows | `templates/charts/hub_inward_arrows.svg` | "Pick for 1 center subject + 4-5 surrounding forces with arrows pointing inward — Porter's Five Forces (central rivalry, threat of new entrants/substitutes, bargaining power of buyers/suppliers), threat-model with central asset, pressure-on-core diagrams. Skip for outward radiation from center capability (use hub_spoke) or non-directional cluster (use mind_map)." | MMSB-Graph multi-constraint model |
| P09 | process_flow | `templates/charts/process_flow.svg` | "Pick for 3-8 sequential steps connected by simple arrows — approval workflows, customer onboarding, request handling, lifecycle stages. Skip if cyclical (use circular_stages) or stages produce named outputs (use pipeline_with_stages)." | Graph editing bridge |
| P10 | icon_grid | `templates/charts/icon_grid.svg` | "Pick for 4-9 parallel features/capabilities/services as icon cards — feature grid, service lineup, benefits matrix, brand values, product highlights. Skip for sequential ordering (use numbered_steps) or hierarchical layers (use pyramid_chart)." | Dataset and metric overview |
| P11 | basic_table | `templates/charts/basic_table.svg` | "Pick for plain tabular text/number grid, 3-8 columns. Skip if cells need visual bars (use consulting_table) or qualitative scores (use harvey_balls_table)." | Method comparison results |
| P12 | circular_stages | `templates/charts/circular_stages.svg` | "Pick for 4-6 stage closed loop where stages compose a cycle — PDCA, flywheel compounding loops (Attract → Engage → Delight), lifecycle, continuous improvement. Skip for linear flow (use process_flow), one-shot sequence (use numbered_steps), or wedge-based central topic (use segmented_wheel)." | Engineering product loop |
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

No AI-generated images are used. The deck has only one image-bearing page, so the image-as-canvas coverage rule does not apply.

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

#### Slide 07 - 科研侧：把产品需求抽象成结构恢复任务

- **Layout**: Left claim block, right formal task definition, bottom hypothesis strip.
- **Title**: 科研侧：把产品需求抽象成结构恢复任务
- **Core message**: 从产品角度看是“语音画图工具”，从科研角度看是语音引导的知识草图结构化。
- **Visualization**: vertical_list.
- **Content**: 给定手绘草图 `S` 与同步语音 `U`，目标是重建知识图 `G_hat = (V, E)`。草图提供模块位置、箭头和空间关系；语音提供节点名称、关系方向和设计意图。三个核心假设是：语音能补全节点标签，口头叙述顺序能纠正边方向，显式编辑路径能降低用户修改成本。

#### Slide 08 - MMSB-Graph：把多模态输入放进同一图状态空间

- **Layout**: Left-side constraint sources, central bridge model, right-side target distribution.
- **Title**: MMSB-Graph：把多模态输入放进同一图状态空间
- **Core message**: 核心不是直接“画好看”，而是在离散知识图空间里求一条低代价、可解释的结构恢复路径。
- **Visualization**: hub_inward_arrows.
- **Content**: `Gs` 提供草图边缘约束，保留位置、邻接和箭头粗方向；`Gu` 提供语音语义约束，补充标签、顺序和关系意图；`Gf` 形成早期融合候选。MMSB-Graph 把这些边缘约束统一进图状态空间，求解 `min_P KL(P||R) + λs Cs + λu Cu + λf Cf`，其中 `R` 是允许节点和边编辑的参考过程。目标不是一个单点预测，而是一条从 `G0` 到 `GT` 的可解释路径。

#### Slide 09 - 训练与推理：先把编辑路径变成可计算对象

- **Layout**: Trainable extension left/right cards with process and math panels.
- **Title**: 训练与推理：先把编辑路径变成可计算对象
- **Core message**: 当前实现验证图桥和指标链路；同一套路径表示也能扩展为可监督训练与能量重排序。
- **Visualization**: process_flow.
- **Content**: 现阶段代码用确定性图编辑桥和 gold graph 做可控 sanity check，验证任务定义、指标和路径代价可运行；可训练扩展则可以把人工修正轨迹、候选图和编辑序列转成 edit policy 或 energy reranker。编辑动作空间包括插入节点、删除节点、插入边、删除边与修正方向。单步代价 `c(Gt, Gt+1)` 由结构变化、语义距离、方向惩罚、布局保持和语音覆盖组成；路径能量 `E(G0:T) = 1/T Σ c(Gt, Gt+1)^2` 既是诊断量，也能作为学习信号。

### Part 3: Evaluation, loop, and final value

#### Slide 10 - 数据与评测：用可控样例验证链路

- **Layout**: Dataset summary plus metric grid.
- **Title**: 数据与评测：用可控样例验证链路
- **Core message**: 评测不是只看“图像好不好看”，而是看结构是否正确、语音是否覆盖、修改成本是否下降。
- **Visualization**: icon_grid.
- **Content**: 构建 24 个知识草图样例，覆盖线性流程、分支结构、反馈闭环、模型架构图和实验流程图。指标包括 Node F1、Edge F1、Direction Accuracy、Normalized GED、Speech Coverage、Layout Preservation、Edit Cost、Path Energy。

#### Slide 11 - 实验结果：多模态编辑路径带来结构一致性

- **Layout**: Top metric table, bottom diagnostic image band.
- **Title**: 实验结果：多模态编辑路径带来结构一致性
- **Core message**: 在可控验证中，MMSB-Graph 同时提升节点、边和方向恢复，并把人工修改成本降到最低。
- **Visualization**: basic_table.
- **Content**: Sketch only 的 Edge F1 为 0.387，Speech only 提升到 0.564，Early Fusion 提升节点但边仍不稳，Greedy Repair 能局部修复，MMSB-Graph 达到 Node/Edge F1 1.000、Normalized GED 0、manual edit cost 0。诊断图用于展示结构恢复、GED 和桥路径负载。
- **Image**: `mmsb_diagnostics.png`.

#### Slide 12 - 可解释性：让生成结果能被追问、定位和改进

- **Layout**: Diagnostic loop with evidence panel.
- **Title**: 可解释性：让生成结果能被追问、定位和改进
- **Core message**: 科研价值来自可诊断的结构恢复过程，而不是只输出一张看起来正确的图。
- **Visualization**: circular_stages.
- **Content**: 中间图可以定位错误来源，编辑轨迹可以解释每一步修复，指标可以把解释落到数字，真实用户修改轨迹还可以反哺训练与交互策略。这样系统从“能生成”提升为“能解释、能评测、能被真实使用数据持续改进”。

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
