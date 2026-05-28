from __future__ import annotations

import re
from collections import OrderedDict

from .models import GraphEdge, GraphNode, MethodGraph


_ID_RE = re.compile(r"[^a-zA-Z0-9_]+")


def sanitize_node_id(raw_id: str, index: int) -> str:
    """把模型输出的自由文本 id 规整为 Mermaid 可接受的稳定 id。"""

    value = _ID_RE.sub("_", raw_id.strip())
    value = value.strip("_")
    if not value:
        value = f"node_{index}"
    if value[0].isdigit():
        value = f"n_{value}"
    return value[:48]


def normalize_graph(graph: MethodGraph) -> MethodGraph:
    """去重节点并删除悬空边，让生成结果适合确定性渲染。"""

    id_map: dict[str, str] = {}
    nodes: "OrderedDict[str, GraphNode]" = OrderedDict()
    warnings = list(graph.warnings)

    for index, node in enumerate(graph.nodes, start=1):
        new_id = sanitize_node_id(node.id, index)
        if new_id in nodes:
            suffix = 2
            candidate = f"{new_id}_{suffix}"
            while candidate in nodes:
                suffix += 1
                candidate = f"{new_id}_{suffix}"
            warnings.append(f"节点 id 重复，已将 {node.id} 重命名为 {candidate}")
            new_id = candidate
        id_map[node.id] = new_id
        nodes[new_id] = node.model_copy(update={"id": new_id})

    valid_edges: list[GraphEdge] = []
    seen_edges: set[tuple[str, str, str]] = set()
    for edge in graph.edges:
        source = id_map.get(edge.source, sanitize_node_id(edge.source, 0))
        target = id_map.get(edge.target, sanitize_node_id(edge.target, 0))
        if source not in nodes or target not in nodes:
            warnings.append(f"已删除悬空边 {edge.source}->{edge.target}")
            continue
        edge_key = (source, target, edge.label)
        if edge_key in seen_edges:
            warnings.append(f"已删除重复边 {source}->{target}")
            continue
        seen_edges.add(edge_key)
        valid_edges.append(edge.model_copy(update={"source": source, "target": target}))

    return graph.model_copy(update={"nodes": list(nodes.values()), "edges": valid_edges, "warnings": warnings})


def _escape_label(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ")


def graph_to_mermaid(graph: MethodGraph, direction: str = "LR") -> str:
    """把规整后的方法图转换为 Mermaid flowchart。"""

    safe_direction = direction if direction in {"LR", "TD"} else "LR"
    graph = normalize_graph(graph)
    lines = [f"flowchart {safe_direction}"]
    for node in graph.nodes:
        lines.append(f'  {node.id}["{_escape_label(node.label)}"]')
    for edge in graph.edges:
        label = f'|{_escape_label(edge.label)}|' if edge.label else ""
        lines.append(f"  {edge.source} -->{label} {edge.target}")

    lines.extend(
        [
            "  classDef input fill:#e7f5ff,stroke:#228be6,color:#102a43;",
            "  classDef process fill:#f8fafc,stroke:#64748b,color:#111827;",
            "  classDef model fill:#fef3c7,stroke:#f59e0b,color:#442006;",
            "  classDef fusion fill:#ccfbf1,stroke:#14b8a6,color:#134e4a;",
            "  classDef output fill:#dcfce7,stroke:#22c55e,color:#14532d;",
            "  classDef metric fill:#fae8ff,stroke:#c026d3,color:#581c87;",
            "  classDef decision fill:#fee2e2,stroke:#ef4444,color:#7f1d1d;",
            "  classDef note fill:#f1f5f9,stroke:#94a3b8,color:#334155;",
        ]
    )
    for node in graph.nodes:
        lines.append(f"  class {node.id} {node.type};")
    return "\n".join(lines)
