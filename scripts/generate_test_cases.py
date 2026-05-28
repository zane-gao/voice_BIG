from __future__ import annotations

import argparse
import asyncio
import base64
import json
import math
import shutil
import tempfile
import wave
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Literal

import httpx
from openai import OpenAI
from PIL import Image, ImageDraw, ImageFont

from sketchvoice.config import Settings
from sketchvoice.image_service import extract_b64_image

TTSProvider = Literal["openai", "doubao", "auto"]


@dataclass(frozen=True)
class CaseDefinition:
    id: str
    topic: str
    difficulty: str
    direction: str
    transcript: str
    gold_nodes: list[str]
    gold_edges: list[list[str]]
    sketch_prompt: str


@dataclass(frozen=True)
class SpeechAsset:
    data: bytes
    suffix: str


CASE_DEFINITIONS: dict[str, CaseDefinition] = {
    "cnn_explainer": CaseDefinition(
        id="cnn_explainer",
        topic="卷积神经网络讲解",
        difficulty="intro",
        direction="LR",
        transcript=(
            "这张图我想讲卷积神经网络。左边是输入图像，先用一组小的卷积核在局部窗口上滑动，"
            "提取边缘、纹理这些低层特征，得到多张特征图。特征图经过 ReLU 激活以后，再做池化，"
            "把空间尺寸降下来，同时保留主要响应。后面可以堆叠多层卷积和池化，让特征从局部边缘逐渐变成物体部件和语义概念。"
            "最后把特征展平，接全连接层，再经过 Softmax 输出类别概率。这里有两个关键词，一个是局部感受野，"
            "另一个是参数共享，它们让 CNN 比普通全连接网络更适合处理图像。"
        ),
        gold_nodes=[
            "输入图像",
            "卷积核",
            "特征图",
            "ReLU",
            "池化",
            "多层卷积",
            "Flatten",
            "全连接",
            "Softmax分类",
            "局部感受野",
            "参数共享",
        ],
        gold_edges=[
            ["输入图像", "卷积核"],
            ["卷积核", "特征图"],
            ["特征图", "ReLU"],
            ["ReLU", "池化"],
            ["池化", "多层卷积"],
            ["多层卷积", "Flatten"],
            ["Flatten", "全连接"],
            ["全连接", "Softmax分类"],
            ["局部感受野", "卷积核"],
            ["参数共享", "卷积核"],
        ],
        sketch_prompt=(
            "画一页真实手写课堂草图，白纸背景，主题是卷积神经网络 CNN。左到右流程：输入图像、卷积核、特征图、ReLU、池化、"
            "多层卷积、Flatten、全连接、Softmax 分类。用手绘框、箭头、少量中文和英文标签，旁边写局部感受野、参数共享、层级特征。"
            "要求像学生在平板白板上的手写笔记，线条自然，清晰可读，不要照片质感，不要水印。"
        ),
    ),
    "diffusion_roadmap": CaseDefinition(
        id="diffusion_roadmap",
        topic="扩散技术发展路线",
        difficulty="intermediate",
        direction="LR",
        transcript=(
            "这张草图讲扩散模型的发展路线。最早可以从 DDPM 开始，它把生成过程看成从高斯噪声逐步去噪。"
            "DDIM 进一步提供了更少步数的确定性采样思路。后面 Classifier-Free Guidance 让文本条件控制变得更稳定，"
            "Latent Diffusion 把扩散过程搬到潜空间里，显著降低计算量，也推动了 Stable Diffusion 的普及。"
            "再往后，ControlNet 这类方法把边缘图、姿态、深度图作为控制条件，让图像生成更可控。"
            "DiT 把 Transformer 引入扩散骨干，Consistency Models 和蒸馏路线则主要解决快速采样问题。"
            "所以这条线可以概括为：从像素扩散到潜空间，从无条件生成到强条件控制，再到更快、更大的生成系统。"
        ),
        gold_nodes=[
            "DDPM",
            "DDIM",
            "Classifier-Free Guidance",
            "Latent Diffusion",
            "Stable Diffusion",
            "ControlNet",
            "DiT",
            "Consistency Models",
            "采样加速",
            "文本条件控制",
        ],
        gold_edges=[
            ["DDPM", "DDIM"],
            ["DDIM", "Classifier-Free Guidance"],
            ["Classifier-Free Guidance", "文本条件控制"],
            ["Classifier-Free Guidance", "Latent Diffusion"],
            ["Latent Diffusion", "Stable Diffusion"],
            ["Stable Diffusion", "ControlNet"],
            ["Stable Diffusion", "DiT"],
            ["DiT", "Consistency Models"],
            ["Consistency Models", "采样加速"],
        ],
        sketch_prompt=(
            "画一页手写技术路线图，主题是扩散模型发展脉络。左到右时间线：DDPM、DDIM、Classifier-Free Guidance、"
            "Latent Diffusion / Stable Diffusion、ControlNet、DiT、Consistency Models / 快速采样。白底，手绘箭头，"
            "像科研讨论白板笔记，标注从像素扩散到潜空间、文本条件控制、采样加速。清晰但保持手写草图感。"
        ),
    ),
    "video_generation_timeline": CaseDefinition(
        id="video_generation_timeline",
        topic="视频生成模型的发展脉络",
        difficulty="advanced",
        direction="LR",
        transcript=(
            "这张图想梳理视频生成模型的发展脉络。早期很多方法基于 GAN、RNN 或者帧预测，只能生成比较短的视频片段，"
            "而且容易出现闪烁和时序不一致。后来 Video Diffusion Models 把扩散生成扩展到视频维度，"
            "Imagen Video 和 Phenaki 进一步展示了文本到视频和长视频生成的可能性。"
            "VideoLDM 这类方法把潜空间扩散用于视频，降低了计算成本。再往后，时空 Transformer 和 DiT 风格的结构开始成为核心，"
            "通过时空 patch 同时建模画面内容和运动。Lumiere、Sora 这一类系统强调更长时长、更一致的运动、更强的镜头控制。"
            "所以评测视频生成时，除了看画质，还要看时序一致性、运动合理性、文本对齐和长视频稳定性。"
        ),
        gold_nodes=[
            "早期GAN/RNN视频",
            "帧预测",
            "Video Diffusion Models",
            "Imagen Video",
            "Phenaki",
            "VideoLDM",
            "时空Transformer",
            "Lumiere",
            "Sora",
            "时序一致性",
            "长视频生成",
            "文本到视频",
        ],
        gold_edges=[
            ["早期GAN/RNN视频", "帧预测"],
            ["帧预测", "Video Diffusion Models"],
            ["Video Diffusion Models", "Imagen Video"],
            ["Video Diffusion Models", "Phenaki"],
            ["Imagen Video", "文本到视频"],
            ["Phenaki", "长视频生成"],
            ["Video Diffusion Models", "VideoLDM"],
            ["VideoLDM", "时空Transformer"],
            ["时空Transformer", "Lumiere"],
            ["时空Transformer", "Sora"],
            ["Sora", "时序一致性"],
        ],
        sketch_prompt=(
            "画一页手写白板路线图，主题是视频生成模型发展脉络。左到右：早期 GAN/RNN 视频、帧预测、Video Diffusion Models、"
            "Imagen Video、Phenaki、VideoLDM、时空 Transformer/DiT、Lumiere、Sora。旁边分支标注时序一致性、长视频生成、"
            "文本到视频、运动控制。要求像真实手写科研笔记，白底，框线箭头清楚，少量蓝绿色强调。"
        ),
    ),
}


