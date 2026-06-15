from __future__ import annotations

import base64
import json
import shutil
import tempfile
import time
import wave
from io import BytesIO
from pathlib import Path
from typing import Any, Literal

import httpx
from openai import OpenAI
from pydantic import BaseModel, Field, field_validator

from .config import Settings

NarrationProvider = Literal["openai", "doubao", "mock"]


class NarrationSegment(BaseModel):
    text: str = Field(min_length=1, max_length=240)
    target_label: str = Field(default="", max_length=80)
    x: float = Field(ge=0.0, le=1.0)
    y: float = Field(ge=0.0, le=1.0)
    emphasis: str = Field(default="normal", max_length=40)


class NarrationPlan(BaseModel):
    script: str = Field(min_length=1, max_length=1600)
    segments: list[NarrationSegment] = Field(min_length=1, max_length=16)

    @field_validator("segments")
    @classmethod
    def validate_segments(cls, value: list[NarrationSegment]) -> list[NarrationSegment]:
        return clamp_segments(value)


class NarrationResponse(BaseModel):
    audio_b64: str
    mime_type: str
    script: str
    segments: list[NarrationSegment]
    provider: str
    model: str
    timings_ms: dict[str, int]
    warnings: list[str] = Field(default_factory=list)


class NarrationService:
    """为终稿图生成讲解音频和光标时间轴。"""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings()
        self.openai_client = (
            OpenAI(api_key=self.settings.openai_api_key, base_url=self.settings.openai_client_base_url)
            if self.settings.openai_api_key
            else None
        )

    async def narrate(
        self,
        *,
        image_bytes: bytes | None,
        image_content_type: str | None,
        graph_json: str,
        mermaid: str,
        transcript: str,
        provider: NarrationProvider,
        voice: str,
        custom_voice_id: str,
        doubao_voice_type: str,
    ) -> NarrationResponse:
        if provider not in {"openai", "doubao", "mock"}:
            raise ValueError("provider 只能是 openai、doubao 或 mock")
        if not image_bytes:
            raise ValueError("请先生成终稿图，再生成语音讲解")

        start = time.perf_counter()
        warnings: list[str] = []

        plan_start = time.perf_counter()
        plan = await self._build_plan(
            image_bytes=image_bytes,
            image_content_type=image_content_type,
            graph_json=graph_json,
            mermaid=mermaid,
            transcript=transcript,
            warnings=warnings,
        )
        timings = {"plan": int((time.perf_counter() - plan_start) * 1000)}

        speech_start = time.perf_counter()
        audio_bytes, mime_type, actual_provider, model = await self._render_speech(
            script=plan.script,
            provider=provider,
            voice=voice,
            custom_voice_id=custom_voice_id,
            doubao_voice_type=doubao_voice_type,
            warnings=warnings,
        )
        timings["tts"] = int((time.perf_counter() - speech_start) * 1000)
        timings["total"] = int((time.perf_counter() - start) * 1000)
        return NarrationResponse(
            audio_b64=base64.b64encode(audio_bytes).decode("ascii"),
            mime_type=mime_type,
            script=plan.script,
            segments=plan.segments,
            provider=actual_provider,
            model=model,
            timings_ms=timings,
            warnings=warnings,
        )

    async def _build_plan(
        self,
        *,
        image_bytes: bytes,
        image_content_type: str | None,
        graph_json: str,
        mermaid: str,
        transcript: str,
        warnings: list[str],
    ) -> NarrationPlan:
        fallback = NarrationPlan(
            script=build_narration_script(graph_json=graph_json, mermaid=mermaid, transcript=transcript),
            segments=build_fallback_segments(graph_json=graph_json, transcript=transcript),
        )
        if self.settings.use_mock or not self.openai_client:
            warnings.append("讲解计划运行在 mock/fallback 模式。")
            return fallback

        try:
            image_url = image_data_url(image_bytes, image_content_type)
            response = self.openai_client.responses.parse(
                model=self.settings.openai_graph_model,
                instructions=(
                    "你是科研方法图讲解导演。根据终稿图和结构化节点，生成简洁中文讲解稿，"
                    "并给每个讲解段落安排光标在图片上的归一化位置。坐标 x/y 范围必须是 0 到 1。"
                ),
                input=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_text",
                                "text": (
                                    "请生成终稿图讲解计划。"
                                    f"\n结构 JSON：{compact(graph_json, 2000)}"
                                    f"\nMermaid：{compact(mermaid, 1200)}"
                                    f"\n原始说明：{compact(transcript, 1000)}"
                                ),
                            },
                            {"type": "input_image", "image_url": image_url},
                        ],
                    }
                ],
                text_format=NarrationPlan,
                store=False,
            )
            if response.output_parsed:
                return response.output_parsed
        except Exception as exc:
            warnings.append(f"OpenAI 讲解计划生成失败，已回退节点顺序：{type(exc).__name__}")
        return fallback

    async def _render_speech(
        self,
        *,
        script: str,
        provider: NarrationProvider,
        voice: str,
        custom_voice_id: str,
        doubao_voice_type: str,
        warnings: list[str],
    ) -> tuple[bytes, str, str, str]:
        if self.settings.use_mock or provider == "mock":
            return make_mock_speech(), "audio/wav", "mock", "mock-tts"

        try:
            if provider == "openai":
                return (
                    await self._render_openai_speech(script=script, voice=voice, custom_voice_id=custom_voice_id),
                    "audio/mpeg",
                    "openai",
                    self.settings.openai_tts_model,
                )
            if provider == "doubao":
                return (
                    await self._render_doubao_speech(script=script, voice_type=doubao_voice_type or custom_voice_id),
                    "audio/mpeg",
                    "doubao",
                    self.settings.doubao_tts_model,
                )
        except Exception as exc:
            warnings.append(f"{provider} TTS 失败，尝试本机 fallback：{type(exc).__name__}")

        try:
            return await render_system_speech(script), "audio/wav", "system-say", "Tingting"
        except Exception as exc:
            warnings.append(f"本机 TTS 失败，已返回 mock WAV：{type(exc).__name__}")
            return make_mock_speech(), "audio/wav", "mock", "mock-tts"

    async def _render_openai_speech(self, *, script: str, voice: str, custom_voice_id: str) -> bytes:
        if not self.openai_client:
            raise ValueError("缺少 OPENAI_API_KEY")
        voice_payload: str | dict[str, str] = {"id": custom_voice_id.strip()} if custom_voice_id.strip() else (voice or self.settings.openai_tts_voice)
        response = self.openai_client.audio.speech.create(
            model=self.settings.openai_tts_model,
            voice=voice_payload,  # type: ignore[arg-type]
            input=script,
            instructions="请用清晰、自然的中文课程讲解语气朗读，节奏适合指针同步演示。",
            response_format="mp3",
        )
        return binary_response_to_bytes(response)

    async def _render_doubao_speech(self, *, script: str, voice_type: str) -> bytes:
        if not self.settings.ark_api_key:
            raise ValueError("缺少 ARK_API_KEY")
        payload = {
            "model": self.settings.doubao_tts_model,
            "input": script,
            "voice": voice_type or self.settings.doubao_tts_voice,
            "voice_type": voice_type or self.settings.doubao_tts_voice,
            "response_format": "mp3",
        }
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.settings.ark_image_base_url.rstrip('/')}/audio/speech",
                headers={"Authorization": f"Bearer {self.settings.ark_api_key}", "Content-Type": "application/json"},
                json=payload,
            )
            response.raise_for_status()
        if "json" not in response.headers.get("content-type", ""):
            return response.content
        body = response.json()
        for key in ("audio", "b64_json", "data"):
            value = body.get(key)
            if isinstance(value, str):
                return base64.b64decode(value.split(",", 1)[-1])
        raise ValueError("豆包 TTS 未返回音频内容")


