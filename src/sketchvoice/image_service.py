from __future__ import annotations

import base64
import hashlib
import json
import math
import re
import time
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Literal

import httpx
from openai import OpenAI
from PIL import Image, ImageDraw, ImageFont
from pydantic import BaseModel, Field

from .config import Settings
from .provider_errors import describe_provider_error

ImageMode = Literal["draft", "final"]


@dataclass(frozen=True)
class RenderNode:
    id: str
    label: str
    type: str = "process"


@dataclass(frozen=True)
class RenderEdge:
    source: str
    target: str
    label: str = ""


@dataclass(frozen=True)
class RenderGraph:
    title: str
    nodes: list[RenderNode]
    edges: list[RenderEdge]


class ImageRenderResponse(BaseModel):
    mode: ImageMode
    provider: str
    model: str
    image_b64: str
    mime_type: str
    prompt: str
    timings_ms: dict[str, int]
    cached: bool = False
    warnings: list[str] = Field(default_factory=list)


class ImageRenderService:
    """服务端图像生成代理，避免把豆包/OpenAI 密钥泄露到前端。"""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings()
        image_api_key = self.settings.openai_image_key
        self.openai_client = (
            OpenAI(api_key=image_api_key, base_url=self.settings.openai_image_client_base_url)
            if image_api_key
            else None
        )
        self._cache: dict[str, ImageRenderResponse] = {}

    async def render(
        self,
        *,
        mode: ImageMode,
        sketch_bytes: bytes | None,
        sketch_content_type: str | None,
        transcript: str,
        mermaid: str,
        graph_json: str,
        style: str,
    ) -> ImageRenderResponse:
        prompt = build_image_prompt(
            mode=mode,
            transcript=transcript,
            mermaid=mermaid,
            graph_json=graph_json,
            style=style,
        )
        cache_key = self._cache_key(mode, prompt, sketch_bytes)
        if cache_key in self._cache:
            cached = self._cache[cache_key].model_copy(update={"cached": True})
            return cached

        if mode == "draft":
            result = await self.render_draft(
                prompt,
                sketch_bytes,
                sketch_content_type,
                graph_json=graph_json,
                mermaid=mermaid,
                transcript=transcript,
            )
        else:
            result = await self.render_final(
                prompt,
                sketch_bytes,
                sketch_content_type,
                graph_json=graph_json,
                mermaid=mermaid,
                transcript=transcript,
            )
        self._cache[cache_key] = result
        return result

    async def render_draft(
        self,
        prompt: str,
        sketch_bytes: bytes | None,
        sketch_content_type: str | None,
        *,
        graph_json: str,
        mermaid: str,
        transcript: str,
    ) -> ImageRenderResponse:
        start = time.perf_counter()
        model = self.settings.doubao_draft_image_model
        if self.settings.image_mock or not self.settings.ark_api_key:
            return self._mock_response(
                "draft",
                "doubao-mock",
                model,
                prompt,
                start,
                ["豆包草稿图运行在 mock 模式。"],
                graph_json=graph_json,
                mermaid=mermaid,
                transcript=transcript,
            )

        payload: dict[str, object] = {
            "model": model,
            "prompt": prompt,
            "response_format": "b64_json",
            "output_format": "jpeg",
            "watermark": False,
            "size": self.settings.doubao_draft_size,
            "sequential_image_generation": "disabled",
        }
        image_data = image_data_url(sketch_bytes, sketch_content_type)
        if image_data:
            payload["image"] = image_data

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.settings.ark_image_base_url.rstrip('/')}/images/generations",
                    headers={"Authorization": f"Bearer {self.settings.ark_api_key}"},
                    json=payload,
                )
                response.raise_for_status()
                body = response.json()
            image_b64 = extract_b64_image(body)
            return ImageRenderResponse(
                mode="draft",
                provider="doubao",
                model=model,
                image_b64=image_b64,
                mime_type="image/jpeg",
                prompt=prompt,
                timings_ms={"total": int((time.perf_counter() - start) * 1000)},
                cached=False,
                warnings=[],
            )
        except Exception as exc:
            if self.settings.image_fallback_to_mock:
                return self._mock_response(
                    "draft",
                    "doubao-mock",
                    model,
                    prompt,
                    start,
                    [f"豆包草稿图生成失败，已回退 mock：{describe_image_error(exc)}"],
                    graph_json=graph_json,
                    mermaid=mermaid,
                    transcript=transcript,
                )
            raise

    async def render_final(
        self,
        prompt: str,
        sketch_bytes: bytes | None,
        sketch_content_type: str | None,
        *,
        graph_json: str,
        mermaid: str,
        transcript: str,
    ) -> ImageRenderResponse:
        start = time.perf_counter()
        model = self.settings.openai_final_image_model
        if self.settings.image_mock or not self.openai_client:
            return self._mock_response(
                "final",
                "openai-mock",
                model,
                prompt,
                start,
                ["OpenAI 终稿图运行在 mock 模式。"],
                graph_json=graph_json,
                mermaid=mermaid,
                transcript=transcript,
            )

        try:
            result = self.openai_client.images.generate(
                model=model,
                prompt=prompt,
                response_format="b64_json",
                output_format="png",
                quality="high",
                size="1536x1024",
            )
            image_b64 = result.data[0].b64_json if result.data and result.data[0].b64_json else ""
            if not image_b64:
                raise ValueError("OpenAI 未返回 b64_json 图像")
            return ImageRenderResponse(
                mode="final",
                provider="openai",
                model=model,
                image_b64=image_b64,
                mime_type="image/png",
                prompt=prompt,
                timings_ms={"total": int((time.perf_counter() - start) * 1000)},
                cached=False,
                warnings=[],
            )
        except Exception as exc:
            if self.settings.image_fallback_to_mock:
                return self._mock_response(
                    "final",
                    "openai-mock",
                    model,
                    prompt,
                    start,
                    [f"OpenAI 终稿图生成失败，已回退 mock：{describe_image_error(exc)}"],
                    graph_json=graph_json,
                    mermaid=mermaid,
                    transcript=transcript,
                )
            raise

    def _cache_key(self, mode: ImageMode, prompt: str, sketch_bytes: bytes | None) -> str:
        sketch_hash = hashlib.sha256(sketch_bytes or b"").hexdigest()
        return hashlib.sha256(f"{mode}\n{prompt}\n{sketch_hash}".encode("utf-8")).hexdigest()

    def _mock_response(
        self,
        mode: ImageMode,
        provider: str,
        model: str,
        prompt: str,
        start: float,
        warnings: list[str],
        *,
        graph_json: str,
        mermaid: str,
        transcript: str,
    ) -> ImageRenderResponse:
        image_b64, mime_type = make_mock_image(
            mode=mode,
            prompt=prompt,
            graph_json=graph_json,
            mermaid=mermaid,
            transcript=transcript,
        )
        return ImageRenderResponse(
            mode=mode,
            provider=provider,
            model=model,
            image_b64=image_b64,
            mime_type=mime_type,
            prompt=prompt,
            timings_ms={"total": int((time.perf_counter() - start) * 1000)},
            cached=False,
            warnings=warnings,
        )


