from sketchvoice.config import Settings


def test_openai_base_url_accepts_gateway_root() -> None:
    settings = Settings(openai_base_url="https://gmn.chuangzuoli.com")

    assert settings.openai_client_base_url == "https://gmn.chuangzuoli.com/v1"
    assert settings.openai_image_client_base_url == "https://gmn.chuangzuoli.com/v1"


def test_openai_base_url_keeps_explicit_v1() -> None:
    settings = Settings(
        openai_base_url="https://gmn.chuangzuoli.com/v1",
        openai_image_base_url="https://image.example/v1",
    )

    assert settings.openai_client_base_url == "https://gmn.chuangzuoli.com/v1"
    assert settings.openai_image_client_base_url == "https://image.example/v1"
