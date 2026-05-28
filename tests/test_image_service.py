import asyncio
import base64

from sketchvoice.config import Settings
from sketchvoice.image_service import ImageRenderService, build_image_prompt


def test_build_image_prompt_prefers_graph_json() -> None:
    prompt = build_image_prompt(
        mode="draft",
        transcript="这段文本应作为备选。",
        mermaid="flowchart LR\nA-->B",
        graph_json='{"nodes":[{"label":"语音输入"},{"label":"草图解析"}],"edges":[{"source":"a","target":"b"}]}',
        style="paper",
    )
    assert "快速低清草稿图" in prompt
    assert "语音输入" in prompt
    assert "草图解析" in prompt


def test_mock_draft_image_returns_valid_base64() -> None:
    service = ImageRenderService(Settings(sketchvoice_mock=True))
    result = asyncio.run(service.render(
        mode="draft",
        sketch_bytes=None,
        sketch_content_type=None,
        transcript="语音和草图生成方法图。",
        mermaid="",
        graph_json="",
        style="paper",
    ))
    assert result.mode == "draft"
    assert result.provider == "doubao-mock"
    assert result.mime_type == "image/jpeg"
    assert base64.b64decode(result.image_b64)


def test_mock_final_image_returns_valid_base64() -> None:
    service = ImageRenderService(Settings(sketchvoice_mock=True))
    result = asyncio.run(service.render(
        mode="final",
        sketch_bytes=None,
        sketch_content_type=None,
        transcript="语音和草图生成方法图。",
        mermaid="",
        graph_json="",
        style="nature",
    ))
    assert result.mode == "final"
    assert result.provider == "openai-mock"
    assert result.mime_type == "image/png"
    assert base64.b64decode(result.image_b64)
