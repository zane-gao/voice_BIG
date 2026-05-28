from __future__ import annotations

import base64
import hashlib
import json
import time
from io import BytesIO
from typing import Literal

import httpx
from openai import OpenAI
from PIL import Image, ImageDraw, ImageFont
from pydantic import BaseModel, Field

from .config import Settings

ImageMode = Literal["draft", "final"]


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
        self.openai_client = (
            OpenAI(api_key=self.settings.openai_api_key, base_url=self.settings.openai_base_url)
            if self.settings.openai_api_key
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
            result = await self.render_draft(prompt, sketch_bytes, sketch_content_type)
        else:
            result = await self.render_final(prompt, sketch_bytes, sketch_content_type)
        self._cache[cache_key] = result
        return result

    async def render_draft(
        self, prompt: str, sketch_bytes: bytes | None, sketch_content_type: str | None
    ) -> ImageRenderResponse:
        start = time.perf_counter()
        model = self.settings.doubao_draft_image_model
        if self.settings.image_mock or not self.settings.ark_api_key:
            return self._mock_response("draft", "doubao-mock", model, prompt, start, ["豆包草稿图运行在 mock 模式。"])

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
                    [f"豆包草稿图生成失败，已回退 mock：{type(exc).__name__}"],
                )
            raise

    async def render_final(
        self, prompt: str, sketch_bytes: bytes | None, sketch_content_type: str | None
    ) -> ImageRenderResponse:
        start = time.perf_counter()
        model = self.settings.openai_final_image_model
        if self.settings.image_mock or not self.openai_client:
            return self._mock_response("final", "openai-mock", model, prompt, start, ["OpenAI 终稿图运行在 mock 模式。"])

        try:
            if sketch_bytes:
                result = self.openai_client.images.edit(
                    model=model,
                    prompt=prompt,
                    image=("sketch.png", normalize_png(sketch_bytes), "image/png"),
                    response_format="b64_json",
                    output_format="png",
                    quality="high",
                    size="1536x1024",
                )
            else:
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
                    [f"OpenAI 终稿图生成失败，已回退 mock：{type(exc).__name__}"],
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
    ) -> ImageRenderResponse:
        image_b64, mime_type = make_mock_image(mode=mode, prompt=prompt)
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
    """构造短而稳定的图像提示词，优先使用结构化图信息。"""

    style_text = {
        "paper": "论文白底方法图，出版级，细线条，模块框和箭头清晰",
        "slides": "PPT 扁平风方法图，高对比，适合课堂展示",
        "nature": "Nature/Science 风格科研流程图，克制配色，版式高级",
        "mono": "黑白线稿方法图，白底，适合论文草稿",
    }.get(style, "论文白底方法图，出版级，细线条，模块框和箭头清晰")
    mode_text = (
        "快速低清草稿图，只做构图预览，保留主要模块布局。"
        if mode == "draft"
        else "高清终稿图，文字尽量清晰，布局必须和 Mermaid 节点边一致。"
    )
    source = summarize_source(mermaid=mermaid, graph_json=graph_json, transcript=transcript)
    prompt = (
        f"{mode_text} 生成一张{style_text}。"
        "白色背景，不要照片质感，不要复杂装饰，不要水印。"
        "用整齐模块、箭头、少量强调色表达科研流程。"
        f"结构依据：{source}"
    )
    return prompt[:1200]


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


def make_mock_image(*, mode: ImageMode, prompt: str) -> tuple[str, str]:
    width, height = (960, 540) if mode == "draft" else (1280, 720)
    bg = (252, 253, 255)
    image = Image.new("RGB", (width, height), bg)
    draw = ImageDraw.Draw(image)
    title = "豆包草稿图 Mock" if mode == "draft" else "OpenAI 终稿图 Mock"
    accent = (245, 158, 11) if mode == "draft" else (15, 118, 110)
    muted = (100, 116, 139)
    text = (17, 24, 39)
    try:
        font_title = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 34)
        font_body = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 20)
        font_small = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 16)
    except Exception:
        font_title = font_body = font_small = ImageFont.load_default()

    draw.rounded_rectangle((36, 36, width - 36, height - 36), radius=18, outline=(216, 226, 238), width=2, fill=(255, 255, 255))
    draw.text((64, 60), title, fill=text, font=font_title)
    draw.line((64, 112, width - 64, 112), fill=accent, width=4)
    boxes = [
        ("语音描述", 90, 190),
        ("草图结构", 90, 310),
        ("语义融合", width // 2 - 90, 250),
        ("论文方法图", width - 260, 250),
    ]
    for label, x, y in boxes:
        draw.rounded_rectangle((x, y, x + 170, y + 58), radius=10, outline=(148, 163, 184), fill=(248, 250, 252), width=2)
        draw.text((x + 22, y + 17), label, fill=text, font=font_body)
    draw.line((260, 219, width // 2 - 90, 270), fill=muted, width=3)
    draw.line((260, 339, width // 2 - 90, 308), fill=muted, width=3)
    draw.line((width // 2 + 80, 279, width - 260, 279), fill=muted, width=3)
    draw.text((64, height - 92), compact(prompt, 90), fill=muted, font=font_small)
    buffer = BytesIO()
    fmt = "JPEG" if mode == "draft" else "PNG"
    image.save(buffer, format=fmt, quality=88)
    mime = "image/jpeg" if mode == "draft" else "image/png"
    return base64.b64encode(buffer.getvalue()).decode("ascii"), mime
