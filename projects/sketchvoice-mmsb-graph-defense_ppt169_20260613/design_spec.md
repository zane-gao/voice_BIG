# SketchVoice MMSB-Graph Defense - Design Spec

> Human-readable design narrative. Machine-readable execution contract: `spec_lock.md`.

## I. Project Information

| Item | Value |
| ---- | ----- |
| Project Name | SketchVoice MMSB-Graph Defense |
| Canvas Format | PPT 16:9 (1280x720) |
| Page Count | 14 |
| Design Style | Instructional research defense, Swiss-minimal visual style |
| Target Audience | 语音信息处理课程答辩教师与同学 |
| Use Case | 课程结项答辩，8-12 分钟 |
| Created Date | 2026-06-13 |

Eight confirmations were supplied by the implementation plan and are treated as confirmed: `ppt169`, 14 pages, course defense audience, blue-green restrained academic style, built-in icons, CJK-first typography, `mixed` formula policy, existing report figure and table assets only.

---

## II. Canvas Specification

| Property | Value |
| -------- | ----- |
| Format | PPT 16:9 |
| Dimensions | 1280x720 |
| viewBox | `0 0 1280 720` |
| Margins | 52px left/right, 44px top, 36px bottom |
| Content Area | 1176x600 after title/footer reservation |

---

## III. Visual Theme

### Theme Style

- Mode: `instructional`
- Visual style: `swiss-minimal`
- Theme: Light theme
- Tone: 清晰、克制、科研答辩、结构化

### Color Scheme

| Role | HEX | Purpose |
| ---- | --- | ------- |
| Background | `#F8FAFC` | page background |
| Surface | `#FFFFFF` | panels, cards, table blocks |
| Primary | `#155E75` | titles, key shapes, section rules |
| Accent | `#0F766E` | semantic highlights and selected paths |
| Secondary accent | `#2563EB` | comparison marks and links |
| Warm accent | `#F59E0B` | warnings, boundary notes |
| Body text | `#172033` | main text |
| Secondary text | `#475569` | annotations |
| Tertiary text | `#94A3B8` | footer and page numbers |
| Border/divider | `#CBD5E1` | separators and card borders |
| Soft blue | `#E0F2FE` | light background fills |
| Soft teal | `#CCFBF1` | light semantic fills |
| Soft amber | `#FEF3C7` | limitation / boundary fills |
| Soft green | `#DCFCE7` | contribution / success fills |

### Gradient Scheme

Use subtle linear gradients only on section bands or bridge arrows. No decorative blobs. Primary gradient: `#155E75` to `#0F766E`.

---

## IV. Typography System

### Font Plan

Typography direction: CJK-first clean sans, with monospace only for symbolic graph variables.

| Role | Chinese | English | Fallback tail |
| ---- | ------- | ------- | ------------- |
| Title | `"Microsoft YaHei"` | `Arial` | `sans-serif` |
| Body | `"Microsoft YaHei"` | `Arial` | `sans-serif` |
| Emphasis | `SimHei` | `Arial` | `sans-serif` |
| Code | - | `Consolas`, `"Courier New"` | `monospace` |

Per-role font stacks:

- Title: `"Microsoft YaHei", Arial, sans-serif`
- Body: `"Microsoft YaHei", Arial, sans-serif`
- Emphasis: `SimHei, "Microsoft YaHei", Arial, sans-serif`
- Code: `Consolas, "Courier New", monospace`

### Font Size Hierarchy

Baseline body size: 22px.

| Purpose | Size |
| ------- | ---- |
| Cover title | 58-68px |
| Page title | 34-38px |
| Subtitle | 24-28px |
| Body | 20-22px |
| Caption / annotation | 14-16px |
| Footer | 12px |

Formula policy: `mixed`. The deck uses short editable notation rather than rendered formula PNGs, so no `formula_manifest.json` is required.

---

## V. Layout Principles

### Page Structure

- Header area: 44-92px, title and small page marker.
- Content area: 560-600px, varies by page rhythm.
- Footer area: 24-36px, project label and page number.

### Layout Pattern Library

- `anchor`: cover, summary, and section bridge pages. Strong whitespace, one central message.
- `dense`: method, dataset, experiment, and results pages. Use tables, flow nodes, comparison columns, and metric tiles.
- `breathing`: pages that need a single idea to land. Avoid multi-card grids; use large statement plus one diagram or contrast.

### Spacing Specification

| Element | Current Project |
| ------- | --------------- |
| Safe margin | 52px |
| Content block gap | 28-36px |
| Icon-text gap | 10-14px |
| Card gap | 22-28px |
| Card padding | 22-28px |
| Card radius | 8px maximum |
| Table row height | 44-54px |

---

## VI. Icon Usage Specification

Source: built-in `tabler-outline` icon library, stroke width 2. One stylistic icon library only.

