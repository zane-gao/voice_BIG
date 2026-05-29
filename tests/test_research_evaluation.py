from __future__ import annotations

import json
import subprocess
from pathlib import Path


def test_evaluate_research_cases_outputs_mmsb_metrics(tmp_path: Path) -> None:
    output_path = tmp_path / "research_eval.json"

    subprocess.run(
        [
            "uv",
            "run",
            "python",
            "scripts/evaluate_research_cases.py",
            "--samples",
            "data/research_samples.json",
            "--limit",
            "3",
            "--output",
            str(output_path),
        ],
        check=True,
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))

    assert payload["sample_count"] == 3
    assert "mmsb_graph" in payload["aggregate"]
    assert payload["aggregate"]["mmsb_graph"]["normalized_ged"] == 0
    assert payload["aggregate"]["sketch_only"]["normalized_ged"] > 0
    assert payload["aggregate"]["mmsb_graph"]["path_energy"] > 0
