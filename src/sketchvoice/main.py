from __future__ import annotations

import json
import mimetypes
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .config import Settings
from .image_service import ImageRenderService
from .narration_service import NarrationService
from .openai_service import SketchVoiceGenerator

STATIC_DIR = Path(__file__).parent / "static"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SAMPLES_PATH = PROJECT_ROOT / "data" / "samples.json"


def create_app(settings: Settings | None = None) -> FastAPI:
    app = FastAPI(title="SketchVoice 方法图工坊", version="0.1.0")
    resolved_settings = settings or Settings()
    app.state.settings = resolved_settings
    app.state.generator = SketchVoiceGenerator(resolved_settings)
    app.state.image_renderer = ImageRenderService(resolved_settings)
    app.state.narration_service = NarrationService(resolved_settings)
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @app.get("/")
    async def index() -> FileResponse:
        return FileResponse(STATIC_DIR / "index.html")

    @app.get("/health")
    async def health(request: Request) -> dict[str, object]:
        current = request.app.state.settings
        return {
            "ok": True,
            "mock": current.use_mock,
            "transcribe_model": current.openai_transcribe_model,
            "graph_model": current.openai_graph_model,
            "draft_image_model": current.doubao_draft_image_model,
            "final_image_model": current.openai_final_image_model,
            "tts_model": current.openai_tts_model,
            "sample_tts_provider": current.sample_tts_provider,
            "image_mock": current.image_mock,
            "max_audio_mb": current.max_audio_mb,
        }

    @app.get("/api/samples")
    async def list_samples() -> dict[str, object]:
        samples = []
        for sample in load_samples():
            if not sample.get("sketch_path"):
                continue
            sample_id = str(sample["id"])
            samples.append(
                {
                    "id": sample_id,
                    "topic": sample.get("topic", sample_id),
                    "difficulty": sample.get("difficulty", "demo"),
                    "transcript": sample.get("transcript", ""),
                    "direction": sample.get("expected_mermaid_direction", "LR"),
                    "sketch_url": f"/api/samples/{sample_id}/sketch",
                    "audio_url": f"/api/samples/{sample_id}/audio" if sample.get("audio_path") else None,
                    "gold_nodes": sample.get("gold_nodes", []),
                    "gold_edges": sample.get("gold_edges", []),
                }
            )
        return {"samples": samples}

    @app.get("/api/samples/{sample_id}/sketch")
    async def sample_sketch(sample_id: str) -> FileResponse:
        sample = get_sample(sample_id)
        path = resolve_project_path(sample.get("sketch_path"))
        if not path or not path.exists():
            raise HTTPException(status_code=404, detail="样例草图不存在")
        return FileResponse(path, media_type=mimetypes.guess_type(path.name)[0] or "image/png")

    @app.get("/api/samples/{sample_id}/audio")
    async def sample_audio(sample_id: str) -> FileResponse:
        sample = get_sample(sample_id)
        path = resolve_project_path(sample.get("audio_path"))
        if not path or not path.exists():
            raise HTTPException(status_code=404, detail="样例音频不存在")
        return FileResponse(path, media_type=mimetypes.guess_type(path.name)[0] or "audio/wav")

    @app.post("/api/generate")
    async def generate(
        request: Request,
        sketch: UploadFile | None = File(default=None),
        audio: UploadFile | None = File(default=None),
        transcript: str | None = Form(default=None),
        direction: str = Form(default="LR"),
    ) -> dict[str, object]:
        try:
            sketch_bytes = await sketch.read() if sketch else None
            audio_bytes = await audio.read() if audio else None
            result = await request.app.state.generator.generate(
                sketch_bytes=sketch_bytes,
                sketch_content_type=sketch.content_type if sketch else None,
                audio_bytes=audio_bytes,
                audio_filename=audio.filename if audio else None,
                audio_content_type=audio.content_type if audio else None,
                transcript=transcript,
                direction=direction,
            )
            return result.model_dump()
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"生成失败：{type(exc).__name__}") from exc

    @app.post("/api/render-image")
    async def render_image(
        request: Request,
        mode: str = Form(default="draft"),
        sketch: UploadFile | None = File(default=None),
        transcript: str = Form(default=""),
        mermaid: str = Form(default=""),
        graph_json: str = Form(default=""),
        style: str = Form(default="paper"),
    ) -> dict[str, object]:
        if mode not in {"draft", "final"}:
            raise HTTPException(status_code=400, detail="mode 只能是 draft 或 final")
        try:
            sketch_bytes = await sketch.read() if sketch else None
            result = await request.app.state.image_renderer.render(
                mode=mode,
                sketch_bytes=sketch_bytes,
                sketch_content_type=sketch.content_type if sketch else None,
                transcript=transcript,
                mermaid=mermaid,
                graph_json=graph_json,
                style=style,
            )
            return result.model_dump()
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"生图失败：{type(exc).__name__}") from exc

    @app.post("/api/narrate-image")
    async def narrate_image(
        request: Request,
        image: UploadFile | None = File(default=None),
        graph_json: str = Form(default=""),
        mermaid: str = Form(default=""),
        transcript: str = Form(default=""),
        provider: str = Form(default=""),
        voice: str = Form(default=""),
        custom_voice_id: str = Form(default=""),
        doubao_voice_type: str = Form(default=""),
    ) -> dict[str, object]:
        current = request.app.state.settings
        selected_provider = provider or current.narration_tts_provider
        selected_voice = voice or current.narration_openai_voice
        selected_custom_voice_id = custom_voice_id or current.narration_custom_voice_id
        selected_doubao_voice_type = doubao_voice_type or current.narration_doubao_voice_type
        try:
            image_bytes = await image.read() if image else None
            result = await request.app.state.narration_service.narrate(
                image_bytes=image_bytes,
                image_content_type=image.content_type if image else None,
                graph_json=graph_json,
                mermaid=mermaid,
                transcript=transcript,
                provider=selected_provider,  # type: ignore[arg-type]
                voice=selected_voice,
                custom_voice_id=selected_custom_voice_id,
                doubao_voice_type=selected_doubao_voice_type,
            )
            return result.model_dump()
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"语音讲解生成失败：{type(exc).__name__}") from exc

    return app


def load_samples() -> list[dict[str, object]]:
    if not SAMPLES_PATH.exists():
        return []
    return json.loads(SAMPLES_PATH.read_text(encoding="utf-8"))


def get_sample(sample_id: str) -> dict[str, object]:
    for sample in load_samples():
        if sample.get("id") == sample_id:
            return sample
    raise HTTPException(status_code=404, detail="样例不存在")


def resolve_project_path(value: object) -> Path | None:
    if not isinstance(value, str) or not value:
        return None
    path = Path(value)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    resolved = path.resolve()
    try:
        resolved.relative_to(PROJECT_ROOT)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="非法样例路径") from exc
    return resolved


app = create_app()
