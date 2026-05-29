from pathlib import Path


STATIC_DIR = Path(__file__).resolve().parents[1] / "src" / "sketchvoice" / "static"


def test_image_tab_contains_narration_controls() -> None:
    html = (STATIC_DIR / "index.html").read_text(encoding="utf-8")

    # 这些 ID 是前端讲解工作流的稳定锚点，避免后续改版时悄悄丢控件。
    for element_id in (
        "narrationProvider",
        "narrationVoice",
        "narrationCustomVoiceId",
        "generateNarrationBtn",
        "narrationAudio",
        "narrationCursor",
        "downloadNarrationVideo",
    ):
        assert f'id="{element_id}"' in html


def test_app_js_contains_narration_workflow_hooks() -> None:
    script = (STATIC_DIR / "app.js").read_text(encoding="utf-8")

    for hook in (
        "generateNarration",
        "updateNarrationCursor",
        "downloadNarrationVideo",
        "recordNarrationVideo",
    ):
        assert hook in script
