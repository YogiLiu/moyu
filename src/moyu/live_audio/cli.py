import typer

from moyu.config import Settings
from .base import LiveAudioRoom, RoomStatus
from .errors import LiveAudioError
from .maoer import MaoEr


async def run(settings: Settings):
    if not settings.live_audio_rooms:
        raise LiveAudioError("No live_audio rooms found in config.")
    rooms: list[LiveAudioRoom] = []
    for ar in settings.live_audio_rooms:
        match ar.platform:
            case "maoer":
                rooms.append(MaoEr(ar.id))
            case _:
                raise LiveAudioError(f"Unsupported platform: '{ar.platform}'.")

    typer.echo("Available live_audio rooms:")
    for idx, room in enumerate(rooms):
        owner = await room.get_owner()
        title = await room.get_title()
        status = await room.get_status()
        if status == RoomStatus.ONLINE:
            colored_id = typer.style(f"[{idx}]", fg=typer.colors.GREEN)
        else:
            colored_id = typer.style(f"[{idx}]", fg=typer.colors.RED)
        typer.echo(f"{colored_id}  {owner} / {title}")
    while True:
        choice = typer.prompt("Enter room ID to listen, or 'q' to exit")
        if choice.lower() == "q":
            typer.echo("👋 Bye!")
            exit(0)
        if not choice.isdigit():
            typer.secho(f"Invalid room ID: {choice}", fg=typer.colors.RED, err=True)
            continue
        idx = int(choice)
        if idx < 0 or idx >= len(rooms):
            typer.secho(f"Invalid room ID: {choice}", fg=typer.colors.RED, err=True)
            continue
        typer.clear()
        room = rooms[idx]
        owner = await room.get_owner()
        typer.echo(f"🎶 Listening {owner}.")
        await room.play()
        typer.echo("Done.")
        break