def build_image_prompt(*, mode: ImageMode, transcript: str, mermaid: str, graph_json: str, style: str) -> str:
    """构造稳定的生图提示词，明确要求模型重绘为论文级知识信息图。"""

    style_text = {
        "paper": "论文白底方法图，出版级矢量信息图风格，细线条，模块框和箭头清晰",
        "slides": "PPT 扁平风知识信息图，高对比，适合课堂展示",
        "nature": "Nature/Science 风格科研信息图，克制配色，版式高级",
        "mono": "黑白线稿知识信息图，白底，适合论文草稿",
    }.get(style, "论文白底方法图，出版级矢量信息图风格，细线条，模块框和箭头清晰")
    mode_text = (
        "快速草稿图，用于预览论文级知识信息图的构图和模块关系。"
        if mode == "draft"
        else "高清终稿图，文字必须清晰，布局必须和 Mermaid/JSON 节点边一致；请从结构数据重新生成，不要做草图 image-edit 或局部修补。"
    )
    source = summarize_source(mermaid=mermaid, graph_json=graph_json, transcript=transcript)
    prompt = "\n".join(
        [
            "任务：你是论文图设计师，请把输入的草图、语音转写和结构化图数据重新设计成论文级知识信息图。",
            f"目标：{mode_text} 输出一张{style_text}，用于科研论文或学术汇报，而不是复刻原始手绘草图。",
            "输入优先级：1) 结构化 JSON 与 Mermaid 的节点、边、方向最重要；2) 语音转写用于补充语义和命名；3) 草图图像只作为粗略布局参考。",
            "严禁：不要照搬手绘线条、歪斜框、潦草笔迹、原始截图质感或画布空白；不要生成照片、3D、卡通插画、水印、装饰背景。",
            "文字约束：不要把本提示词、任务描述、输入优先级、结构依据或任何说明性长句写进图片；图中只允许出现方法图标题、节点标签和必要的短边标签。",
            "重绘要求：用干净的模块卡片、统一字号、标准箭头、清楚层级、少量强调色和充足留白表达知识流程；中文标签要短、准确、可读。",
            "版式要求：根据节点关系重新排版，必要时把凌乱草图整理为输入层、处理/模型层、融合/评估层、输出层；让读者一眼理解方法逻辑。",
            "研究语义：该项目是 MMSB-Graph，核心是从草图空间/语音讲述空间迁移到标准、可编辑知识图；图像只是结构化知识图的论文级可视化后处理。",
            f"结构依据：{source}",
        ]
    )
    return prompt[:2000]


