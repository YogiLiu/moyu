import typer

from moyu.config import Settings
from .base import AudioRoom, RoomStatus
from .errors import AudioError
from .maoer import MaoEr


async def run(settings: Settings):
    if not settings.audio_rooms:
        raise AudioError("No audio rooms found in config.")
    rooms: list[AudioRoom] = []
    for ar in settings.audio_rooms:
        match ar.platform:
            case "maoer":
                rooms.append(MaoEr(ar.id))
            case _:
                raise AudioError(f"Unsupported platform: '{ar.platform}'.")

    typer.echo("Available audio rooms:")
    for room in rooms:
        room_id = room.id
        owner = await room.get_owner()
        title = await room.get_title()
        status = await room.get_status()
        if status == RoomStatus.ONLINE:
            colored_id = typer.style(f"[{room_id}]", fg=typer.colors.GREEN)
        else:
            colored_id = typer.style(f"[{room_id}]", fg=typer.colors.RED)
        typer.echo(f"{colored_id}  {owner} / {title}")
    while True:
        choice = typer.prompt("Enter room ID to listen, or 'q' to exit")
        if choice.lower() == "q":
            typer.echo("Bye!")
            exit(0)
        for room in rooms:
            if room.id == choice:
                typer.clear()
                owner = await room.get_owner()
                typer.echo(f"🎶 Listening {owner}.")
                await room.play()
                typer.echo("Done.")
                break
        typer.secho(f"Invalid room ID: {choice}", fg=typer.colors.RED, err=True)
