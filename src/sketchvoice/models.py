from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


NodeType = Literal["input", "process", "model", "fusion", "output", "metric", "decision", "note"]
EdgeType = Literal["data", "control", "semantic", "feedback", "evaluation", "other"]


class GraphNode(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(description="稳定节点 id，只能包含字母、数字和下划线")
    label: str = Field(min_length=1, max_length=80, description="节点显示名")
    type: NodeType = Field(default="process", description="节点类型")
    description: str = Field(default="", max_length=240, description="节点解释")
    confidence: float = Field(default=0.8, ge=0.0, le=1.0, description="节点识别置信度")

    @field_validator("id")
    @classmethod
    def validate_id(cls, value: str) -> str:
        clean = value.strip()
        if not clean:
            raise ValueError("节点 id 不能为空")
        return clean

    @field_validator("label")
    @classmethod
    def validate_label(cls, value: str) -> str:
        clean = value.strip()
        if not clean:
            raise ValueError("节点 label 不能为空")
        return clean


class GraphEdge(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: str = Field(description="起点节点 id")
    target: str = Field(description="终点节点 id")
    label: str = Field(default="", max_length=80, description="边标签")
    type: EdgeType = Field(default="data", description="边类型")
    confidence: float = Field(default=0.8, ge=0.0, le=1.0, description="边识别置信度")


class MethodGraph(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=120, description="方法图标题")
    summary: str = Field(default="", max_length=600, description="方法图摘要")
    nodes: list[GraphNode] = Field(min_length=1, max_length=24, description="图节点")
    edges: list[GraphEdge] = Field(default_factory=list, max_length=48, description="图边")
    warnings: list[str] = Field(default_factory=list, max_length=12, description="不确定项或修复说明")
    confidence: float = Field(default=0.75, ge=0.0, le=1.0, description="整体置信度")


class GenerateResponse(BaseModel):
    transcript: str
    graph: MethodGraph
    mermaid: str
    timings_ms: dict[str, int]
