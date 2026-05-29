from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher

from .models import GraphEdge, GraphNode, MethodGraph


@dataclass(frozen=True)
class GraphEditCounts:
    node_insertions: int = 0
    node_deletions: int = 0
    edge_insertions: int = 0
    edge_deletions: int = 0

    @property
    def total(self) -> int:
        return self.node_insertions + self.node_deletions + self.edge_insertions + self.edge_deletions


@dataclass(frozen=True)
class BridgeResult:
    final_graph: MethodGraph
    path: list[MethodGraph]
    edit_counts: GraphEditCounts
    path_energy: float


def normalize_label(value: str) -> str:
    return "".join(value.lower().split())


def label_similarity(left: str, right: str) -> float:
    if normalize_label(left) == normalize_label(right):
        return 1.0
    return SequenceMatcher(None, normalize_label(left), normalize_label(right)).ratio()


def label_set(graph: MethodGraph) -> set[str]:
    return {normalize_label(node.label) for node in graph.nodes}


def label_to_node(graph: MethodGraph) -> dict[str, GraphNode]:
    return {normalize_label(node.label): node for node in graph.nodes}


def edge_label_pairs(graph: MethodGraph) -> set[tuple[str, str]]:
    id_to_label = {node.id: normalize_label(node.label) for node in graph.nodes}
    return {
        (id_to_label.get(edge.source, normalize_label(edge.source)), id_to_label.get(edge.target, normalize_label(edge.target)))
        for edge in graph.edges
    }


def graph_edit_counts(predicted: MethodGraph, gold: MethodGraph) -> GraphEditCounts:
    pred_nodes = label_set(predicted)
    gold_nodes = label_set(gold)
    pred_edges = edge_label_pairs(predicted)
    gold_edges = edge_label_pairs(gold)
    return GraphEditCounts(
        node_insertions=len(gold_nodes - pred_nodes),
        node_deletions=len(pred_nodes - gold_nodes),
        edge_insertions=len(gold_edges - pred_edges),
        edge_deletions=len(pred_edges - gold_edges),
    )


def normalized_graph_edit_distance(predicted: MethodGraph, gold: MethodGraph) -> float:
    counts = graph_edit_counts(predicted, gold)
    denominator = max(1, len(label_set(gold)) + len(edge_label_pairs(gold)))
    return counts.total / denominator


def manual_edit_cost(predicted: MethodGraph, gold: MethodGraph) -> float:
    counts = graph_edit_counts(predicted, gold)
    # 节点错误通常比边错误更费人工修，给节点编辑更高权重。
    return (
        1.5 * (counts.node_insertions + counts.node_deletions)
        + counts.edge_insertions
        + counts.edge_deletions
    )


def edge_direction_accuracy(predicted: MethodGraph, gold: MethodGraph) -> float:
    pred_edges = edge_label_pairs(predicted)
    gold_edges = edge_label_pairs(gold)
    if not gold_edges:
        return 1.0
    correct = 0
    for source, target in gold_edges:
        if (source, target) in pred_edges:
            correct += 1
    return correct / len(gold_edges)


def speech_coverage(transcript: str, gold: MethodGraph) -> float:
    if not gold.nodes:
        return 1.0
    normalized_transcript = normalize_label(transcript)
    covered = 0
    for node in gold.nodes:
        label = normalize_label(node.label)
        if label and label in normalized_transcript:
            covered += 1
    return covered / len(gold.nodes)


def sketch_preservation(predicted: MethodGraph, sketch_graph: MethodGraph) -> float:
    sketch_nodes = label_set(sketch_graph)
    if not sketch_nodes:
        return 1.0
    return len(label_set(predicted) & sketch_nodes) / len(sketch_nodes)


def _graph_with_nodes(graph: MethodGraph, nodes: list[GraphNode]) -> MethodGraph:
    valid_ids = {node.id for node in nodes}
    edges = [edge for edge in graph.edges if edge.source in valid_ids and edge.target in valid_ids]
    return graph.model_copy(update={"nodes": nodes, "edges": edges})


