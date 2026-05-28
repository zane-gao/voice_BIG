from sketchvoice.mermaid import graph_to_mermaid, normalize_graph
from sketchvoice.models import GraphEdge, GraphNode, MethodGraph


def test_normalize_graph_removes_dangling_edges() -> None:
    graph = MethodGraph(
        title="测试图",
        nodes=[GraphNode(id="1 input", label="输入"), GraphNode(id="model", label="模型")],
        edges=[
            GraphEdge(source="1 input", target="model", label="进入"),
            GraphEdge(source="missing", target="model", label="错误"),
        ],
    )
    normalized = normalize_graph(graph)
    assert [node.id for node in normalized.nodes] == ["n_1_input", "model"]
    assert len(normalized.edges) == 1
    assert "悬空边" in normalized.warnings[-1]


def test_graph_to_mermaid_contains_classes_and_direction() -> None:
    graph = MethodGraph(
        title="测试图",
        nodes=[GraphNode(id="input", label='语音"输入', type="input"), GraphNode(id="out", label="输出", type="output")],
        edges=[GraphEdge(source="input", target="out", label="生成")],
    )
    mermaid = graph_to_mermaid(graph, direction="TD")
    assert mermaid.startswith("flowchart TD")
    assert 'input["语音\\"输入"]' in mermaid
    assert "input -->|生成| out" in mermaid
    assert "class out output;" in mermaid
