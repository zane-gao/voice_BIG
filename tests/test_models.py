import pytest
from pydantic import ValidationError

from sketchvoice.models import GraphEdge, GraphNode, MethodGraph


def test_node_rejects_empty_label() -> None:
    with pytest.raises(ValidationError):
        GraphNode(id="a", label=" ")


def test_method_graph_accepts_basic_schema() -> None:
    graph = MethodGraph(
        title="好图",
        summary="摘要",
        nodes=[GraphNode(id="a", label="A"), GraphNode(id="b", label="B")],
        edges=[GraphEdge(source="a", target="b", label="到达")],
        confidence=0.9,
    )
    assert graph.nodes[0].label == "A"
    assert graph.edges[0].label == "到达"