async def write_case_assets(
    case: CaseDefinition,
    *,
    output_root: Path,
    mock: bool,
    force: bool,
    tts_provider: TTSProvider,
    settings: Settings | None = None,
) -> dict[str, object]:
    settings = settings or Settings()
    case_dir = output_root / case.id
    case_dir.mkdir(parents=True, exist_ok=True)

    sketch_path = case_dir / "sketch.png"
    audio_path = existing_audio_path(case_dir)
    transcript_path = case_dir / "transcript.txt"
    gold_path = case_dir / "gold.json"
    warnings: list[str] = []

    transcript_path.write_text(case.transcript + "\n", encoding="utf-8")
    if force or not sketch_path.exists():
        sketch_bytes, sketch_warnings = await render_sketch(case, settings=settings, mock=mock)
        warnings.extend(sketch_warnings)
        sketch_path.write_bytes(to_png(sketch_bytes))
    if force or not audio_path.exists():
        speech_asset, speech_warnings = await render_speech(
            case.transcript,
            settings=settings,
            mock=mock,
            provider=tts_provider,
        )
        warnings.extend(speech_warnings)
        audio_path = case_dir / f"speech{speech_asset.suffix}"
        for stale in case_dir.glob("speech.*"):
            if stale != audio_path:
                stale.unlink()
        audio_path.write_bytes(speech_asset.data)

    gold = {
        "id": case.id,
        "topic": case.topic,
        "difficulty": case.difficulty,
        "expected_mermaid_direction": case.direction,
        "gold_nodes": case.gold_nodes,
        "gold_edges": case.gold_edges,
        "warnings": warnings,
    }
    gold_path.write_text(json.dumps(gold, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return {
        "id": case.id,
        "topic": case.topic,
        "difficulty": case.difficulty,
        "transcript": case.transcript,
        "transcript_path": str(transcript_path),
        "sketch_path": str(sketch_path),
        "audio_path": str(audio_path),
        "expected_mermaid_direction": case.direction,
        "gold_nodes": case.gold_nodes,
        "gold_edges": case.gold_edges,
    }


async def render_sketch(case: CaseDefinition, *, settings: Settings, mock: bool) -> tuple[bytes, list[str]]:
    if mock or settings.image_mock or not settings.ark_api_key:
        return make_mock_sketch(case), ["草图使用 mock/PIL 生成，未调用豆包。"]

    payload: dict[str, object] = {
        "model": settings.doubao_draft_image_model,
        "prompt": case.sketch_prompt,
        "response_format": "b64_json",
        "output_format": "png",
        "watermark": False,
        "size": settings.doubao_draft_size,
        "sequential_image_generation": "disabled",
    }
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{settings.ark_image_base_url.rstrip('/')}/images/generations",
                headers={"Authorization": f"Bearer {settings.ark_api_key}"},
                json=payload,
            )
            response.raise_for_status()
        return base64.b64decode(extract_b64_image(response.json())), []
    except Exception as exc:
        return make_mock_sketch(case), [f"豆包草图生成失败，已回退 PIL：{type(exc).__name__}"]


async def render_speech(
    transcript: str,
    *,
    settings: Settings,
    mock: bool,
    provider: TTSProvider,
) -> tuple[SpeechAsset, list[str]]:
    if mock:
        return SpeechAsset(make_mock_speech(), ".wav"), ["语音使用 mock 静音音频生成，未调用 TTS API。"]

    providers: list[TTSProvider]
    if provider == "auto":
        providers = ["openai", "doubao"]
    else:
        providers = [provider]

    warnings: list[str] = []
    for current in providers:
        try:
            if current == "openai":
                return SpeechAsset(await render_openai_speech(transcript, settings), ".mp3"), warnings
            if current == "doubao":
                return SpeechAsset(await render_doubao_speech(transcript, settings), ".mp3"), warnings
        except Exception as exc:
            warnings.append(f"{current} TTS 失败，已尝试回退：{type(exc).__name__}")
    try:
        return SpeechAsset(await render_system_speech(transcript), ".wav"), warnings + ["API TTS 均失败，已用 macOS say 生成本机语音。"]
    except Exception as exc:
        return SpeechAsset(make_mock_speech(), ".wav"), warnings + [f"本机 TTS 失败：{type(exc).__name__}", "所有 TTS provider 均失败，已写入 mock 静音音频。"]


def existing_audio_path(case_dir: Path) -> Path:
    for name in ("speech.mp3", "speech.wav"):
        path = case_dir / name
        if path.exists():
            return path
    return case_dir / "speech.mp3"


async def render_openai_speech(transcript: str, settings: Settings) -> bytes:
    if not settings.openai_api_key:
        raise ValueError("缺少 OPENAI_API_KEY")
    client = OpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url)
    response = client.audio.speech.create(
        model=settings.openai_tts_model,
        voice=settings.openai_tts_voice,
        input=transcript,
        instructions="请用清晰、自然的中文课程讲解语气朗读，语速中等，适合课堂演示。",
        response_format="mp3",
    )
    return binary_response_to_bytes(response)


