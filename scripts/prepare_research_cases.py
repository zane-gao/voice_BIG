from __future__ import annotations

import argparse
import json
import math
import wave
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from sketchvoice.mermaid import graph_to_mermaid
from sketchvoice.models import GraphEdge, GraphNode, MethodGraph


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "data" / "research_cases"
DEFAULT_MANIFEST = ROOT / "data" / "research_samples.json"


def case(
    case_id: str,
    topic: str,
    difficulty: str,
    transcript: str,
    nodes: list[str],
    edges: list[tuple[str, str]],
) -> dict[str, Any]:
    return {
        "id": case_id,
        "topic": topic,
        "difficulty": difficulty,
        "transcript": transcript,
        "nodes": nodes,
        "edges": edges,
    }


CASES: list[dict[str, Any]] = [
    case(
        "linear_pipeline",
        "线性实验流程",
        "intro",
        "输入数据经过预处理，进入深度学习模型，最后得到分类结果。",
        ["输入数据", "预处理", "深度学习模型", "分类结果"],
        [("输入数据", "预处理"), ("预处理", "深度学习模型"), ("深度学习模型", "分类结果")],
    ),
    case(
        "multimodal_fusion",
        "语音草图多模态融合",
        "intro",
        "语音描述经过 ASR 转写，手绘草图经过结构识别，两路信息进入语义融合模块，生成 Mermaid 方法图。",
        ["语音描述", "ASR转写", "手绘草图", "结构识别", "语义融合", "Mermaid方法图"],
        [("语音描述", "ASR转写"), ("手绘草图", "结构识别"), ("ASR转写", "语义融合"), ("结构识别", "语义融合"), ("语义融合", "Mermaid方法图")],
    ),
    case(
        "evaluation_loop",
        "方法图评测闭环",
        "intro",
        "方法图先由用户检查，再计算结构还原度、生成耗时和主观评分，最后进入反馈迭代。",
        ["方法图", "用户检查", "结构还原度", "生成耗时", "主观评分", "反馈迭代"],
        [("方法图", "用户检查"), ("用户检查", "结构还原度"), ("用户检查", "生成耗时"), ("用户检查", "主观评分"), ("主观评分", "反馈迭代")],
    ),
    case(
        "cnn_explainer",
        "卷积神经网络讲解",
        "intro",
        "输入图像先经过卷积核得到特征图，特征图经过 ReLU 和池化，再进入多层卷积、Flatten、全连接和 Softmax分类。",
        ["输入图像", "卷积核", "特征图", "ReLU", "池化", "多层卷积", "Flatten", "全连接", "Softmax分类"],
        [("输入图像", "卷积核"), ("卷积核", "特征图"), ("特征图", "ReLU"), ("ReLU", "池化"), ("池化", "多层卷积"), ("多层卷积", "Flatten"), ("Flatten", "全连接"), ("全连接", "Softmax分类")],
    ),
    case(
        "diffusion_roadmap",
        "扩散技术发展路线",
        "intermediate",
        "DDPM 发展到 DDIM，Classifier-Free Guidance 带来文本条件控制，Latent Diffusion 推动 Stable Diffusion，之后出现 ControlNet、DiT 和 Consistency Models。",
        ["DDPM", "DDIM", "Classifier-Free Guidance", "文本条件控制", "Latent Diffusion", "Stable Diffusion", "ControlNet", "DiT", "Consistency Models"],
        [("DDPM", "DDIM"), ("DDIM", "Classifier-Free Guidance"), ("Classifier-Free Guidance", "文本条件控制"), ("Classifier-Free Guidance", "Latent Diffusion"), ("Latent Diffusion", "Stable Diffusion"), ("Stable Diffusion", "ControlNet"), ("Stable Diffusion", "DiT"), ("DiT", "Consistency Models")],
    ),
    case(
        "video_generation_timeline",
        "视频生成模型脉络",
        "advanced",
        "早期GAN/RNN视频依赖帧预测，后来 Video Diffusion Models 连接 Imagen Video、Phenaki 和 VideoLDM，时空Transformer 进一步支持 Lumiere、Sora 和时序一致性评测。",
        ["早期GAN/RNN视频", "帧预测", "Video Diffusion Models", "Imagen Video", "Phenaki", "VideoLDM", "时空Transformer", "Lumiere", "Sora", "时序一致性"],
        [("早期GAN/RNN视频", "帧预测"), ("帧预测", "Video Diffusion Models"), ("Video Diffusion Models", "Imagen Video"), ("Video Diffusion Models", "Phenaki"), ("Video Diffusion Models", "VideoLDM"), ("VideoLDM", "时空Transformer"), ("时空Transformer", "Lumiere"), ("时空Transformer", "Sora"), ("Sora", "时序一致性")],
    ),
    case(
        "rag_pipeline",
        "检索增强生成流程",
        "intermediate",
        "用户问题进入查询改写，检索器召回文档，重排序器筛选证据，提示构造后交给生成模型，最终输出答案并做引用校验。",
        ["用户问题", "查询改写", "检索器", "重排序器", "提示构造", "生成模型", "答案输出", "引用校验"],
        [("用户问题", "查询改写"), ("查询改写", "检索器"), ("检索器", "重排序器"), ("重排序器", "提示构造"), ("提示构造", "生成模型"), ("生成模型", "答案输出"), ("答案输出", "引用校验")],
    ),
    case(
        "contrastive_learning",
        "对比学习训练框架",
        "intermediate",
        "原始样本经过两路数据增强得到两个视图，共享编码器提取表示，投影头输出向量，通过对比损失拉近正样本并推远负样本。",
        ["原始样本", "数据增强A", "数据增强B", "共享编码器", "投影头", "对比损失", "表示向量"],
        [("原始样本", "数据增强A"), ("原始样本", "数据增强B"), ("数据增强A", "共享编码器"), ("数据增强B", "共享编码器"), ("共享编码器", "投影头"), ("投影头", "表示向量"), ("表示向量", "对比损失")],
    ),
    case(
        "diffusion_training_sampling",
        "扩散训练与采样",
        "intermediate",
        "训练阶段从真实图像加入噪声得到噪声图像，噪声预测网络学习预测噪声；采样阶段从高斯噪声开始反复去噪得到生成图像。",
        ["真实图像", "加噪过程", "噪声图像", "噪声预测网络", "训练损失", "高斯噪声", "反向去噪", "生成图像"],
        [("真实图像", "加噪过程"), ("加噪过程", "噪声图像"), ("噪声图像", "噪声预测网络"), ("噪声预测网络", "训练损失"), ("高斯噪声", "反向去噪"), ("反向去噪", "生成图像"), ("噪声预测网络", "反向去噪")],
    ),
    case(
        "transformer_encoder",
        "Transformer 编码器",
        "intro",
        "输入序列先加入位置编码，经过多头自注意力和残差归一化，再进入前馈网络，最终输出上下文表示。",
        ["输入序列", "位置编码", "多头自注意力", "残差归一化", "前馈网络", "上下文表示"],
        [("输入序列", "位置编码"), ("位置编码", "多头自注意力"), ("多头自注意力", "残差归一化"), ("残差归一化", "前馈网络"), ("前馈网络", "上下文表示")],
    ),
    case(
        "graph_neural_network",
        "图神经网络消息传递",
        "intermediate",
        "节点特征和边关系进入消息传递层，邻居聚合后更新节点表示，多层传播得到图表示，再用于分类预测。",
        ["节点特征", "边关系", "消息传递层", "邻居聚合", "节点表示", "图表示", "分类预测"],
        [("节点特征", "消息传递层"), ("边关系", "消息传递层"), ("消息传递层", "邻居聚合"), ("邻居聚合", "节点表示"), ("节点表示", "图表示"), ("图表示", "分类预测")],
    ),
    case(
        "multi_agent_eval",
        "多智能体评测",
        "advanced",
        "任务描述分配给规划智能体，工具智能体执行检索和代码操作，审稿智能体检查结果，仲裁模块汇总评分并输出评测报告。",
        ["任务描述", "规划智能体", "工具智能体", "审稿智能体", "仲裁模块", "评测报告"],
        [("任务描述", "规划智能体"), ("规划智能体", "工具智能体"), ("工具智能体", "审稿智能体"), ("审稿智能体", "仲裁模块"), ("仲裁模块", "评测报告")],
    ),
    case(
        "reinforcement_learning_loop",
        "强化学习交互闭环",
        "intro",
        "智能体根据状态选择动作，环境返回奖励和下一状态，经验进入回放池，策略网络根据损失更新。",
        ["状态", "智能体", "动作", "环境", "奖励", "下一状态", "回放池", "策略网络"],
        [("状态", "智能体"), ("智能体", "动作"), ("动作", "环境"), ("环境", "奖励"), ("环境", "下一状态"), ("下一状态", "回放池"), ("回放池", "策略网络"), ("策略网络", "智能体")],
    ),
    case(
        "medical_image_segmentation",
        "医学图像分割",
        "intermediate",
        "医学图像经过预处理和数据增强进入 U-Net，解码器输出分割掩码，再用 Dice 系数和 Hausdorff 距离评估。",
        ["医学图像", "预处理", "数据增强", "U-Net", "分割掩码", "Dice系数", "Hausdorff距离"],
        [("医学图像", "预处理"), ("预处理", "数据增强"), ("数据增强", "U-Net"), ("U-Net", "分割掩码"), ("分割掩码", "Dice系数"), ("分割掩码", "Hausdorff距离")],
    ),
    case(
        "speech_emotion_recognition",
        "语音情感识别",
        "intermediate",
        "原始音频先做特征提取，得到谱图和韵律特征，声学编码器建模上下文，分类头输出情感标签。",
        ["原始音频", "特征提取", "谱图", "韵律特征", "声学编码器", "分类头", "情感标签"],
        [("原始音频", "特征提取"), ("特征提取", "谱图"), ("特征提取", "韵律特征"), ("谱图", "声学编码器"), ("韵律特征", "声学编码器"), ("声学编码器", "分类头"), ("分类头", "情感标签")],
    ),
    case(
        "anomaly_detection",
        "异常检测流程",
        "intro",
        "传感器数据进入滑动窗口，特征编码后由预测模型重建信号，重建误差超过阈值时触发异常告警。",
        ["传感器数据", "滑动窗口", "特征编码", "预测模型", "重建信号", "重建误差", "阈值判断", "异常告警"],
        [("传感器数据", "滑动窗口"), ("滑动窗口", "特征编码"), ("特征编码", "预测模型"), ("预测模型", "重建信号"), ("重建信号", "重建误差"), ("重建误差", "阈值判断"), ("阈值判断", "异常告警")],
    ),
    case(
        "federated_learning",
        "联邦学习训练",
        "advanced",
        "多个客户端在本地数据上训练本地模型，上传梯度到服务器，服务器聚合参数并下发全局模型，同时隐私预算监控泄露风险。",
        ["本地数据", "客户端训练", "本地模型", "梯度上传", "服务器聚合", "全局模型", "隐私预算"],
        [("本地数据", "客户端训练"), ("客户端训练", "本地模型"), ("本地模型", "梯度上传"), ("梯度上传", "服务器聚合"), ("服务器聚合", "全局模型"), ("全局模型", "客户端训练"), ("梯度上传", "隐私预算")],
    ),
    case(
        "active_learning",
        "主动学习采样",
        "intermediate",
        "未标注样本进入不确定性评估，查询策略选择最有价值样本，人工标注后加入训练集并更新模型。",
        ["未标注样本", "不确定性评估", "查询策略", "人工标注", "训练集", "模型更新"],
        [("未标注样本", "不确定性评估"), ("不确定性评估", "查询策略"), ("查询策略", "人工标注"), ("人工标注", "训练集"), ("训练集", "模型更新"), ("模型更新", "不确定性评估")],
    ),
    case(
        "human_feedback_alignment",
        "人类反馈对齐",
        "advanced",
        "候选回答经过人类偏好标注形成偏好数据，奖励模型学习打分，策略模型通过强化学习更新并接受安全评估。",
        ["候选回答", "偏好标注", "偏好数据", "奖励模型", "策略模型", "强化学习更新", "安全评估"],
        [("候选回答", "偏好标注"), ("偏好标注", "偏好数据"), ("偏好数据", "奖励模型"), ("奖励模型", "强化学习更新"), ("策略模型", "强化学习更新"), ("强化学习更新", "策略模型"), ("策略模型", "安全评估")],
    ),
    case(
        "scientific_figure_pipeline",
        "科研图生成流程",
        "intro",
        "草图和论文文本进入结构解析，图元素规划模块生成版式，渲染器输出矢量图，再由用户编辑和导出。",
        ["草图", "论文文本", "结构解析", "图元素规划", "渲染器", "矢量图", "用户编辑", "导出"],
        [("草图", "结构解析"), ("论文文本", "结构解析"), ("结构解析", "图元素规划"), ("图元素规划", "渲染器"), ("渲染器", "矢量图"), ("矢量图", "用户编辑"), ("用户编辑", "导出")],
    ),
    case(
        "ablation_study_design",
        "消融实验设计",
        "intro",
        "完整模型作为主实验，分别去掉语音反馈、草图保持和路径能量，比较节点F1、边F1和用户修改成本。",
        ["完整模型", "去掉语音反馈", "去掉草图保持", "去掉路径能量", "节点F1", "边F1", "用户修改成本"],
        [("完整模型", "节点F1"), ("完整模型", "边F1"), ("完整模型", "用户修改成本"), ("去掉语音反馈", "节点F1"), ("去掉草图保持", "边F1"), ("去掉路径能量", "用户修改成本")],
    ),
    case(
        "dataset_curation",
        "数据集构建流程",
        "intro",
        "原始论文图经过筛选和去重，标注节点、边和语音锚点，质检后形成训练集、验证集和测试集。",
        ["原始论文图", "筛选", "去重", "节点标注", "边标注", "语音锚点", "质检", "数据划分"],
        [("原始论文图", "筛选"), ("筛选", "去重"), ("去重", "节点标注"), ("去重", "边标注"), ("节点标注", "语音锚点"), ("边标注", "语音锚点"), ("语音锚点", "质检"), ("质检", "数据划分")],
    ),
    case(
        "multimodal_rag",
        "多模态 RAG",
        "advanced",
        "文本问题和参考图像分别进入文本检索和视觉检索，跨模态重排序融合证据，多模态生成器输出带图像引用的答案。",
        ["文本问题", "参考图像", "文本检索", "视觉检索", "跨模态重排序", "证据融合", "多模态生成器", "带引用答案"],
        [("文本问题", "文本检索"), ("参考图像", "视觉检索"), ("文本检索", "跨模态重排序"), ("视觉检索", "跨模态重排序"), ("跨模态重排序", "证据融合"), ("证据融合", "多模态生成器"), ("多模态生成器", "带引用答案")],
    ),
    case(
        "model_compression",
        "模型压缩流程",
        "intermediate",
        "教师模型产生软标签，学生模型通过蒸馏损失学习，同时剪枝和量化降低参数量，最后做延迟评测。",
        ["教师模型", "软标签", "学生模型", "蒸馏损失", "剪枝", "量化", "压缩模型", "延迟评测"],
        [("教师模型", "软标签"), ("软标签", "蒸馏损失"), ("学生模型", "蒸馏损失"), ("蒸馏损失", "压缩模型"), ("学生模型", "剪枝"), ("剪枝", "量化"), ("量化", "压缩模型"), ("压缩模型", "延迟评测")],
    ),
]


