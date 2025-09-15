from pathlib import Path
from typing import Annotated, Literal

from pydantic import BaseModel, Field
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
    PydanticBaseSettingsSource,
    TomlConfigSettingsSource,
)


_CONFIG_PATH = Path.home() / ".config" / "moyu" / "config.toml"

SupportedPlatform = Literal["maoer"]


class LiveAudioRoom(BaseModel):
    id: Annotated[str, Field(min_length=1, description="Audio room ID.")]
    platform: Annotated[
        SupportedPlatform, Field(description="Live audio room platform.")
    ]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(toml_file=_CONFIG_PATH)

    live_audio_rooms: Annotated[
        list[LiveAudioRoom],
        Field(default_factory=list, description="List of audio rooms."),
    ]

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (TomlConfigSettingsSource(settings_cls),)
