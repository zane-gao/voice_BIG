from __future__ import annotations

import asyncio
import base64
from io import BytesIO

from PIL import Image

from sketchvoice.config import Settings
from sketchvoice.narration_service import NarrationService, build_fallback_segments, build_narration_script


def make_png_bytes() -> bytes:
    image = Image.new("RGB", (320, 180), "white")
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_build_fallback_segments_uses_graph_nodes() -> None:
    graph_json = '{"nodes":[{"label":"输入图像"},{"label":"卷积核"},{"label":"分类结果"}],"edges":[]}'
    segments = build_fallback_segments(graph_json=graph_json, transcript="")

    assert [segment.target_label for segment in segments] == ["输入图像", "卷积核", "分类结果"]
    assert all(0.0 <= segment.x <= 1.0 and 0.0 <= segment.y <= 1.0 for segment in segments)
    assert segments[0].x < segments[-1].x


def test_build_narration_script_contains_graph_labels() -> None:
    graph_json = '{"nodes":[{"label":"语音输入"},{"label":"结构化方法图"}],"edges":[]}'
    script = build_narration_script(graph_json=graph_json, mermaid="", transcript="")

    assert "语音输入" in script
    assert "结构化方法图" in script


def test_mock_narration_returns_audio_and_segments() -> None:
    service = NarrationService(Settings(sketchvoice_mock=True))
    result = asyncio.run(
        service.narrate(
            image_bytes=make_png_bytes(),
            image_content_type="image/png",
            graph_json='{"nodes":[{"label":"输入"},{"label":"模型"},{"label":"输出"}],"edges":[]}',
            mermaid="flowchart LR\nA-->B",
            transcript="输入经过模型得到输出。",
            provider="openai",
            voice="coral",
            custom_voice_id="",
            doubao_voice_type="",
        )
    )

    assert result.provider == "mock"
    assert result.mime_type == "audio/wav"
    assert base64.b64decode(result.audio_b64)
    assert len(result.segments) == 3
    assert all(0.0 <= segment.x <= 1.0 for segment in result.segments)