def summarize_source(*, mermaid: str, graph_json: str, transcript: str) -> str:
    if graph_json.strip():
        try:
            graph = json.loads(graph_json)
            nodes = [node.get("label", "") for node in graph.get("nodes", [])][:10]
            edges = [
                f"{edge.get('source', '')}->{edge.get('target', '')}"
                for edge in graph.get("edges", [])[:12]
            ]
            return f"节点：{'、'.join(filter(None, nodes))}；边：{'，'.join(edges)}"
        except json.JSONDecodeError:
            pass
    if mermaid.strip():
        return "Mermaid：" + compact(mermaid, 700)
    if transcript.strip():
        return "语音说明：" + compact(transcript, 700)
    return "语音、草图和方法图结构尚不完整，请生成通用的语音草图多模态方法流程图。"


def compact(value: str, limit: int) -> str:
    return " ".join(value.split())[:limit]


def describe_image_error(exc: Exception) -> str:
    if isinstance(exc, httpx.HTTPStatusError):
        status = exc.response.status_code
        detail = exc.response.text
        try:
            body = exc.response.json()
            error = body.get("error") if isinstance(body, dict) else None
            if isinstance(error, dict):
                code = error.get("code") or error.get("type") or ""
                message = error.get("message") or detail
                detail = f"{code}: {message}" if code else str(message)
        except Exception:
            pass
        return compact(f"HTTP {status} {detail}", 500)
    return describe_provider_error(exc)


def image_data_url(sketch_bytes: bytes | None, sketch_content_type: str | None) -> str | None:
    if not sketch_bytes:
        return None
    png_bytes = normalize_png(sketch_bytes)
    payload = base64.b64encode(png_bytes).decode("ascii")
    return f"data:image/png;base64,{payload}"


def normalize_png(image_bytes: bytes) -> bytes:
    try:
        image = Image.open(BytesIO(image_bytes)).convert("RGBA")
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        return buffer.getvalue()
    except Exception:
        return image_bytes


def extract_b64_image(body: dict[str, object]) -> str:
    data = body.get("data")
    if isinstance(data, list) and data:
        first = data[0]
        if isinstance(first, dict):
            for key in ("b64_json", "image", "content"):
                value = first.get(key)
                if isinstance(value, str) and value:
                    return strip_data_url(value)
    raise ValueError("图像接口未返回 b64_json")