def build_narration_script(*, graph_json: str, mermaid: str, transcript: str) -> str:
    labels = graph_labels(graph_json)
    if labels:
        if len(labels) == 1:
            body = labels[0]
        else:
            body = "、".join(labels[:8])
        return f"这张终稿方法图主要包含 {body}。请跟随光标，从输入开始理解每个模块如何连接，并观察最终输出。"
    if transcript.strip():
        return f"这张终稿图对应的讲解是：{compact(transcript, 520)}"
    if mermaid.strip():
        return "这张终稿图展示了一个科研方法流程。光标会按照图中的主要模块顺序移动，帮助理解整体结构。"
    return "这张终稿图展示了语音和草图共同生成方法图的流程。"


def build_fallback_segments(*, graph_json: str, transcript: str) -> list[NarrationSegment]:
    labels = graph_labels(graph_json) or fallback_labels(transcript)
    count = max(1, len(labels))
    segments: list[NarrationSegment] = []
    for index, label in enumerate(labels):
        x = 0.16 + (0.68 * index / max(1, count - 1))
        y = 0.34 if index % 2 == 0 else 0.62
        segments.append(
            NarrationSegment(
                text=f"这里是{label}。",
                target_label=label,
                x=round(x, 4),
                y=round(y, 4),
                emphasis="focus" if index in {0, count - 1} else "normal",
            )
        )
    return segments


