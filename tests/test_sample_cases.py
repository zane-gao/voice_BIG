from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.evaluate_samples import evaluate, resolve_sample_inputs
from scripts.generate_test_cases import CASE_DEFINITIONS, write_case_assets


def test_case_definitions_cover_requested_topics() -> None:
    assert set(CASE_DEFINITIONS) == {
        "cnn_explainer",
        "diffusion_roadmap",
        "video_generation_timeline",
    }
    for case in CASE_DEFINITIONS.values():
        assert case.transcript
        assert len(case.gold_nodes) >= 8
        assert len(case.gold_edges) >= 6
        assert case.direction in {"LR", "TD"}


def test_write_mock_case_creates_valid_assets(tmp_path: Path) -> None:
    record = asyncio.run(
        write_case_assets(
            CASE_DEFINITIONS["cnn_explainer"],
            output_root=tmp_path,
            mock=True,
            force=True,
            tts_provider="openai",
        )
    )

    sketch_path = tmp_path / "cnn_explainer" / "sketch.png"
    audio_path = Path(record["audio_path"])
    transcript_path = tmp_path / "cnn_explainer" / "transcript.txt"
    gold_path = tmp_path / "cnn_explainer" / "gold.json"

    assert record["id"] == "cnn_explainer"
    assert record["sketch_path"] == str(sketch_path)
    assert audio_path.suffix in {".mp3", ".wav"}
    Image.open(sketch_path).verify()
    assert audio_path.stat().st_size > 0
    assert "卷积" in transcript_path.read_text(encoding="utf-8")
    gold = json.loads(gold_path.read_text(encoding="utf-8"))
    assert gold["gold_nodes"] == record["gold_nodes"]


def test_resolve_sample_inputs_prefers_external_files(tmp_path: Path) -> None:
    sketch_path = tmp_path / "sketch.png"
    audio_path = tmp_path / "speech.mp3"
    transcript_path = tmp_path / "transcript.txt"
    Image.new("RGB", (32, 32), "white").save(sketch_path)
    audio_path.write_bytes(b"ID3\x03\x00\x00\x00\x00\x00\x00")
    transcript_path.write_text("外部 transcript 文本", encoding="utf-8")

    sample = {
        "id": "external",
        "transcript": "内联文本",
        "transcript_path": str(transcript_path),
        "sketch_path": str(sketch_path),
        "audio_path": str(audio_path),
    }
    inputs = resolve_sample_inputs(sample, sample_file=tmp_path / "samples.json", include_audio=True)

    assert inputs.transcript == "外部 transcript 文本"
    assert inputs.sketch_bytes
    assert inputs.sketch_content_type == "image/png"
    assert inputs.audio_bytes == audio_path.read_bytes()
    assert inputs.audio_filename == "speech.mp3"
    assert inputs.audio_content_type == "audio/mpeg"


def test_mock_evaluation_handles_new_topic_case(tmp_path: Path) -> None:
    case = CASE_DEFINITIONS["diffusion_roadmap"]
    sample_path = tmp_path / "samples.json"
    sample_path.write_text(
        json.dumps(
            [
                {
                    "id": case.id,
                    "transcript": case.transcript,
                    "gold_nodes": case.gold_nodes,
                    "gold_edges": case.gold_edges,
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    result = asyncio.run(evaluate(sample_path, force_mock=True))[0]

    assert result["node"]["f1"] == 1.0
    assert result["edge"]["f1"] == 1.0
