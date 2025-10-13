import asyncio
from typing import Type

from pydantic import HttpUrl, ValidationError, BaseModel

from moyu.live_audio.base import LiveAudioRoom, RoomStatus
from moyu.live_audio.errors import LiveAudioError
from .models import BiliRes, RoomInfo, Master


class Bili(LiveAudioRoom):
    platform = "bili"

    base_url = "https://api.live.bilibili.com"

    __info_sem = asyncio.Semaphore(2)
    __owner_sem = asyncio.Semaphore(2)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__cached_info: RoomInfo | None = None
        self.__cached_owner: Master | None = None
        self.__cache_info_lock = asyncio.Lock()
        self.__cache_owner_lock = asyncio.Lock()

    @staticmethod
    def _parse_bili_response(res: dict, model: Type[BaseModel], context: str):
        try:
            payload = model.model_validate(res)
        except ValidationError as e:
            raise LiveAudioError(f"Failed to get {context}, error: {e}.")
        if payload.code != 0:
            raise LiveAudioError(
                f"Failed to get {context}, code: {payload.code}, info: '{payload.message}'."
            )
        return payload.data

    async def _get_info(self) -> RoomInfo:
        async with self.__info_sem:
            res = await self.get(f"/room/v1/Room/get_info?room_id={self.id}")
            return self._parse_bili_response(
                res, BiliRes[RoomInfo], f"room({self.id}) info"
            )

    async def get_info(self) -> RoomInfo:
        async with self.__cache_info_lock:
            if self.__cached_info is None:
                self.__cached_info = await self._get_info()
            return self.__cached_info

    async def _get_owner(self) -> Master:
        async with self.__owner_sem:
            info = await self.get_info()
            res = await self.get(f"/live_user/v1/Master/info?uid={info.uid}")
            return self._parse_bili_response(
                res, BiliRes[Master], f"owner({self.id}) info"
            )

    async def get_owner(self) -> str:
        async with self.__cache_owner_lock:
            if self.__cached_owner is None:
                self.__cached_owner = await self._get_owner()
            return self.__cached_owner.info.uname

    async def get_title(self) -> str:
        info = await self.get_info()
        return info.title

    async def get_status(self) -> RoomStatus:
        info = await self.get_info()
        if info.live_status == 1:
            return RoomStatus.ONLINE
        return RoomStatus.OFFLINE

    async def get_url(self) -> HttpUrl:
        return HttpUrl(f"https://live.bilibili.com/{self.id}")
