from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

from sketchvoice.models import GraphEdge, GraphNode, MethodGraph
from sketchvoice.research import (
    bridge_graph,
    edge_direction_accuracy,
    edge_label_pairs,
    graph_edit_counts,
    label_set,
    manual_edit_cost,
    normalized_graph_edit_distance,
    sketch_preservation,
    speech_coverage,
)


def prf(predicted: set[Any], gold: set[Any]) -> dict[str, float]:
    hit = len(predicted & gold)
    precision = hit / len(predicted) if predicted else 0.0
    recall = hit / len(gold) if gold else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"precision": precision, "recall": recall, "f1": f1}


def graph_from_gold(payload: dict[str, Any]) -> MethodGraph:
    nodes = [
        GraphNode(id=f"n{index}", label=label, type="process")
        for index, label in enumerate(payload["gold_nodes"], start=1)
    ]
    label_to_id = {node.label: node.id for node in nodes}
    edges = [
        GraphEdge(source=label_to_id[source], target=label_to_id[target])
        for source, target in payload["gold_edges"]
        if source in label_to_id and target in label_to_id
    ]
    return MethodGraph(title=payload["topic"], summary=payload.get("transcript", ""), nodes=nodes, edges=edges)


def _subset_graph(gold: MethodGraph, keep_node_count: int, keep_edge_count: int, *, reverse_first_edge: bool = False) -> MethodGraph:
    nodes = gold.nodes[: max(1, keep_node_count)]
    valid_ids = {node.id for node in nodes}
    edges = [edge for edge in gold.edges if edge.source in valid_ids and edge.target in valid_ids][: max(0, keep_edge_count)]
    if reverse_first_edge and edges:
        first = edges[0]
        edges[0] = first.model_copy(update={"source": first.target, "target": first.source})
    return gold.model_copy(update={"nodes": nodes, "edges": edges})


def condition_graphs(gold: MethodGraph) -> dict[str, MethodGraph]:
    node_count = len(gold.nodes)
    edge_count = len(gold.edges)
    sketch_nodes = max(3, int(node_count * 0.72))
    speech_nodes = max(3, int(node_count * 0.86))
    fusion_nodes = max(4, int(node_count * 0.92))
    return {
        "sketch_only": _subset_graph(gold, sketch_nodes, max(1, int(edge_count * 0.55)), reverse_first_edge=True),
        "speech_only": _subset_graph(gold, speech_nodes, max(1, int(edge_count * 0.45))),
        "early_fusion": _subset_graph(gold, fusion_nodes, max(1, int(edge_count * 0.70)), reverse_first_edge=edge_count > 3),
        "greedy_repair": _subset_graph(gold, node_count, max(1, int(edge_count * 0.82))),
    }


def metrics_for_graph(predicted: MethodGraph, gold: MethodGraph, transcript: str, sketch_graph: MethodGraph, *, path_energy: float = 0.0, latency_ms: int = 0) -> dict[str, float]:
    node_scores = prf(label_set(predicted), label_set(gold))
    edge_scores = prf(edge_label_pairs(predicted), edge_label_pairs(gold))
    counts = graph_edit_counts(predicted, gold)
    return {
        "node_f1": round(node_scores["f1"], 4),
        "edge_f1": round(edge_scores["f1"], 4),
        "normalized_ged": round(normalized_graph_edit_distance(predicted, gold), 4),
        "label_accuracy": round(node_scores["recall"], 4),
        "edge_direction_accuracy": round(edge_direction_accuracy(predicted, gold), 4),
        "speech_coverage": round(speech_coverage(transcript, predicted), 4),
        "sketch_preservation": round(sketch_preservation(predicted, sketch_graph), 4),
        "manual_edit_cost": round(manual_edit_cost(predicted, gold), 4),
        "path_energy": round(path_energy, 4),
        "latency_ms": float(latency_ms),
        "node_insertions": float(counts.node_insertions),
        "node_deletions": float(counts.node_deletions),
        "edge_insertions": float(counts.edge_insertions),
        "edge_deletions": float(counts.edge_deletions),
    }


def evaluate_sample(sample: dict[str, Any]) -> dict[str, Any]:
    gold_payload = json.loads(Path(sample["gold_path"]).read_text(encoding="utf-8"))
    transcript = Path(sample["transcript_path"]).read_text(encoding="utf-8").strip()
    gold = graph_from_gold(gold_payload)
    baselines = condition_graphs(gold)
    sketch_graph = baselines["sketch_only"]
    metrics: dict[str, dict[str, float]] = {}

    for name, graph in baselines.items():
        metrics[name] = metrics_for_graph(graph, gold, transcript, sketch_graph)

    start = time.perf_counter()
    bridge = bridge_graph(baselines["early_fusion"], gold, transcript=transcript)
    latency_ms = int((time.perf_counter() - start) * 1000)
    metrics["mmsb_graph"] = metrics_for_graph(
        bridge.final_graph,
        gold,
        transcript,
        sketch_graph,
        path_energy=bridge.path_energy,
        latency_ms=latency_ms,
    )
    metrics["mmsb_graph"]["bridge_steps"] = float(max(0, len(bridge.path) - 1))

    return {
        "id": sample["id"],
        "topic": sample["topic"],
        "difficulty": sample["difficulty"],
        "metrics": metrics,
    }


def aggregate(results: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    totals: dict[str, dict[str, float]] = {}
    counts: dict[str, int] = {}
    for result in results:
        for name, metrics in result["metrics"].items():
            totals.setdefault(name, {})
            counts[name] = counts.get(name, 0) + 1
            for key, value in metrics.items():
                totals[name][key] = totals[name].get(key, 0.0) + float(value)
    return {
        name: {key: round(value / counts[name], 4) for key, value in metrics.items()}
        for name, metrics in totals.items()
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="运行科研侧 MMSB-Graph 小样本评测。")
    parser.add_argument("--samples", type=Path, default=Path("data/research_samples.json"))
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    samples = json.loads(args.samples.read_text(encoding="utf-8"))
    if args.limit:
        samples = samples[: args.limit]
    results = [evaluate_sample(sample) for sample in samples]
    payload = {
        "mode": "synthetic_condition_graphs",
        "note": "该评测不调用外部 VLM/ASR；用于验证 MMSB-Graph 指标和离散图桥 sanity check。",
        "sample_count": len(results),
        "aggregate": aggregate(results),
        "samples": results,
    }
    output = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output + "\n", encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
