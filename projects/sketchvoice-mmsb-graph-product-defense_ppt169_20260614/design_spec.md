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
| P08 | vertical_pillars | `templates/charts/vertical_pillars.svg` | "Pick for 1×3 / 1×4 / 1×5 vertical column layout where each pillar = one independent category with title + bullets — PEST (Political/Economic/Social/Technological), four-pillar strategy overview, side-by-side independent categories. Skip for 2×2 quadrant (use quadrant_text_bullets), pricing tiers (use comparison_columns), or 2×2 parallel aspects (use labeled_card)." | Three intermediate graphs |
| P09 | process_flow | `templates/charts/process_flow.svg` | "Pick for 3-8 sequential steps connected by simple arrows — approval workflows, customer onboarding, request handling, lifecycle stages. Skip if cyclical (use circular_stages) or stages produce named outputs (use pipeline_with_stages)." | Graph editing bridge |
| P10 | icon_grid | `templates/charts/icon_grid.svg` | "Pick for 4-9 parallel features/capabilities/services as icon cards — feature grid, service lineup, benefits matrix, brand values, product highlights. Skip for sequential ordering (use numbered_steps) or hierarchical layers (use pyramid_chart)." | Dataset and metric overview |
| P11 | basic_table | `templates/charts/basic_table.svg` | "Pick for plain tabular text/number grid, 3-8 columns. Skip if cells need visual bars (use consulting_table) or qualitative scores (use harvey_balls_table)." | Method comparison results |
| P12 | circular_stages | `templates/charts/circular_stages.svg` | "Pick for 4-6 stage closed loop where stages compose a cycle — PDCA, flywheel compounding loops (Attract → Engage → Delight), lifecycle, continuous improvement. Skip for linear flow (use process_flow), one-shot sequence (use numbered_steps), or wedge-based central topic (use segmented_wheel)." | Engineering product loop |
| P13 | vertical_list | `templates/charts/vertical_list.svg` | "Pick for 3-6 numbered key points each with a short description — design principles, core tenets, action items, key takeaways, recommendations, executive summary points. Skip for icon-style cards (use icon_grid) or sequential steps (use numbered_steps)." | Boundary and value explanation |

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

#### Slide 08 - 三种中间图：把不完整信息显式拆开

- **Layout**: Three vertical pillars converging to a fusion graph.
- **Title**: 三种中间图：把不完整信息显式拆开
- **Core message**: `Gs`、`Gu`、`Gf` 让产品调试从黑箱输出变成可观察过程。
- **Visualization**: vertical_pillars.
- **Content**: `Gs` 来自草图解析，保留空间结构但语义弱；`Gu` 来自语音转写，语义强但没有布局；`Gf` 融合两者，作为编辑桥的初始候选图。这个拆分也对应用户可能看到的错误来源。

#### Slide 09 - 图编辑桥：逐步恢复，而不是一次猜完

- **Layout**: Process flow with edit operations and cost badges.
- **Title**: 图编辑桥：逐步恢复，而不是一次猜完
- **Core message**: 图编辑桥把结构恢复转化为可追踪的离散编辑路径。
- **Visualization**: process_flow.
- **Content**: 允许插入节点、删除节点、插入边、删除边和修正边方向。单步代价 `c(Gt, Gt+1)` 由结构变化、语义距离、方向惩罚、布局保持和语音覆盖组成；路径能量 `E(G0:T) = 1/T Σ c(Gt, Gt+1)^2` 衡量整体修复是否自然。

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

#### Slide 12 - 工程闭环：产品、模型、评测可以互相反馈

- **Layout**: Circular stages loop.
- **Title**: 工程闭环：产品、模型、评测可以互相反馈
- **Core message**: 这个项目的完整性体现在“用户可操作、模型可替换、结果可评测”。
- **Visualization**: circular_stages.
- **Content**: 用户输入产生结构图；结构图驱动 Mermaid、SVG、图像和讲解；评测系统对齐预测图与标准图；指标反馈到样例构建和模型策略；mock 模式保障无 key 时也能完整演示。

#### Slide 13 - 真实性边界：当前是可控验证，不是大规模宣称

- **Layout**: Vertical list with boundary, value, next step.
- **Title**: 真实性边界：当前是可控验证，不是大规模宣称
- **Core message**: 产品原型已经跑通闭环，但科研结论需要清楚限定在合成条件图的可控验证范围内。
- **Visualization**: vertical_list.
- **Content**: 当前实验用于验证任务定义、评测链路和图编辑过程可计算性；它不等价于大规模真实世界性能。下一步可以扩展真实用户数据、引入更强草图识别、记录用户实际修改成本，并把评测指标接入前端反馈。

#### Slide 14 - 总结：产品闭环 + 方法支撑 + 可评测系统

- **Layout**: Three contribution blocks plus closing sentence.
- **Title**: 总结：产品闭环 + 方法支撑 + 可评测系统
- **Core message**: 本项目的贡献不只在算法，也在把算法放进一个可演示、可编辑、可评测的产品闭环里。
- **Content**: 产品层：构建 SketchVoice 方法图工作台，从草图和语音到 Mermaid、JSON、SVG、终稿图和 WebM。方法层：提出语音引导的知识草图结构化任务和 MMSB-Graph 图编辑桥。系统层：实现输入、生成、展示、导出和评测闭环。一句话结论：SketchVoice 将“语音 + 草图”的自然表达过程转化为可编辑知识图，MMSB-Graph 则提供可解释的结构恢复路径。

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