| Purpose | Icon Path | Page |
| ------- | --------- | ---- |
| 语音输入 | `tabler-outline/microphone` | P02, P04 |
| 草图输入 | `tabler-outline/pencil` | P02, P04 |
| 知识图 | `tabler-outline/network` | P03, P06 |
| 方法路径 | `tabler-outline/route` | P08, P09 |
| 多模态层次 | `tabler-outline/layers-linked` | P06, P07 |
| 数据集 | `tabler-outline/database` | P10 |
| 实验验证 | `tabler-outline/test-pipe` | P11 |
| 结果图表 | `tabler-outline/chart-dots` | P12 |
| 目标任务 | `tabler-outline/target` | P03, P14 |
| 研究贡献 | `tabler-outline/bulb` | P14 |

---

## VII. Visualization Reference List

Catalog read: 71 templates.

| Page | Template | Path | Summary-quote (verbatim from `charts_index.json`) | Usage |
| ---- | -------- | ---- | ------------------------------------------------- | ----- |
| P06 | pipeline_with_stages | `templates/charts/pipeline_with_stages.svg` | "Pick for 3-5 horizontal pipeline stages, each = title + 1-line description + output artifact, connected by arrows (data pipelines, ETL, build pipelines). Skip if any stage lacks an artifact (use process_flow or numbered_steps)." | MMSB-Graph method overview |
| P08 | process_flow | `templates/charts/process_flow.svg` | "Pick for 3-8 sequential steps connected by simple arrows 鈥?approval workflows, customer onboarding, request handling, lifecycle stages. Skip if cyclical (use circular_stages) or stages produce named outputs (use pipeline_with_stages)." | Graph editing bridge operations |
| P11 | vertical_list | `templates/charts/vertical_list.svg` | "Pick for 3-6 numbered key points each with a short description 鈥?design principles, core tenets, action items, key takeaways, recommendations, executive summary points. Skip for icon-style cards (use icon_grid) or sequential steps (use numbered_steps)." | Experiment design comparison list |
| P12 | basic_table | `templates/charts/basic_table.svg` | "Pick for plain tabular text/number grid, 3-8 columns. Skip if cells need visual bars (use consulting_table) or qualitative scores (use harvey_balls_table)." | Result table |

Runners-up considered:

- `numbered_steps` | rejected for P08: operations include correction/deletion/insertion but arrowed process better emphasizes graph transition.
- `comparison_table` | rejected for P12: the result table is metric reporting, not feature comparison across rows.
- `kpi_cards` | rejected for P12: key numbers matter, but the page needs method-by-method comparison rather than isolated metrics.

---

## VIII. Image Resource List

| Filename | Dimensions | Ratio | Purpose | Type | Layout pattern | Acquire Via | Status | Reference | text_policy | page_role |
| -------- | ---------- | ----- | ------- | ---- | -------------- | ----------- | ------ | --------- | ----------- | --------- |
| mmsb_diagnostics.png | 3514x1309 | 2.68 | Report diagnostic figure for structural recovery, GED distribution, and bridge load | Diagram | #6 Bottom-band image + top title + middle text + #70 Image with thin colored matte frame | user | Existing | `report/figures/mmsb_diagnostics.png` copied into project images | none | local |

No AI-generated images are used.

---

## IX. Content Outline

### Part 1: Problem and Motivation

#### Slide 01 - 标题页

- Layout: Anchor cover with left title column and right abstract graph motif.
- Title: 语音引导的知识草图结构化与 MMSB-Graph
- Core message: 本项目把“边说边画”的科研表达形式转化为可研究、可评测、可编辑的知识图结构化任务。
- Content: 课程项目 / SketchVoice / MMSB-Graph / 2026年6月。

#### Slide 02 - 真实场景：科研表达通常是“草图 + 语音”

- Layout: Two input panels converging into a mixed expression strip.
- Core message: 科研讨论中的信息往往同时存在空间结构和口头语义。
- Content: 草图表达模块位置、流程关系、并行和闭环；语音表达节点名称、因果关系、设计意图和补充说明；二者单独使用都不完整。

#### Slide 03 - 任务定义：Speech-Guided Sketch-to-Knowledge-Graph

- Layout: Definition block with input/output schema.
- Core message: 目标不是生成一张图片，而是恢复结构化知识图 `G_hat = (V, E)`。
- Content: 输入为手绘草图 `S` 与同步语音 `U`；输出节点包含标签、语义类型、解释、置信度；输出边包含方向、关系类型、关系标签、置信度。

#### Slide 04 - 模态互补性：草图给结构，语音给语义

- Layout: Symmetric contrast, center conclusion.
- Core message: 语音和草图分别覆盖对方最薄弱的信息维度。
- Content: 草图优势是二维布局和关系形态，缺陷是标签和方向不稳定；语音优势是语义、顺序和意图，缺陷是缺少布局；核心结论是用语音锚点补全草图缺失。

#### Slide 05 - 相关工作与研究空白

- Layout: Three-column research map plus bottom gap statement.
- Core message: 现有研究尚未充分建模“语音 + 草图 + 用户修改成本”的联合结构恢复问题。
- Content: Sketch-to-Diagram 主要依赖视觉；Image-to-Code 强调可编辑输出但输入静态；Diffusion/SB 提供图变换启发但很少接入真实交互输入。空白包括语音结构约束、联合建模、面向修改成本的图编辑。

