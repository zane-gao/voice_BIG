from __future__ import annotations

from sketchvoice.models import GraphEdge, GraphNode, MethodGraph
from sketchvoice.research import (
    bridge_graph,
    edge_direction_accuracy,
    graph_edit_counts,
    normalized_graph_edit_distance,
    speech_coverage,
)


def make_graph(title: str, labels: list[str], edges: list[tuple[str, str]]) -> MethodGraph:
    nodes = [
        GraphNode(id=f"n{index}", label=label, type="process")
        for index, label in enumerate(labels, start=1)
    ]
    label_to_id = {node.label: node.id for node in nodes}
    return MethodGraph(
        title=title,
        summary="",
        nodes=nodes,
        edges=[
            GraphEdge(source=label_to_id[source], target=label_to_id[target])
            for source, target in edges
        ],
    )


def test_bridge_graph_reduces_graph_edit_distance_and_records_path_energy() -> None:
    source = make_graph(
        "草图粗解析图",
        ["输入图像", "卷积核", "分类概率"],
        [("卷积核", "输入图像"), ("输入图像", "分类概率")],
    )
    target = make_graph(
        "标准方法图",
        ["输入图像", "卷积核", "特征图", "分类概率"],
        [("输入图像", "卷积核"), ("卷积核", "特征图"), ("特征图", "分类概率")],
    )

    result = bridge_graph(source, target, transcript="输入图像经过卷积核得到特征图，最后输出分类概率。")

    assert normalized_graph_edit_distance(source, target) > 0
    assert normalized_graph_edit_distance(result.final_graph, target) == 0
    assert len(result.path) >= 3
    assert result.path_energy > 0
    assert result.edit_counts.node_insertions == 1
    assert result.edit_counts.edge_deletions == 2
    assert result.edit_counts.edge_insertions == 3


def test_research_metrics_measure_speech_coverage_and_edge_direction() -> None:
    predicted = make_graph(
        "预测图",
        ["语音描述", "ASR转写", "语义融合"],
        [("语音描述", "ASR转写"), ("语义融合", "ASR转写")],
    )
    gold = make_graph(
        "标准图",
        ["语音描述", "ASR转写", "结构识别", "语义融合"],
        [("语音描述", "ASR转写"), ("ASR转写", "语义融合")],
    )

    counts = graph_edit_counts(predicted, gold)

    assert counts.node_insertions == 1
    assert counts.edge_insertions == 1
    assert counts.edge_deletions == 1
    assert edge_direction_accuracy(predicted, gold) == 0.5
    assert speech_coverage("语音描述经过 ASR 转写后进入语义融合。", gold) == 0.75