def load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
    ]:
        if Path(path).exists():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


def node_positions(nodes: list[str]) -> dict[str, tuple[int, int]]:
    width = 1180
    row_y = [190, 390, 590]
    positions: dict[str, tuple[int, int]] = {}
    columns = math.ceil(len(nodes) / len(row_y))
    x_gap = max(120, (width - 180) // max(1, columns - 1))
    for index, node in enumerate(nodes):
        row = index % len(row_y)
        col = index // len(row_y)
        positions[node] = (90 + col * x_gap, row_y[row])
    return positions


def wrap_label(label: str, max_chars: int = 11) -> str:
    if len(label) <= max_chars:
        return label
    return label[:max_chars] + "\n" + label[max_chars:]


def draw_graph_image(path: Path, nodes: list[str], edges: list[tuple[str, str]], *, sketch: bool) -> dict[str, dict[str, float]]:
    width, height = 1280, 760
    image = Image.new("RGB", (width, height), "#ffffff")
    draw = ImageDraw.Draw(image)
    font = load_font(25 if not sketch else 23)
    positions = node_positions(nodes)
    regions: dict[str, dict[str, float]] = {}
    box_w, box_h = (190, 74) if not sketch else (184, 68)
    line_color = "#334155" if not sketch else "#475569"

    for source, target in edges:
        if source not in positions or target not in positions:
            continue
        x1, y1 = positions[source]
        x2, y2 = positions[target]
        start = (x1 + box_w, y1 + box_h // 2)
        end = (x2, y2 + box_h // 2)
        if x2 < x1:
            start = (x1 + box_w // 2, y1 + box_h)
            end = (x2 + box_w // 2, y2)
        draw.line([start, end], fill=line_color, width=3)
        angle = math.atan2(end[1] - start[1], end[0] - start[0])
        arrow = [
            end,
            (end[0] - 13 * math.cos(angle - 0.45), end[1] - 13 * math.sin(angle - 0.45)),
            (end[0] - 13 * math.cos(angle + 0.45), end[1] - 13 * math.sin(angle + 0.45)),
        ]
        draw.polygon(arrow, fill=line_color)

    for index, node in enumerate(nodes):
        x, y = positions[node]
        jitter = (index % 3 - 1) * 4 if sketch else 0
        rect = [x + jitter, y - jitter, x + box_w + jitter, y + box_h - jitter]
        fill = "#f8fafc" if not sketch else "#ffffff"
        outline = "#0f766e" if not sketch else "#1f2937"
        draw.rounded_rectangle(rect, radius=12 if not sketch else 7, fill=fill, outline=outline, width=3)
        text = wrap_label(node)
        bbox = draw.multiline_textbbox((0, 0), text, font=font, spacing=2, align="center")
        tx = rect[0] + (box_w - (bbox[2] - bbox[0])) / 2
        ty = rect[1] + (box_h - (bbox[3] - bbox[1])) / 2 - 2
        draw.multiline_text((tx, ty), text, fill="#111827", font=font, spacing=2, align="center")
        regions[node] = {
            "x": round((rect[0] + rect[2]) / 2 / width, 4),
            "y": round((rect[1] + rect[3]) / 2 / height, 4),
            "w": round((rect[2] - rect[0]) / width, 4),
            "h": round((rect[3] - rect[1]) / height, 4),
        }

    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)
    return regions


def write_placeholder_wav(path: Path, seconds: float = 0.8, rate: int = 16_000) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frames = int(seconds * rate)
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        wav.writeframes(b"\x00\x00" * frames)


def graph_for_case(item: dict[str, Any]) -> MethodGraph:
    nodes = [
        GraphNode(id=f"n{index}", label=label, type="process")
        for index, label in enumerate(item["nodes"], start=1)
    ]
    label_to_id = {node.label: node.id for node in nodes}
    edges = [
        GraphEdge(source=label_to_id[source], target=label_to_id[target])
        for source, target in item["edges"]
    ]
    return MethodGraph(title=item["topic"], summary=item["transcript"], nodes=nodes, edges=edges)


def build_gold_payload(item: dict[str, Any], regions: dict[str, dict[str, float]]) -> dict[str, Any]:
    transcript = item["transcript"]
    node_spans: dict[str, list[int]] = {}
    for node in item["nodes"]:
        start = transcript.find(node)
        node_spans[node] = [start, start + len(node)] if start >= 0 else [-1, -1]
    return {
        "id": item["id"],
        "topic": item["topic"],
        "difficulty": item["difficulty"],
        "transcript": transcript,
        "gold_nodes": item["nodes"],
        "gold_edges": item["edges"],
        "node_spans": node_spans,
        "speech_anchors": [
            {"label": node, "order": index, "span": node_spans[node]}
            for index, node in enumerate(item["nodes"])
        ],
        "sketch_regions": regions,
        "layout": {label: {"x": region["x"], "y": region["y"]} for label, region in regions.items()},
        "warnings": ["speech.wav 为确定性占位音频；真实 ASR 评测时请替换为真人或 TTS 录音。"],
    }


def prepare_cases(output_dir: Path, manifest_path: Path) -> list[dict[str, Any]]:
    manifest: list[dict[str, Any]] = []
    for item in CASES:
        case_dir = output_dir / item["id"]
        sketch_path = case_dir / "sketch.png"
        render_path = case_dir / "gold_render.png"
        transcript_path = case_dir / "transcript.txt"
        audio_path = case_dir / "speech.wav"
        gold_path = case_dir / "gold.json"
        mermaid_path = case_dir / "gold_mermaid.mmd"

        regions = draw_graph_image(sketch_path, item["nodes"], item["edges"], sketch=True)
        draw_graph_image(render_path, item["nodes"], item["edges"], sketch=False)
        transcript_path.write_text(item["transcript"] + "\n", encoding="utf-8")
        write_placeholder_wav(audio_path)
        gold_path.write_text(json.dumps(build_gold_payload(item, regions), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        mermaid_path.write_text(graph_to_mermaid(graph_for_case(item)), encoding="utf-8")

        manifest.append(
            {
                "id": item["id"],
                "topic": item["topic"],
                "difficulty": item["difficulty"],
                "transcript_path": str(transcript_path.relative_to(ROOT)),
                "sketch_path": str(sketch_path.relative_to(ROOT)),
                "audio_path": str(audio_path.relative_to(ROOT)),
                "gold_path": str(gold_path.relative_to(ROOT)),
                "gold_mermaid_path": str(mermaid_path.relative_to(ROOT)),
                "gold_render_path": str(render_path.relative_to(ROOT)),
            }
        )
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="生成科研侧小样本数据集与 gold 标注。")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args()
    manifest = prepare_cases(args.output_dir, args.manifest)
    print(json.dumps({"samples": len(manifest), "manifest": str(args.manifest)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
