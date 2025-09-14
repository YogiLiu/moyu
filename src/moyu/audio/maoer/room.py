import asyncio
from typing import Any

from pydantic import ValidationError, HttpUrl

from moyu.audio.base import AudioRoom, RoomStatus
from moyu.audio.errors import AudioError

from .models import RoomInfoApiRes, RoomInfoApiInfo


class MaoEr(AudioRoom):
    base_url = "https://fm.missevan.com/api/v2"

    __cached_info: RoomInfoApiInfo = None
    __cache_lock = asyncio.Lock()

    async def _get_info(self) -> RoomInfoApiInfo:
        res: dict[str, Any] = await self.get(f"/live/{self.id}")
        try:
            payload = RoomInfoApiRes.model_validate(res)
        except ValidationError as e:
            raise AudioError(f"Failed to get room info, error: {e}.")
        if payload.code != 0:
            raise AudioError(f"Failed to get room info, code: {payload.code}")
        return payload.info

    async def get_info(self) -> RoomInfoApiInfo:
        async with self.__cache_lock:
            if self.__cached_info is None:
                self.__cached_info = await self._get_info()
            return self.__cached_info

    async def get_owner(self) -> str:
        info = await self.get_info()
        return info.room.creator_username

    async def get_title(self) -> str:
        info = await self.get_info()
        return info.room.name

    async def get_status(self) -> RoomStatus:
        info = await self.get_info()
        if info.room.status.open == 1:
            return RoomStatus.ONLINE
        else:
            return RoomStatus.OFFLINE

    async def get_url(self) -> HttpUrl:
        info = await self.get_info()
        return info.room.channel.flv_pull_url
