from fastapi.testclient import TestClient

from sketchvoice.config import Settings
from sketchvoice.main import create_app


def test_health_uses_mock_without_key() -> None:
    app = create_app(Settings(sketchvoice_mock=True))
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["mock"] is True


def test_generate_with_transcript_in_mock_mode() -> None:
    app = create_app(Settings(sketchvoice_mock=True))
    client = TestClient(app)
    response = client.post(
        "/api/generate",
        data={"transcript": "输入语音和草图，输出方法图，并计算评测指标。", "direction": "LR"},
        files={"sketch": ("sketch.png", b"not-a-real-image", "image/png")},
    )
    assert response.status_code == 200
    body = response.json()
    assert "flowchart LR" in body["mermaid"]
    assert body["transcript"].startswith("输入语音")
    assert any(node["id"] == "eval" for node in body["graph"]["nodes"])


def test_render_image_mock_draft() -> None:
    app = create_app(Settings(sketchvoice_mock=True))
    client = TestClient(app)
    response = client.post(
        "/api/render-image",
        data={
            "mode": "draft",
            "transcript": "语音和草图生成方法图。",
            "mermaid": "flowchart LR\nA-->B",
            "style": "paper",
        },
        files={"sketch": ("sketch.png", b"not-a-real-image", "image/png")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["provider"] == "doubao-mock"
    assert body["mime_type"] == "image/jpeg"
    assert body["image_b64"]


def test_render_image_rejects_bad_mode() -> None:
    app = create_app(Settings(sketchvoice_mock=True))
    client = TestClient(app)
    response = client.post("/api/render-image", data={"mode": "bad"})
    assert response.status_code == 400


def test_samples_endpoint_lists_demo_cases() -> None:
    app = create_app(Settings(sketchvoice_mock=True))
    client = TestClient(app)
    response = client.get("/api/samples")
    assert response.status_code == 200
    body = response.json()
    ids = {sample["id"] for sample in body["samples"]}
    assert {"cnn_explainer", "diffusion_roadmap", "video_generation_timeline"} <= ids
    cnn = next(sample for sample in body["samples"] if sample["id"] == "cnn_explainer")
    assert cnn["sketch_url"] == "/api/samples/cnn_explainer/sketch"
    assert cnn["audio_url"] == "/api/samples/cnn_explainer/audio"
    assert "卷积神经网络" in cnn["transcript"]


def test_sample_asset_endpoints_return_files() -> None:
    app = create_app(Settings(sketchvoice_mock=True))
    client = TestClient(app)
    sketch = client.get("/api/samples/cnn_explainer/sketch")
    audio = client.get("/api/samples/cnn_explainer/audio")
    assert sketch.status_code == 200
    assert sketch.headers["content-type"].startswith("image/")
    assert audio.status_code == 200
    assert audio.headers["content-type"].startswith("audio/")


def test_narrate_image_mock_returns_cursor_segments() -> None:
    app = create_app(Settings(sketchvoice_mock=True))
    client = TestClient(app)
    response = client.post(
        "/api/narrate-image",
        data={
            "provider": "openai",
            "voice": "coral",
            "graph_json": '{"nodes":[{"label":"输入"},{"label":"模型"},{"label":"输出"}],"edges":[]}',
            "transcript": "输入经过模型得到输出。",
        },
        files={"image": ("final.png", b"not-a-real-image", "image/png")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["audio_b64"]
    assert body["mime_type"] == "audio/wav"
    assert len(body["segments"]) == 3
    assert all(0 <= segment["x"] <= 1 for segment in body["segments"])


def test_narrate_image_rejects_bad_provider() -> None:
    app = create_app(Settings(sketchvoice_mock=True))
    client = TestClient(app)
    response = client.post("/api/narrate-image", data={"provider": "bad"})
    assert response.status_code == 400
