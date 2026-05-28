from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """集中管理运行配置，避免把密钥泄露到前端或日志。"""

    openai_api_key: str | None = Field(default=None, validation_alias="OPENAI_API_KEY")
    openai_base_url: str | None = Field(default=None, validation_alias="OPENAI_BASE_URL")
    openai_transcribe_model: str = Field(
        default="gpt-4o-mini-transcribe", validation_alias="OPENAI_TRANSCRIBE_MODEL"
    )
    openai_graph_model: str = Field(default="gpt-5.5", validation_alias="OPENAI_GRAPH_MODEL")
    openai_final_image_model: str = Field(default="gpt-image-2", validation_alias="OPENAI_FINAL_IMAGE_MODEL")
    openai_tts_model: str = Field(default="gpt-4o-mini-tts", validation_alias="OPENAI_TTS_MODEL")
    openai_tts_voice: str = Field(default="coral", validation_alias="OPENAI_TTS_VOICE")
    openai_fallback_to_mock: bool = Field(default=True, validation_alias="OPENAI_FALLBACK_TO_MOCK")
    ark_api_key: str | None = Field(default=None, validation_alias="ARK_API_KEY")
    ark_image_base_url: str = Field(
        default="https://ark.cn-beijing.volces.com/api/v3",
        validation_alias="ARK_IMAGE_BASE_URL",
    )
    doubao_draft_image_model: str = Field(
        default="doubao-seedream-5-0-lite-260128",
        validation_alias="DOUBAO_DRAFT_IMAGE_MODEL",
    )
    doubao_draft_size: str = Field(default="2K", validation_alias="DOUBAO_DRAFT_SIZE")
    sample_tts_provider: str = Field(default="openai", validation_alias="SAMPLE_TTS_PROVIDER")
    doubao_tts_model: str = Field(default="doubao-seed-2-0-pro-260215", validation_alias="DOUBAO_TTS_MODEL")
    doubao_tts_voice: str = Field(default="zh_female_kailangjiejie_moon_bigtts", validation_alias="DOUBAO_TTS_VOICE")
    image_fallback_to_mock: bool = Field(default=True, validation_alias="IMAGE_FALLBACK_TO_MOCK")
    sketchvoice_mock: bool = Field(default=False, validation_alias="SKETCHVOICE_MOCK")
    max_audio_mb: int = Field(default=25, validation_alias="MAX_AUDIO_MB")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    @property
    def use_mock(self) -> bool:
        return self.sketchvoice_mock or not bool(self.openai_api_key)

    @property
    def image_mock(self) -> bool:
        return self.sketchvoice_mock
