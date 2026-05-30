from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager


ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = ROOT / "docs" / "research_eval_results.json"
FIG_DIR = ROOT / "report" / "figures"


METHODS = [
    ("sketch_only", "草图单模态"),
    ("speech_only", "语音单模态"),
    ("early_fusion", "早期融合"),
    ("greedy_repair", "贪心修复"),
    ("mmsb_graph", "MMSB-Graph"),
]

PALETTE = {
    "sketch_only": "#486A86",
    "speech_only": "#8A6F3D",
    "early_fusion": "#2F7D6D",
    "greedy_repair": "#9B5A4A",
    "mmsb_graph": "#1F2937",
    "intro": "#4C78A8",
    "intermediate": "#59A14F",
    "advanced": "#B07AA1",
}


def configure_style() -> None:
    """配置适合论文插图的字体、线宽和导出参数。"""

    candidates = [
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/simsun.ttc",
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            font_manager.fontManager.addfont(path)
            mpl.rcParams["font.family"] = font_manager.FontProperties(fname=path).get_name()
            break
    mpl.rcParams.update(
        {
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "axes.linewidth": 0.75,
            "axes.edgecolor": "#222222",
            "axes.labelcolor": "#222222",
            "xtick.color": "#333333",
            "ytick.color": "#333333",
            "font.size": 9.5,
            "axes.titlesize": 10.5,
            "axes.labelsize": 9.5,
            "legend.fontsize": 8.5,
            "axes.unicode_minus": False,
        }
    )


def load_results() -> dict[str, Any]:
    return json.loads(RESULT_PATH.read_text(encoding="utf-8"))


def metric_series(payload: dict[str, Any], method: str, metric: str) -> np.ndarray:
    return np.asarray([sample["metrics"][method][metric] for sample in payload["samples"]], dtype=float)


def gaussian_smooth(values: np.ndarray, sigma: float = 1.15) -> np.ndarray:
    """用轻量高斯核平滑直方图，避免额外引入 scipy。"""

    radius = int(math.ceil(3 * sigma))
    xs = np.arange(-radius, radius + 1)
    kernel = np.exp(-(xs**2) / (2 * sigma**2))
    kernel = kernel / kernel.sum()
    return np.convolve(values, kernel, mode="same")


def draw_phase_portrait(ax: mpl.axes.Axes, aggregate: dict[str, dict[str, float]]) -> None:
    xs = [aggregate[key]["manual_edit_cost"] for key, _ in METHODS]
    ys = [aggregate[key]["edge_f1"] for key, _ in METHODS]
    ged = [aggregate[key]["normalized_ged"] for key, _ in METHODS]
    # Keep nearby aggregate points readable without changing the source metrics.
    visual_offsets = {
        "speech_only": (0.18, -0.006),
        "early_fusion": (-0.18, 0.008),
    }
    plot_xs = [
        x + visual_offsets.get(key, (0.0, 0.0))[0]
        for (key, _), x in zip(METHODS, xs, strict=True)
    ]
    plot_ys = [
        y + visual_offsets.get(key, (0.0, 0.0))[1]
        for (key, _), y in zip(METHODS, ys, strict=True)
    ]

    ax.plot(plot_xs, plot_ys, color="#30343F", linewidth=1.1, alpha=0.55, zorder=1)
    for i in range(len(plot_xs) - 1):
        ax.annotate(
            "",
            xy=(plot_xs[i + 1], plot_ys[i + 1]),
            xytext=(plot_xs[i], plot_ys[i]),
            arrowprops=dict(arrowstyle="->", color="#30343F", lw=1.0, alpha=0.7),
        )

    label_offsets = {
        "sketch_only": (0.25, 0.035),
        "speech_only": (0.72, 0.046),
        "early_fusion": (-0.72, -0.044),
        "greedy_repair": (-0.02, -0.055),
        "mmsb_graph": (0.28, -0.055),
    }
    for (key, label), x, y, g in zip(METHODS, plot_xs, plot_ys, ged, strict=True):
        size = 95 + 520 * g
        ax.scatter(x, y, s=size, color=PALETTE[key], alpha=0.18, edgecolor="none", zorder=2)
        ax.scatter(x, y, s=42, color=PALETTE[key], edgecolor="white", linewidth=0.7, zorder=3)
        offset_x, offset_y = label_offsets[key]
        ax.text(x + offset_x, y + offset_y, label, ha="center", va="center", fontsize=8.2, color="#1F2937")

    ax.set_xlim(10.2, -0.7)
    ax.set_ylim(0.32, 1.05)
    ax.set_xlabel("人工修改成本（越低越好）")
    ax.set_ylabel("边 F1（越高越好）")
    ax.set_title("A  结构恢复相图")
    ax.grid(True, color="#D7D2C8", linewidth=0.55, alpha=0.65)
    ax.text(0.02, 0.04, "圆晕面积编码 GED", transform=ax.transAxes, fontsize=8, color="#6B7280")


def draw_ged_ridges(ax: mpl.axes.Axes, payload: dict[str, Any]) -> None:
    bins = np.linspace(0, 0.82, 42)
    centers = (bins[:-1] + bins[1:]) / 2
    y_positions = np.arange(len(METHODS))[::-1]
    for y, (key, label) in zip(y_positions, METHODS, strict=True):
        values = metric_series(payload, key, "normalized_ged")
        hist, _ = np.histogram(values, bins=bins, density=True)
        density = gaussian_smooth(hist)
        if density.max() > 0:
            density = density / density.max() * 0.62
        baseline = np.full_like(centers, y, dtype=float)
        ax.fill_between(centers, baseline, baseline + density, color=PALETTE[key], alpha=0.34, linewidth=0)
        ax.plot(centers, baseline + density, color=PALETTE[key], linewidth=1.2)
        ax.scatter(values, np.full_like(values, y - 0.05), s=7, color=PALETTE[key], alpha=0.45, linewidth=0)
        ax.text(-0.045, y + 0.23, label, ha="right", va="center", fontsize=8.3, color="#1F2937")

    ax.set_xlim(-0.02, 0.82)
    ax.set_ylim(-0.45, len(METHODS) - 0.05)
    ax.set_xlabel("归一化图编辑距离")
    ax.set_yticks([])
    ax.set_title("B  图结构误差分布")
    ax.grid(True, axis="x", color="#D7D2C8", linewidth=0.55, alpha=0.65)
    for spine in ["left", "right", "top"]:
        ax.spines[spine].set_visible(False)


def draw_bridge_load(ax: mpl.axes.Axes, payload: dict[str, Any]) -> None:
    early_ged = metric_series(payload, "early_fusion", "normalized_ged")
    steps = metric_series(payload, "mmsb_graph", "bridge_steps")
    energy = metric_series(payload, "mmsb_graph", "path_energy")
    difficulties = [sample["difficulty"] for sample in payload["samples"]]

    for difficulty, display in [
        ("intro", "基础"),
        ("intermediate", "中等"),
        ("advanced", "复杂"),
    ]:
        mask = np.asarray([item == difficulty for item in difficulties])
        ax.scatter(
            early_ged[mask],
            steps[mask],
            s=55 + 65 * energy[mask],
            color=PALETTE[difficulty],
            alpha=0.72,
            edgecolor="white",
            linewidth=0.65,
            label=display,
        )

    coef = np.polyfit(early_ged, steps, deg=1)
    xs = np.linspace(max(0, early_ged.min() - 0.03), early_ged.max() + 0.03, 100)
    ax.plot(xs, coef[0] * xs + coef[1], color="#1F2937", linewidth=1.2, linestyle=(0, (3, 2)))
    corr = float(np.corrcoef(early_ged, steps)[0, 1])
    ax.text(0.04, 0.93, f"r = {corr:.2f}", transform=ax.transAxes, fontsize=8.5, color="#374151")

    ax.set_xlabel("早期融合图 GED")
    ax.set_ylabel("桥编辑步数")
    ax.set_title("C  桥负载诊断")
    ax.grid(True, color="#D7D2C8", linewidth=0.55, alpha=0.65)
    ax.legend(frameon=False, loc="lower right")


def create_diagnostic_figure(payload: dict[str, Any]) -> None:
    """生成三联诊断图，突出恢复路径、误差分布和桥负载。"""

    FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig = plt.figure(figsize=(11.6, 4.25), constrained_layout=True)
    gs = fig.add_gridspec(1, 3, width_ratios=[1.08, 1.02, 1.05])
    axes = [fig.add_subplot(gs[0, i]) for i in range(3)]
    fig.patch.set_facecolor("#FFFFFF")
    for ax in axes:
        ax.set_facecolor("#FFFFFF")

    draw_phase_portrait(axes[0], payload["aggregate"])
    draw_ged_ridges(axes[1], payload)
    draw_bridge_load(axes[2], payload)

    for ax in axes:
        ax.tick_params(length=3, width=0.65)
    fig.savefig(FIG_DIR / "mmsb_diagnostics.pdf", bbox_inches="tight")
    fig.savefig(FIG_DIR / "mmsb_diagnostics.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    configure_style()
    payload = load_results()
    create_diagnostic_figure(payload)
    print(json.dumps({"figure": str(FIG_DIR / "mmsb_diagnostics.pdf")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