def strip_data_url(value: str) -> str:
    if "," in value and value.startswith("data:"):
        return value.split(",", 1)[1]
    return value


FONT_CANDIDATES = [
    Path("C:/Windows/Fonts/msyh.ttc"),
    Path("C:/Windows/Fonts/simhei.ttf"),
    Path("C:/Windows/Fonts/simsun.ttc"),
    Path("C:/Windows/Fonts/Deng.ttf"),
    Path("/System/Library/Fonts/PingFang.ttc"),
    Path("/System/Library/Fonts/STHeiti Light.ttc"),
    Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
    Path("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"),
]


def load_ui_font(size: int) -> ImageFont.ImageFont:
    for path in FONT_CANDIDATES:
        if not path.exists():
            continue
        try:
            return ImageFont.truetype(str(path), size)
        except Exception:
            continue
    return ImageFont.load_default()


def parse_render_graph(*, graph_json: str, mermaid: str, transcript: str) -> RenderGraph:
    return graph_from_json(graph_json) or graph_from_mermaid(mermaid) or fallback_render_graph(transcript)


def graph_from_json(graph_json: str) -> RenderGraph | None:
    if not graph_json.strip():
        return None
    try:
        raw = json.loads(graph_json)
    except json.JSONDecodeError:
        return None
    if not isinstance(raw, dict):
        return None

    nodes: list[RenderNode] = []
    seen: set[str] = set()
    for item in raw.get("nodes", [])[:12]:
        if not isinstance(item, dict):
            continue
        node_id = str(item.get("id") or f"n{len(nodes) + 1}").strip()
        label = str(item.get("label") or node_id).strip()
        if not node_id or not label or node_id in seen:
            continue
        seen.add(node_id)
        nodes.append(RenderNode(id=node_id, label=label[:24], type=str(item.get("type") or "process")))
    if not nodes:
        return None

    node_ids = {node.id for node in nodes}
    edges: list[RenderEdge] = []
    for item in raw.get("edges", [])[:18]:
        if not isinstance(item, dict):
            continue
        source = str(item.get("source") or "").strip()
        target = str(item.get("target") or "").strip()
        if source in node_ids and target in node_ids and source != target:
            edges.append(RenderEdge(source=source, target=target, label=str(item.get("label") or "").strip()[:18]))
    title = str(raw.get("title") or "结构化知识图").strip()[:36]
    return RenderGraph(title=title or "结构化知识图", nodes=nodes, edges=edges)


MERMAID_NODE_RE = re.compile(r'^\s*(?P<id>[A-Za-z0-9_]+)\s*\[\s*"?(?P<label>[^"\]]+)"?\s*\]')
MERMAID_EDGE_RE = re.compile(
    r"(?P<source>[A-Za-z0-9_]+)\s*[-.=]+(?:>\|(?P<label>[^|]+)\||>)?\s*(?P<target>[A-Za-z0-9_]+)"
)


def graph_from_mermaid(mermaid: str) -> RenderGraph | None:
    if not mermaid.strip():
        return None
    labels: dict[str, str] = {}
    edges: list[RenderEdge] = []
    for line in mermaid.splitlines():
        stripped = line.strip()
        node_match = MERMAID_NODE_RE.search(stripped)
        if node_match:
            labels[node_match.group("id")] = clean_mermaid_label(node_match.group("label"))
            continue

        match = MERMAID_EDGE_RE.search(stripped)
        if not match:
            continue
        source = match.group("source")
        target = match.group("target")
        labels.setdefault(source, source)
        labels.setdefault(target, target)
        if source != target:
            edges.append(RenderEdge(source=source, target=target, label=clean_mermaid_label(match.group("label") or "")))
    if not labels:
        return None
    nodes = [RenderNode(id=node_id, label=label[:24]) for node_id, label in list(labels.items())[:12]]
    node_ids = {node.id for node in nodes}
    filtered_edges = [edge for edge in edges if edge.source in node_ids and edge.target in node_ids][:18]
    return RenderGraph(title="结构化知识图", nodes=nodes, edges=filtered_edges)


