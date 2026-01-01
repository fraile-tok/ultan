# -----------
# cli.py 
# -----------

# -----------
# Libraries & Imports
# -----------
from __future__ import annotations
from pathlib import Path 
from typing import Optional

import typer

from .storage import (
    create_world,
    create_session,
    load_codex,
    get_world_paths
)

# Declare App
app = typer.Typer(
    name = "ultan",
    help = " Ultan — terminal-first worldbuilding recorder.",
    no_args_is_help = True,
)

# Print Paths
def _print_paths(world_id: str) -> None:
    wp = get_world_paths(world_id)
    typer.echo(f"World ID:     {wp.world_id}")
    typer.echo(f"World dir:    {wp.world_dir}")
    typer.echo(f"Codex:        {wp.codex_path}")
    typer.echo(f"Sessions dir: {wp.sessions_dir}")
    
# App Commands
@app.command("world") # Creates and/or ensures world exists
def world_cmd(
    world_id: str = typer.Argument(..., help = "World ID (folder-friendly, spaces will be normalized)."),
) -> None:
    
    wp = create_world(world_id)
    typer.echo(f"World {world_id} is ready.")
    typer.echo()
    _print_paths(wp.world_id)

@app.command("new") # New session
def new_session_cmd(
    world_id: str = typer.Argument(..., help = "World identifier."),
) -> None:
    create_world(world_id)
    session_path = create_session(world_id)
    typer.echo("Session created.")
    typer.echo(f"{session_path}")

@app.command("codex") # Prints either Codex path or Codex contents
def codex_cmd(
        world_id: str = typer.Argument(..., help = "World identifier."),
        print_path: bool = typer.Option(
            True,
            "--path/--no-path",
            help = "Print path for the codex file (default: on)."
        ),
        show: bool = typer.Option(
            False,
            "--show",
            help = "Print the codex file.",
        ),
) -> None: 
    wp = create_world(world_id)
    if print_path:
        typer.echo(str("wp.codex_path"))
    if show:
        typer.echo()
        typer.echo(load_codex(world_id))

@app.command("paths") # Prints World Paths
def paths_cmd(
    world_id: str = typer.Argument(..., help = "World identifier."),
) -> None:
    create_world(world_id)
    _print_paths(world_id)

@app.command("latest") # Prints path to latest session for a given world
def latest_session_cmd(
    world_id: str = typer.Argument(..., help="World identifier."),
) -> None:
    wp = create_world(world_id)
    sessions = sorted(wp.sessions_dir.glob("*.md"))
    if not sessions:
        raise typer.Exit(code=1)
    typer.echo(str(sessions[-1]))

@app.command("tail") # Prints N lines of latest session log
def tail_cmd(
    world_id: str = typer.Argument(..., help="World identifier."),
    n: int = typer.Option(30, "--n", min=1, help="Number of lines to show from the latest session."),
) -> None:
    wp = create_world(world_id)
    sessions = sorted(wp.sessions_dir.glob("*.md"))
    if not sessions:
        typer.echo("No sessions found for this world.")
        raise typer.Exit(code=1)

    latest = sessions[-1]
    lines = latest.read_text(encoding="utf-8").splitlines()
    tail_lines = lines[-n:]
    typer.echo(f"# Tail of: {latest.name}")
    typer.echo("\n".join(tail_lines))

WORLDS_DIR = Path("worlds")

@app.command("worldlist") # Prints list of available worlds
def worldlist_cmd() -> None:
    if not WORLDS_DIR.exists():
        typer.echo("Worlds directory not found.")
        raise typer.Exit(code=1)
    
    worlds = sorted(
        p.name for p in WORLDS_DIR.iterdir()
        if p.is_dir()
    )

    if not worlds: 
        typer.echo("No worlds available.")
        return
    
    typer.echo("Available worlds:")
    for w in worlds:
        typer.echo(f"  - {w}")