from typing import Annotated, Generic, TypeVar

from pydantic import BaseModel, Field


T = TypeVar("T", bound=BaseModel)


class BiliRes(BaseModel, Generic[T]):
    code: Annotated[int, Field(description="API status code.")]
    message: Annotated[str, Field(description="API message.")]
    msg: Annotated[str, Field(description="API message.")]
    data: Annotated[T | dict, Field(description="API payload.")]


class RoomInfo(BaseModel):
    uid: Annotated[int, Field(description="User ID.")]
    live_status: Annotated[int, Field(description="Live status.")]
    title: Annotated[str, Field(description="Live title.")]


class MasterInfo(BaseModel):
    uname: Annotated[str, Field(description="User name.")]


class Master(BaseModel):
    info: Annotated[MasterInfo, Field(description="Master info.")]