### Part 2: MMSB-Graph Method

#### Slide 06 - 方法总览：MMSB-Graph 图编辑桥框架

- Layout: Horizontal pipeline with 5 stages.
- Visualization: pipeline_with_stages.
- Core message: MMSB-Graph 不直接一步生成最终图，而是通过受约束的图编辑路径恢复结构。
- Content: 草图观测和语音转写先构造条件图，再形成融合候选图，最后通过图编辑桥得到规范知识图和可编辑渲染。

#### Slide 07 - 三种中间图表示：`Gs`、`Gu`、`Gf`

- Layout: Three vertical pillars with a convergence arrow.
- Core message: 中间图把不同模态的不完整信息显式拆开，便于诊断和融合。
- Content: `Gs` 来自草图，保留空间结构但语义弱；`Gu` 来自语音，语义强但无布局；`Gf` 合并二者，是桥过程的初始候选图。

#### Slide 08 - 图编辑桥：逐步恢复而非一步生成

- Layout: Process flow with operation chips.
- Visualization: process_flow.
- Core message: 图编辑桥使结构恢复过程可解释、可追踪、可诊断。
- Content: 允许插入节点、删除节点、插入边、删除边、修正边方向；相比一步生成，编辑路径能定位错误来源并估计修改负担。

#### Slide 09 - 代价函数与路径能量

- Layout: Formula panel plus interpretation bullets.
- Core message: 代价函数衡量每一步编辑，路径能量衡量整个恢复过程是否自然。
- Content: 单步代价由结构变化、语义距离、方向惩罚、布局保持和语音覆盖组成；路径能量可理解为平均编辑强度，能量越高表示越依赖强行修正。

### Part 3: Dataset, Experiments, and System

#### Slide 10 - 数据集与评测协议

- Layout: Dataset card plus metric grid.
- Core message: 24 个知识草图样例支撑节点、边、路径和用户修改成本的多维评测。
- Content: 样例覆盖线性流程、分支结构、反馈闭环、模型架构图和实验流程图；每例包含草图、语音、转写、标准节点边、语音锚点、草图区域坐标和难度标签。指标包括 Node F1、Edge F1、Direction Accuracy、Normalized GED、Speech Coverage、Layout Preservation、Edit Cost、Path Energy。

#### Slide 11 - 实验设置：五类对比方法

- Layout: Vertical list with method tags.
- Visualization: vertical_list.
- Core message: 对比设置逐步增加模态与编辑能力，用来定位每一部分的贡献。
- Content: 草图单模态、语音单模态、早期融合、贪心修复、MMSB-Graph。当前实验是合成条件图的可控验证，用于验证任务定义、评测链路和图编辑过程可计算性。

#### Slide 12 - 实验结果与解释

- Layout: Top result table, bottom diagnostic figure strip.
- Visualization: basic_table.
- Core message: MMSB-Graph 在可控设定下达到最优结构一致性，同时路径能量提供额外诊断。
- Content: 草图单模态边 F1 为 0.387，语音单模态边 F1 提升到 0.564，早期融合节点提升但边错误仍存在，贪心修复有效但有限，MMSB-Graph 的 Node/Edge F1 为 1.000、Normalized GED 为 0。
- Image: `mmsb_diagnostics.png`.

#### Slide 13 - 工程系统与科研闭环

- Layout: End-to-end system loop.
- Core message: 系统实现了从交互输入到可编辑输出再到自动评测的闭环。
- Content: 支持草图输入、语音录入、文本补充、自动转写、Mermaid/JSON/SVG 生成、终稿图生成、语音讲解 WebM；评测系统自动对齐预测图和标准图，输出结构化指标。

#### Slide 14 - 贡献总结与一句话结论

- Layout: Three contribution blocks plus closing sentence.
- Core message: 项目贡献覆盖任务层、方法层和系统层。
- Content: 任务层提出语音引导的知识草图结构化；方法层提出 MMSB-Graph 图编辑桥；系统层构建交互输入、图结构、可编辑输出和可评测系统闭环。一句话总结：本项目将“语音 + 草图”的自然表达过程抽象为多模态知识结构恢复问题，并用图编辑桥实现从不完整表达到可编辑知识图的可解释重建。

---

## X. Speaker Notes Requirements

- Duration: 8-12 minutes.
- Notes style: formal but conversational Chinese.
- Filename: match SVG names, e.g. `01_title.md`.
- `notes/total.md` uses slide headings; split files must not contain heading lines.

---

## XI. Technical Constraints Reminder

- Every SVG uses viewBox `0 0 1280 720`.
- Text wrapping uses `<tspan>`; `<foreignObject>` is forbidden.
- Use `fill-opacity` / `stroke-opacity`; `rgba()` is forbidden.
- Forbidden: `<style>`, `class`, `textPath`, `animate*`, `script`, `<iframe>`, `<g opacity>`.
- Icons must use only `tabler-outline` placeholders listed in Section VI.
- Images must reference files listed in Section VIII.
- Chinese text stays as raw UTF-8 characters. XML-reserved characters must be escaped.
