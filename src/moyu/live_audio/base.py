import aiohttp
import asyncio
from abc import ABCMeta, abstractmethod
from enum import IntEnum
from typing import Any, ClassVar

import mpv
from pydantic import HttpUrl

from moyu.config import SupportedPlatform
from .errors import LiveAudioError, ApiTimeoutError


class RoomStatus(IntEnum):
    OFFLINE = 0
    ONLINE = 1


class LiveAudioRoom(aiohttp.ClientSession, metaclass=ABCMeta):
    platform: ClassVar[SupportedPlatform]
    base_url: ClassVar[str] = ""

    default_headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:142.0) Gecko/20100101 Firefox/142.0",
        "Accept-Encoding": "gzip",
        "Connection": "keep-alive",
    }

    timeout = aiohttp.ClientTimeout(total=60)

    def __init__(self, room_id: str, **kwargs):
        base_url = self.base_url.rstrip("/") + "/"
        super().__init__(
            base_url=base_url, headers=self.default_headers, timeout=self.timeout
        )
        self._id = room_id
        self._extra_config: dict[str, Any] = kwargs
        self._player = mpv.MPV(ytdl=True, video=False)

    async def request(self, *args, **kwargs):
        try:
            return await super().request(*args, **kwargs)
        except asyncio.TimeoutError as e:
            raise ApiTimeoutError(f"Api time out: {e.__class__.__name__}") from e

    @abstractmethod
    async def get_owner(self) -> str:
        raise NotImplementedError

    @abstractmethod
    async def get_title(self) -> str:
        raise NotImplementedError

    @abstractmethod
    async def get_status(self) -> RoomStatus:
        raise NotImplementedError

    @abstractmethod
    async def get_url(self) -> HttpUrl:
        raise NotImplementedError

    @property
    def id(self) -> str:
        return self._id

    @property
    def extra_config(self) -> dict[str, Any]:
        return self._extra_config

    async def play(self) -> None:
        url = await self.get_url()
        await asyncio.to_thread(self._player.play, str(url))
        try:
            await asyncio.to_thread(self._player.wait_for_playback)
        except mpv.ShutdownError as e:
            raise LiveAudioError(f"Player shutdown unexpectedly: {e}.")
        except asyncio.CancelledError:
            self._player.stop()
            raise

    def __str__(self) -> str:
        return f"<{self.__class__.__name__} id='{self._id}'>"
