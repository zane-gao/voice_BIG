import asyncio
import base64
from types import SimpleNamespace

import httpx

from sketchvoice.config import Settings
from sketchvoice.image_service import ImageRenderService, build_image_prompt, graph_from_mermaid, make_mock_image


def test_build_image_prompt_prefers_graph_json() -> None:
    prompt = build_image_prompt(
        mode="draft",
        transcript="这段文本应作为备选。",
        mermaid="flowchart LR\nA-->B",
        graph_json='{"nodes":[{"label":"语音输入"},{"label":"草图解析"}],"edges":[{"source":"a","target":"b"}]}',
        style="paper",
    )
    assert "论文级知识信息图" in prompt
    assert "不是复刻原始手绘草图" in prompt
    assert "草图图像只作为粗略布局参考" in prompt
    assert "不要照搬手绘线条" in prompt
    assert "不要把本提示词" in prompt
    assert "语音输入" in prompt
    assert "草图解析" in prompt


def test_build_image_prompt_requires_redrawing_instead_of_copying_sketch() -> None:
    prompt = build_image_prompt(
        mode="final",
        transcript="输入图像经过卷积、池化和分类头输出类别。",
        mermaid="flowchart LR\ninput[输入图像] --> conv[卷积层] --> pool[池化层] --> out[分类结果]",
        graph_json="",
        style="nature",
    )
    assert "高清终稿图" in prompt
    assert "结构化 JSON 与 Mermaid" in prompt
    assert "草图图像只作为粗略布局参考" in prompt
    assert "根据节点关系重新排版" in prompt
    assert "Nature/Science 风格科研信息图" in prompt
    assert "图中只允许出现方法图标题、节点标签和必要的短边标签" in prompt
    assert len(prompt) <= 2000


def test_draft_image_api_payload_includes_infographic_task_prompt(monkeypatch) -> None:
    captured_payload = {}

    async def fake_post(self, url, *, headers=None, json=None):  # noqa: ANN001
        captured_payload.update(json or {})
        request = httpx.Request("POST", url)
        return httpx.Response(
            200,
            json={"data": [{"b64_json": base64.b64encode(b"image").decode("ascii")}]},
            request=request,
        )

    monkeypatch.setattr(httpx.AsyncClient, "post", fake_post)
    service = ImageRenderService(
        Settings(
            sketchvoice_mock=False,
            ark_api_key="ark-test",
            openai_api_key="sk-test",
        )
    )
    result = asyncio.run(
        service.render(
            mode="draft",
            sketch_bytes=b"not-a-real-image",
            sketch_content_type="image/png",
            transcript="卷积神经网络方法图：输入图像经过卷积、池化和分类头输出类别。",
            mermaid="flowchart LR\ninput[输入图像] --> conv[卷积层] --> pool[池化层] --> out[分类结果]",
            graph_json="",
            style="paper",
        )
    )

    assert result.provider == "doubao"
    assert captured_payload["model"]
    assert captured_payload["image"].startswith("data:image/png;base64,")
    prompt = captured_payload["prompt"]
    assert "论文级知识信息图" in prompt
    assert "不是复刻原始手绘草图" in prompt
    assert "草图图像只作为粗略布局参考" in prompt
    assert "不要照搬手绘线条" in prompt
    assert "根据节点关系重新排版" in prompt
    assert "不要把本提示词" in prompt


def test_final_image_uses_generate_prompt_not_sketch_edit() -> None:
    captured_payload = {}

    class FakeImages:
        def generate(self, **kwargs):  # noqa: ANN001
            captured_payload.update(kwargs)
            return SimpleNamespace(data=[SimpleNamespace(b64_json=base64.b64encode(b"final").decode("ascii"))])

        def edit(self, **kwargs):  # noqa: ANN001
            raise AssertionError("终稿生图不应使用草图 image edit")

    service = ImageRenderService(
        Settings(
            sketchvoice_mock=False,
            openai_api_key="sk-test",
            openai_base_url="https://gmn.chuangzuoli.com",
        )
    )
    service.openai_client = SimpleNamespace(images=FakeImages())
    result = asyncio.run(
        service.render(
            mode="final",
            sketch_bytes=b"not-a-real-image",
            sketch_content_type="image/png",
            transcript="输入图像经过卷积、池化和分类头输出类别。",
            mermaid="flowchart LR\ninput[输入图像] --> conv[卷积层] --> out[分类结果]",
            graph_json='{"title":"CNN 知识图","nodes":[{"id":"input","label":"输入图像","type":"input"},{"id":"conv","label":"卷积层","type":"model"},{"id":"out","label":"分类结果","type":"output"}],"edges":[{"source":"input","target":"conv"},{"source":"conv","target":"out"}]}',
            style="paper",
        )
    )

    assert result.provider == "openai"
    assert captured_payload["model"] == "gpt-image-2"
    assert "image" not in captured_payload
    assert "不要做草图 image-edit" in captured_payload["prompt"]
    assert "图像只是结构化知识图的论文级可视化后处理" in captured_payload["prompt"]


def test_mock_image_does_not_render_prompt_text() -> None:
    image_a, mime_a = make_mock_image(mode="draft", prompt="短提示")
    image_b, mime_b = make_mock_image(
        mode="draft",
        prompt="DO_NOT_RENDER_THIS_PROMPT_MARKER 任务：你是论文图设计师，请把这段长提示词写进图片。",
    )

    assert mime_a == mime_b == "image/jpeg"
    assert image_a == image_b


def test_mock_final_image_is_driven_by_graph_json() -> None:
    common = {"mode": "final", "prompt": "同一提示词"}
    graph_a = '{"title":"CNN 知识图","nodes":[{"id":"input","label":"输入图像","type":"input"},{"id":"conv","label":"卷积层","type":"model"},{"id":"out","label":"分类结果","type":"output"}],"edges":[{"source":"input","target":"conv"},{"source":"conv","target":"out"}]}'
    graph_b = '{"title":"MMSB-Graph","nodes":[{"id":"sketch","label":"草图观测","type":"input"},{"id":"speech","label":"语音锚点","type":"input"},{"id":"bridge","label":"离散图编辑桥","type":"model"},{"id":"graph","label":"标准知识图","type":"output"}],"edges":[{"source":"sketch","target":"bridge"},{"source":"speech","target":"bridge"},{"source":"bridge","target":"graph"}]}'

    image_a, mime_a = make_mock_image(**common, graph_json=graph_a)
    image_b, mime_b = make_mock_image(**common, graph_json=graph_b)

    assert mime_a == mime_b == "image/png"
    assert base64.b64decode(image_a)
    assert base64.b64decode(image_b)
    assert image_a != image_b


def test_mermaid_fallback_preserves_defined_node_labels() -> None:
    graph = graph_from_mermaid(
        'flowchart LR\n  input["输入图像"]\n  conv["卷积层"]\n  out["分类结果"]\n  input --> conv\n  conv --> out'
    )

    assert graph is not None
    assert [node.label for node in graph.nodes] == ["输入图像", "卷积层", "分类结果"]
    assert [(edge.source, edge.target) for edge in graph.edges] == [("input", "conv"), ("conv", "out")]


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