def _append_node(graph: MethodGraph, node: GraphNode) -> MethodGraph:
    existing_ids = {item.id for item in graph.nodes}
    new_node = node
    if new_node.id in existing_ids:
        suffix = 2
        while f"{new_node.id}_{suffix}" in existing_ids:
            suffix += 1
        new_node = new_node.model_copy(update={"id": f"{new_node.id}_{suffix}"})
    return graph.model_copy(update={"nodes": [*graph.nodes, new_node]})


def _remove_node_by_label(graph: MethodGraph, label: str) -> MethodGraph:
    key = normalize_label(label)
    kept = [node for node in graph.nodes if normalize_label(node.label) != key]
    return _graph_with_nodes(graph, kept)


def _remove_edge_by_labels(graph: MethodGraph, source_label: str, target_label: str) -> MethodGraph:
    id_to_label = {node.id: normalize_label(node.label) for node in graph.nodes}
    source = normalize_label(source_label)
    target = normalize_label(target_label)
    edges = [
        edge
        for edge in graph.edges
        if (id_to_label.get(edge.source, edge.source), id_to_label.get(edge.target, edge.target)) != (source, target)
    ]
    return graph.model_copy(update={"edges": edges})


def _append_edge_by_labels(graph: MethodGraph, target_graph: MethodGraph, source_label: str, target_label: str) -> MethodGraph:
    current_label_to_id = {normalize_label(node.label): node.id for node in graph.nodes}
    target_id_to_label = {node.id: normalize_label(node.label) for node in target_graph.nodes}
    target_edges = {
        (target_id_to_label.get(edge.source, edge.source), target_id_to_label.get(edge.target, edge.target)): edge
        for edge in target_graph.edges
    }
    source = normalize_label(source_label)
    target = normalize_label(target_label)
    source_id = current_label_to_id.get(source)
    target_id = current_label_to_id.get(target)
    if not source_id or not target_id:
        return graph
    template = target_edges.get((source, target))
    edge = GraphEdge(
        source=source_id,
        target=target_id,
        label=template.label if template else "",
        type=template.type if template else "data",
        confidence=template.confidence if template else 0.8,
    )
    return graph.model_copy(update={"edges": [*graph.edges, edge]})


def _ordered_missing_nodes(source: MethodGraph, target: MethodGraph, transcript: str) -> list[GraphNode]:
    missing = [node for node in target.nodes if normalize_label(node.label) not in label_set(source)]
    normalized_transcript = normalize_label(transcript)

    def sort_key(node: GraphNode) -> tuple[int, str]:
        label = normalize_label(node.label)
        position = normalized_transcript.find(label)
        return (position if position >= 0 else 10**9, label)

    return sorted(missing, key=sort_key)


def bridge_graph(source: MethodGraph, target: MethodGraph, transcript: str = "") -> BridgeResult:
    """用确定性图编辑路径近似离散薛定谔桥，便于小样本可复现实验。

    这里不训练像素扩散模型，而是把语音反馈作为编辑顺序和约束信号，
    让草图粗图逐步迁移到目标方法图，并记录路径能量。
    """

    initial_counts = graph_edit_counts(source, target)
    current = source.model_copy(deep=True)
    path = [current]
    step_costs: list[float] = []

    for label in sorted(label_set(current) - label_set(target)):
        current = _remove_node_by_label(current, label)
        path.append(current)
        step_costs.append(1.5)

    for node in _ordered_missing_nodes(current, target, transcript):
        current = _append_node(current, node)
        path.append(current)
        step_costs.append(1.5)

    for source_label, target_label in sorted(edge_label_pairs(current) - edge_label_pairs(target)):
        current = _remove_edge_by_labels(current, source_label, target_label)
        path.append(current)
        step_costs.append(1.0)

    for source_label, target_label in sorted(edge_label_pairs(target) - edge_label_pairs(current)):
        current = _append_edge_by_labels(current, target, source_label, target_label)
        path.append(current)
        step_costs.append(1.0)

    energy = sum(cost * cost for cost in step_costs) / max(1, len(step_costs))
    final_graph = target.model_copy(deep=True) if normalized_graph_edit_distance(current, target) == 0 else current
    if path[-1] is not final_graph:
        path[-1] = final_graph
    return BridgeResult(final_graph=final_graph, path=path, edit_counts=initial_counts, path_energy=energy)
