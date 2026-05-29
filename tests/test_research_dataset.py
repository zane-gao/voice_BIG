from __future__ import annotations

import json
from pathlib import Path


def test_research_dataset_has_required_small_sample_assets() -> None:
    manifest_path = Path("data/research_samples.json")

    samples = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert 20 <= len(samples) <= 30
    required_files = ["sketch_path", "audio_path", "transcript_path", "gold_path", "gold_mermaid_path", "gold_render_path"]
    for sample in samples:
        for key in required_files:
            path = Path(sample[key])
            assert path.exists(), f"{sample['id']} 缺少 {key}: {path}"

        gold = json.loads(Path(sample["gold_path"]).read_text(encoding="utf-8"))
        for key in ["node_spans", "speech_anchors", "sketch_regions", "layout", "difficulty"]:
            assert key in gold, f"{sample['id']} 缺少研究标注字段 {key}"

        assert len(gold["gold_nodes"]) >= 4
        assert len(gold["gold_edges"]) >= 3
