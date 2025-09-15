import asyncio
from functools import partial

import typer

from .live_audio import run
from .config import Settings
from .errors import MoyuError

app = typer.Typer()

warning = partial(typer.secho, fg=typer.colors.YELLOW)
error = partial(typer.secho, fg=typer.colors.RED, err=True)


@app.command(help="Live audio rooms.")
def live_audio():
    # noinspection PyArgumentList
    settings = Settings()
    try:
        asyncio.run(run(settings))
    except KeyboardInterrupt:
        warning("Aborted!")
        exit(1)
    except MoyuError as e:
        error(str(e))
        exit(1)
    except Exception as e:
        error(f"Unexpected error: {e}")
        exit(1)
