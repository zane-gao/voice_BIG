# 科研侧方法说明：MMSB-Graph

## 研究定位

当前科研侧不再把项目只写成 Web MVP，而是写成“语音引导的手绘科研方法图结构化”方法原型。核心方法为 MMSB-Graph：把草图粗解析图、语音语义图和早期融合图放到同一个 `MethodGraph` 状态空间中，用离散图编辑桥近似多模态薛定谔桥。

## 关键实现

- `src/sketchvoice/research.py`：图编辑统计、normalized GED、语音覆盖率、草图保持率、人工修改成本和 `bridge_graph`。
- `scripts/prepare_research_cases.py`：生成 24 个科研小样本 case，包括草图、占位音频、transcript、gold 标注、gold Mermaid 和标准渲染图。
- `scripts/evaluate_research_cases.py`：运行合成条件图 sanity check，比较 sketch-only、speech-only、early-fusion、greedy repair 和 MMSB-Graph。
- `docs/research_eval_results.json`：当前 24 个样例的完整评测输出。

## 重要口径

- 当前 `speech.wav` 是确定性占位音频，不是可发表的真实 ASR 数据。
- 当前 sanity check 不调用外部 VLM/ASR，使用从 gold graph 合成的条件图，因此只验证指标链路和离散图桥行为。
- `MMSB-Graph` 在 sanity check 中恢复到 gold graph，是受控 oracle 设定，不能表述为真实系统已经达到满分。
- 真实实验需要后续替换为模型输出：sketch-only、speech-only、speech+sketch、late rerank、MMSB-Graph。

## 当前主要数字

24 个合成条件图 sanity check 的均值：

- Sketch-only：Node F1 0.803，Edge F1 0.387，normalized GED 0.587，Edit Cost 9.29。
- Speech-only：Node F1 0.890，Edge F1 0.564，normalized GED 0.391，Edit Cost 6.19。
- Early fusion：Node F1 0.929，Edge F1 0.577，normalized GED 0.391，Edit Cost 5.94。
- Greedy repair：Node F1 1.000，Edge F1 0.842，normalized GED 0.129，Edit Cost 1.79。
- MMSB-Graph：Node F1 1.000，Edge F1 1.000，normalized GED 0.000，Edit Cost 0.00，平均 bridge steps 5.46，path energy 1.21。