async def render_doubao_speech(transcript: str, settings: Settings) -> bytes:
    if not settings.ark_api_key:
        raise ValueError("缺少 ARK_API_KEY")
    # 这里使用方舟 OpenAI-compatible 风格的语音端点；若账号/模型未开放，会自动回退。
    payload = {
        "model": settings.doubao_tts_model,
        "input": transcript,
        "voice": settings.doubao_tts_voice,
        "response_format": "mp3",
    }
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{settings.ark_image_base_url.rstrip('/')}/audio/speech",
            headers={"Authorization": f"Bearer {settings.ark_api_key}", "Content-Type": "application/json"},
            json=payload,
        )
        response.raise_for_status()
    content_type = response.headers.get("content-type", "")
    if "json" not in content_type:
        return response.content
    body = response.json()
    for key in ("audio", "b64_json", "data"):
        value = body.get(key)
        if isinstance(value, str):
            return base64.b64decode(value.split(",", 1)[-1])
    raise ValueError("豆包 TTS 未返回音频内容")


async def render_system_speech(transcript: str) -> bytes:
    if not shutil.which("say") or not shutil.which("afconvert"):
        raise RuntimeError("当前系统缺少 say 或 afconvert")
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        aiff_path = tmp / "speech.aiff"
        wav_path = tmp / "speech.wav"
        say_proc = await asyncio.create_subprocess_exec(
            "say",
            "-v",
            "Tingting",
            "-o",
            str(aiff_path),
            transcript,
        )
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


