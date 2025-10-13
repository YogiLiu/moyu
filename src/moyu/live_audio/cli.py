import asyncio
from typing import Type

import typer

from moyu.config import Settings
from .base import LiveAudioRoom, RoomStatus
from .errors import LiveAudioError
from .maoer import MaoEr
from .bili.room import Bili


register_room_classes: list[Type[LiveAudioRoom]] = [
    MaoEr,
    Bili,
]


async def _fetch_room_info(room: LiveAudioRoom) -> tuple[str, str, RoomStatus]:
    owner = await room.get_owner()
    title = await room.get_title()
    status = await room.get_status()
    return owner, title, status


async def run(settings: Settings):
    if not settings.live_audio_rooms:
        raise LiveAudioError("No live_audio rooms found in config.")
    rooms: list[LiveAudioRoom] = []
    register_room_classes_map = dict()
    for room_cls in register_room_classes:
        register_room_classes_map[room_cls.platform] = room_cls
    for ar in settings.live_audio_rooms:
        room_cls = register_room_classes_map.get(ar.platform)
        if room_cls is None:
            raise LiveAudioError(f"Unsupported platform: '{ar.platform}'.")
        rooms.append(room_cls(ar.id))

    typer.echo("Available live_audio rooms:")
    fetch_room_tasks = []
    for room in rooms:
        fetch_room_tasks.append(asyncio.create_task(_fetch_room_info(room)))
    infos = await asyncio.gather(*fetch_room_tasks, return_exceptions=True)
    online_rooms: list[LiveAudioRoom] = []
    room_idx = 1
    for idx, info in enumerate(infos):
        room = rooms[idx]
        if isinstance(info, Exception):
            typer.secho(
                f"Failed to get room({room.platform}/{room.id}): {type(info).__name__}<'{info}'>",
                fg=typer.colors.RED,
                err=True,
            )
            continue
        else:
            owner, title, status = info
        if status == RoomStatus.ONLINE:
            colored_id = typer.style(f"[{room_idx}]", fg=typer.colors.GREEN)
            typer.echo(f"{colored_id} {room.platform.upper()} / {owner} / {title}")
            online_rooms.append(room)
            room_idx += 1
    while True:
        choice = typer.prompt("Enter index to listen, or 'q' to exit")
        if choice.lower() == "q":
            typer.echo("👋 Bye!")
            exit(0)
        if not choice.isdigit():
            typer.secho(f"Invalid room ID: {choice}", fg=typer.colors.RED, err=True)
            continue
        room_idx = int(choice)
        if room_idx < 1 or room_idx > len(online_rooms):
            typer.secho(f"Invalid room ID: {choice}", fg=typer.colors.RED, err=True)
            continue
        typer.clear()
        room = online_rooms[room_idx - 1]
        owner = await room.get_owner()
        typer.echo(f"🎶 Listening {room.platform} / {owner}.")
        await room.play()
        typer.echo("Done.")
        break
