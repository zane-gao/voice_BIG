from __future__ import annotations

import argparse
import asyncio
import json
import mimetypes
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from sketchvoice.config import Settings
from sketchvoice.openai_service import SketchVoiceGenerator


@dataclass
class ResolvedSampleInputs:
    transcript: str
    sketch_bytes: bytes | None
    sketch_content_type: str | None
    audio_bytes: bytes | None
    audio_filename: str | None
    audio_content_type: str | None


def prf(pred: set, gold: set) -> dict[str, float]:
    hit = len(pred & gold)
    precision = hit / len(pred) if pred else 0.0
    recall = hit / len(gold) if gold else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"precision": precision, "recall": recall, "f1": f1}


def normalize_label(value: str) -> str:
    return "".join(value.lower().split())


def resolve_sample_path(value: str | None, sample_file: Path) -> Path | None:
    if not value:
        return None
    candidate = Path(value)
    if candidate.is_absolute():
        return candidate
    if candidate.exists():
        return candidate
    return sample_file.parent / candidate


def guess_content_type(path: Path, default: str) -> str:
    return mimetypes.guess_type(path.name)[0] or default


def resolve_sample_inputs(sample: dict[str, Any], *, sample_file: Path, include_audio: bool) -> ResolvedSampleInputs:
    transcript = str(sample.get("transcript", "")).strip()
    transcript_path = resolve_sample_path(sample.get("transcript_path"), sample_file)
    if transcript_path and transcript_path.exists():
        transcript = transcript_path.read_text(encoding="utf-8").strip()

    sketch_bytes = None
    sketch_content_type = None
    sketch_path = resolve_sample_path(sample.get("sketch_path"), sample_file)
    if sketch_path and sketch_path.exists():
        sketch_bytes = sketch_path.read_bytes()
        sketch_content_type = guess_content_type(sketch_path, "image/png")

    audio_bytes = None
    audio_filename = None
    audio_content_type = None
    audio_path = resolve_sample_path(sample.get("audio_path"), sample_file)
    if include_audio and audio_path and audio_path.exists():
        audio_bytes = audio_path.read_bytes()
        audio_filename = audio_path.name
        audio_content_type = guess_content_type(audio_path, "audio/mpeg")

    return ResolvedSampleInputs(
        transcript=transcript,
        sketch_bytes=sketch_bytes,
        sketch_content_type=sketch_content_type,
        audio_bytes=audio_bytes,
        audio_filename=audio_filename,
        audio_content_type=audio_content_type,
    )


async def evaluate(sample_path: Path, force_mock: bool, include_audio: bool = False) -> list[dict[str, object]]:
    settings = Settings(sketchvoice_mock=force_mock or Settings().use_mock)
    generator = SketchVoiceGenerator(settings)
    samples = json.loads(sample_path.read_text(encoding="utf-8"))
    results: list[dict[str, object]] = []

    for sample in samples:
        inputs = resolve_sample_inputs(sample, sample_file=sample_path, include_audio=include_audio)
        result = await generator.generate(
            sketch_bytes=inputs.sketch_bytes,
            sketch_content_type=inputs.sketch_content_type,
            audio_bytes=inputs.audio_bytes,
            audio_filename=inputs.audio_filename,
            audio_content_type=inputs.audio_content_type,
            transcript=inputs.transcript,
            direction=str(sample.get("expected_mermaid_direction") or sample.get("direction") or "LR"),
        )
        pred_nodes = {normalize_label(node.label) for node in result.graph.nodes}
        gold_nodes = {normalize_label(label) for label in sample["gold_nodes"]}
        id_to_label = {node.id: node.label for node in result.graph.nodes}
        pred_edges = {
            (normalize_label(id_to_label.get(edge.source, edge.source)), normalize_label(id_to_label.get(edge.target, edge.target)))
            for edge in result.graph.edges
        }
        gold_edges = {
            (normalize_label(source), normalize_label(target))
            for source, target in sample["gold_edges"]
        }
        node_scores = prf(pred_nodes, gold_nodes)
        edge_scores = prf(pred_edges, gold_edges)
        results.append(
            {
                "id": sample["id"],
                "node": node_scores,
                "edge": edge_scores,
                "timings_ms": result.timings_ms,
                "warnings": result.graph.warnings,
            }
        )
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="评测样例节点/边 F1 和耗时。")
    parser.add_argument("--samples", type=Path, default=Path("data/samples.json"))
    parser.add_argument("--mock", action="store_true", help="强制使用 mock 后端")
    parser.add_argument("--include-audio", action="store_true", help="传入样例音频；默认只使用 transcript 以避免额外 ASR 调用")
    args = parser.parse_args()
    results = asyncio.run(evaluate(args.samples, args.mock, include_audio=args.include_audio))
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