def to_png(image_bytes: bytes) -> bytes:
    image = Image.open(BytesIO(image_bytes)).convert("RGB")
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def make_mock_sketch(case: CaseDefinition) -> bytes:
    width, height = 1440, 900
    image = Image.new("RGB", (width, height), (255, 255, 252))
    draw = ImageDraw.Draw(image)
    title_font, body_font, small_font = load_fonts()
    draw.text((54, 36), case.topic, fill=(17, 24, 39), font=title_font)
    draw.line((48, 92, width - 48, 92), fill=(20, 184, 166), width=4)

    nodes = case.gold_nodes[:8]
    positions = layout_positions(len(nodes), width, height)
    for idx, (label, (x, y)) in enumerate(zip(nodes, positions)):
        jitter = math.sin(idx + 1) * 5
        box = (x + jitter, y, x + 194 + jitter, y + 78)
        draw.rounded_rectangle(box, radius=14, outline=(71, 85, 105), fill=(248, 250, 252), width=3)
        draw.text((box[0] + 18, box[1] + 23), label[:12], fill=(31, 41, 55), font=body_font)
        if idx > 0:
            px, py = positions[idx - 1]
            draw.line((px + 194, py + 39, box[0], box[1] + 39), fill=(100, 116, 139), width=4)
            draw.polygon([(box[0] - 10, box[1] + 31), (box[0], box[1] + 39), (box[0] - 10, box[1] + 47)], fill=(100, 116, 139))

    notes = case.gold_nodes[8:12]
    for idx, note in enumerate(notes):
        y = height - 190 + idx * 38
        draw.ellipse((68, y + 8, 82, y + 22), fill=(245, 158, 11))
        draw.text((96, y), note, fill=(75, 85, 99), font=small_font)

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def layout_positions(count: int, width: int, height: int) -> list[tuple[int, int]]:
    cols = min(4, count)
    rows = math.ceil(count / cols)
    x_gap = (width - 160) // cols
    y_start = 180 if rows == 1 else 155
    positions: list[tuple[int, int]] = []
    for idx in range(count):
        row = idx // cols
        col = idx % cols
        x = 80 + col * x_gap
        y = y_start + row * 170
        positions.append((x, y))
    return positions


def load_fonts() -> tuple[ImageFont.FreeTypeFont | ImageFont.ImageFont, ImageFont.FreeTypeFont | ImageFont.ImageFont, ImageFont.FreeTypeFont | ImageFont.ImageFont]:
    try:
        return (
            ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 42),
            ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 27),
            ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 24),
        )
    except Exception:
        fallback = ImageFont.load_default()
        return fallback, fallback, fallback


def make_mock_speech() -> bytes:
    sample_rate = 16000
    duration_s = 1.0
    frames = int(sample_rate * duration_s)
    buffer = BytesIO()
    with wave.open(buffer, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(b"\x00\x00" * frames)
    return buffer.getvalue()


def merge_sample_records(existing: list[dict[str, object]], new_records: list[dict[str, object]]) -> list[dict[str, object]]:
    merged = {str(sample["id"]): sample for sample in existing}
    for record in new_records:
        merged[str(record["id"])] = record
    return list(merged.values())


async def generate_cases(args: argparse.Namespace) -> list[dict[str, object]]:
    selected = args.case or list(CASE_DEFINITIONS)
    output_root = Path(args.output_root)
    records: list[dict[str, object]] = []
    for case_id in selected:
        records.append(
            await write_case_assets(
                CASE_DEFINITIONS[case_id],
                output_root=output_root,
                mock=args.mock,
                force=args.force,
                tts_provider=args.tts_provider,
            )
        )
    return records


def main() -> None:
    parser = argparse.ArgumentParser(description="生成草图 + 语音测试案例，并更新 data/samples.json。")
    parser.add_argument("--case", choices=sorted(CASE_DEFINITIONS), nargs="*", help="只生成指定案例；默认生成全部")
    parser.add_argument("--output-root", type=Path, default=Path("data/cases"))
    parser.add_argument("--samples", type=Path, default=Path("data/samples.json"))
    parser.add_argument("--mock", action="store_true", help="不调用外部 API，生成可测试占位资产")
    parser.add_argument("--force", action="store_true", help="覆盖已存在的草图和语音资产")
    parser.add_argument("--tts-provider", choices=["openai", "doubao", "auto"], default=Settings().sample_tts_provider)
    args = parser.parse_args()

    records = asyncio.run(generate_cases(args))
    existing = json.loads(args.samples.read_text(encoding="utf-8")) if args.samples.exists() else []
    merged = merge_sample_records(existing, records)
    args.samples.parent.mkdir(parents=True, exist_ok=True)
    args.samples.write_text(json.dumps(merged, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"generated": [record["id"] for record in records], "samples": str(args.samples)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