def graph_labels(graph_json: str) -> list[str]:
    if not graph_json.strip():
        return []
    try:
        graph = json.loads(graph_json)
    except json.JSONDecodeError:
        return []
    labels: list[str] = []
    for node in graph.get("nodes", [])[:10]:
        if isinstance(node, dict):
            label = str(node.get("label", "")).strip()
            if label:
                labels.append(label)
    return labels


def fallback_labels(transcript: str) -> list[str]:
    compacted = compact(transcript, 120)
    if not compacted:
        return ["输入", "核心模块", "输出"]
    return ["开场", "关键流程", "结果输出"]


def clamp_segments(segments: list[NarrationSegment]) -> list[NarrationSegment]:
    return [
        segment.model_copy(
            update={
                "x": min(1.0, max(0.0, segment.x)),
                "y": min(1.0, max(0.0, segment.y)),
            }
        )
        for segment in segments
    ]


def image_data_url(image_bytes: bytes, content_type: str | None) -> str:
    encoded = base64.b64encode(image_bytes).decode("ascii")
    return f"data:{content_type or 'image/png'};base64,{encoded}"


def binary_response_to_bytes(response: object) -> bytes:
    content = getattr(response, "content", None)
    if isinstance(content, bytes):
        return content
    read = getattr(response, "read", None)
    if callable(read):
        data = read()
        if isinstance(data, bytes):
            return data
    raise TypeError("无法读取 TTS 二进制响应")


async def render_system_speech(script: str) -> bytes:
    if not shutil.which("say") or not shutil.which("afconvert"):
        raise RuntimeError("当前系统缺少 say 或 afconvert")
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        aiff_path = tmp / "narration.aiff"
        wav_path = tmp / "narration.wav"
        import asyncio

        say_proc = await asyncio.create_subprocess_exec("say", "-v", "Tingting", "-o", str(aiff_path), script)
        if await say_proc.wait() != 0:
            raise RuntimeError("say 生成语音失败")
        convert_proc = await asyncio.create_subprocess_exec(
            "afconvert",
            "-f",
            "WAVE",
            "-d",
            "LEI16",
            str(aiff_path),
            str(wav_path),
        )
        if await convert_proc.wait() != 0:
            raise RuntimeError("afconvert 转换 WAV 失败")
        return wav_path.read_bytes()


def make_mock_speech() -> bytes:
    sample_rate = 16000
    frames = sample_rate
    buffer = BytesIO()
    with wave.open(buffer, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(b"\x00\x00" * frames)
    return buffer.getvalue()


def compact(value: str, limit: int) -> str:
    return " ".join(value.split())[:limit]
