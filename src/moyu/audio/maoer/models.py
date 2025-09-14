from typing import Annotated

from pydantic import BaseModel, Field, HttpUrl


class RoomInfoApiStatus(BaseModel):
    open: Annotated[int, Field(description="Open status.")]


class RoomInfoApiChannel(BaseModel):
    flv_pull_url: Annotated[HttpUrl, Field(description="FLV pull URL.")]
    hls_pull_url: Annotated[HttpUrl, Field(description="HLS pull URL.")]


class RoomInfoApiRoom(BaseModel):
    room_id: Annotated[int, Field(description="Room ID.")]
    name: Annotated[str, Field(description="Room name.")]
    creator_username: Annotated[str, Field(description="Creator username.")]
    status: Annotated[RoomInfoApiStatus, Field(description="Room status.")]
    channel: Annotated[RoomInfoApiChannel, Field(description="Room channel.")]


class RoomInfoApiInfo(BaseModel):
    room: Annotated[RoomInfoApiRoom, Field(description="Room information.")]


class RoomInfoApiRes(BaseModel):
    code: Annotated[int, Field(description="API status code.")]
    info: Annotated[RoomInfoApiInfo | str, Field(description="API payload.")]