def clean_mermaid_label(value: str) -> str:
    return re.sub(r"[`\"{}()]", "", value).strip() or "节点"


def fallback_render_graph(transcript: str) -> RenderGraph:
    if "卷积神经网络" in transcript or "卷积" in transcript:
        return RenderGraph(
            title="卷积神经网络知识图",
            nodes=[
                RenderNode("input", "输入图像", "input"),
                RenderNode("conv", "卷积层", "model"),
                RenderNode("feature", "特征图", "process"),
                RenderNode("pool", "池化", "process"),
                RenderNode("fc", "全连接", "model"),
                RenderNode("out", "分类结果", "output"),
            ],
            edges=[
                RenderEdge("input", "conv"),
                RenderEdge("conv", "feature"),
                RenderEdge("feature", "pool"),
                RenderEdge("pool", "fc"),
                RenderEdge("fc", "out"),
            ],
        )
    return RenderGraph(
        title="MMSB-Graph 知识草图结构化",
        nodes=[
            RenderNode("sketch", "草图观测", "input"),
            RenderNode("speech", "语音讲述", "input"),
            RenderNode("semantic", "语义锚点", "process"),
            RenderNode("fusion", "多模态候选图", "fusion"),
            RenderNode("bridge", "离散图编辑桥", "model"),
            RenderNode("graph", "标准知识图", "output"),
            RenderNode("render", "可编辑矢量渲染", "output"),
        ],
        edges=[
            RenderEdge("sketch", "fusion"),
            RenderEdge("speech", "semantic"),
            RenderEdge("semantic", "fusion"),
            RenderEdge("fusion", "bridge"),
            RenderEdge("bridge", "graph"),
            RenderEdge("graph", "render"),
        ],
    )


def make_mock_image(
    *,
    mode: ImageMode,
    prompt: str,
    graph_json: str = "",
    mermaid: str = "",
    transcript: str = "",
) -> tuple[str, str]:
    width, height = (960, 540) if mode == "draft" else (1280, 720)
    bg = (252, 253, 255)
    image = Image.new("RGB", (width, height), bg)
    draw = ImageDraw.Draw(image)
    graph = parse_render_graph(graph_json=graph_json, mermaid=mermaid, transcript=transcript)
    title = f"{graph.title} · {'草稿 Mock' if mode == 'draft' else '终稿 Mock'}"
    accent = (245, 158, 11) if mode == "draft" else (15, 118, 110)
    muted = (100, 116, 139)
    text = (17, 24, 39)
    font_title = load_ui_font(34)
    font_body = load_ui_font(20)
    font_small = load_ui_font(16)

    draw.rounded_rectangle((36, 36, width - 36, height - 36), radius=18, outline=(216, 226, 238), width=2, fill=(255, 255, 255))
    draw.text((64, 60), title, fill=text, font=font_title)
    draw.line((64, 112, width - 64, 112), fill=accent, width=4)

    positions = layout_nodes(graph.nodes, graph.edges, width=width, height=height)
    for edge in graph.edges:
        start = positions.get(edge.source)
        end = positions.get(edge.target)
        if start and end:
            draw_arrow(draw, start, end, fill=muted)

    for node in graph.nodes:
        x, y = positions[node.id]
        draw_node(draw, x, y, node.label, node.type, font=font_body, text_fill=text)

    footer = "Mock fallback：真实生图接口不可用；此图按结构化 JSON/Mermaid 渲染，保持知识图闭环可演示。"
    draw.text((64, height - 84), footer, fill=muted, font=font_small)
    buffer = BytesIO()
    fmt = "JPEG" if mode == "draft" else "PNG"
    image.save(buffer, format=fmt, quality=88)
    mime = "image/jpeg" if mode == "draft" else "image/png"
    return base64.b64encode(buffer.getvalue()).decode("ascii"), mime


def layout_nodes(nodes: list[RenderNode], edges: list[RenderEdge], *, width: int, height: int) -> dict[str, tuple[int, int]]:
    if not nodes:
        return {}
    left, right = 120, width - 260
    top, bottom = 170, height - 170
    layers = graph_layers(nodes, edges)
    if not layers:
        layers = [nodes]
    positions: dict[str, tuple[int, int]] = {}
    for col, layer in enumerate(layers):
        x = int(left + (right - left) * col / max(1, len(layers) - 1))
        for row, node in enumerate(layer):
            y = int(top + (bottom - top) * row / max(1, len(layer) - 1))
            if len(layer) == 1:
                y = (top + bottom) // 2
            positions[node.id] = (x, y)
    return positions


def graph_layers(nodes: list[RenderNode], edges: list[RenderEdge]) -> list[list[RenderNode]]:
    by_id = {node.id: node for node in nodes}
    depth = {node.id: 0 for node in nodes}
    for _ in range(len(nodes)):
        changed = False
        for edge in edges:
            if edge.source not in by_id or edge.target not in by_id:
                continue
            next_depth = min(depth[edge.source] + 1, len(nodes) - 1)
            if next_depth > depth[edge.target]:
                depth[edge.target] = next_depth
                changed = True
        if not changed:
            break
    buckets: dict[int, list[RenderNode]] = {}
    for node in nodes:
        buckets.setdefault(depth[node.id], []).append(node)
    return [buckets[key] for key in sorted(buckets)]


def node_colors(node_type: str) -> tuple[tuple[int, int, int], tuple[int, int, int]]:
    if node_type == "input":
        return (231, 245, 255), (37, 99, 235)
    if node_type == "output":
        return (220, 252, 231), (22, 101, 52)
    if node_type == "model":
        return (254, 243, 199), (180, 83, 9)
    if node_type == "fusion":
        return (204, 251, 241), (15, 118, 110)
    if node_type == "metric":
        return (237, 233, 254), (109, 40, 217)
    return (248, 250, 252), (100, 116, 139)


def draw_node(draw: ImageDraw.ImageDraw, x: int, y: int, label: str, node_type: str, *, font: ImageFont.ImageFont, text_fill: tuple[int, int, int]) -> None:
    fill, outline = node_colors(node_type)
    box_w, box_h = 188, 62
    draw.rounded_rectangle((x, y, x + box_w, y + box_h), radius=8, outline=outline, fill=fill, width=2)
    label_text = fit_label(label, max_chars=10)
    bbox = draw.multiline_textbbox((0, 0), label_text, font=font, spacing=4)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    draw.multiline_text((x + (box_w - text_w) / 2, y + (box_h - text_h) / 2 - 2), label_text, fill=text_fill, font=font, align="center", spacing=4)


def fit_label(label: str, *, max_chars: int) -> str:
    value = compact(label, 24)
    if len(value) <= max_chars:
        return value
    return "\n".join(value[index : index + max_chars] for index in range(0, len(value), max_chars))


def draw_arrow(draw: ImageDraw.ImageDraw, start: tuple[int, int], end: tuple[int, int], *, fill: tuple[int, int, int]) -> None:
    start_x, start_y = start[0] + 188, start[1] + 31
    end_x, end_y = end[0], end[1] + 31
    if end_x <= start_x:
        start_x, start_y = start[0] + 94, start[1] + 62
        end_x, end_y = end[0] + 94, end[1]
    draw.line((start_x, start_y, end_x, end_y), fill=fill, width=3)
    angle = math.atan2(end_y - start_y, end_x - start_x)
    size = 10
    left = (end_x - size * math.cos(angle - math.pi / 6), end_y - size * math.sin(angle - math.pi / 6))
    right = (end_x - size * math.cos(angle + math.pi / 6), end_y - size * math.sin(angle + math.pi / 6))
    draw.polygon([(end_x, end_y), left, right], fill=fill)
