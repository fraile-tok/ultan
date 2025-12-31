# -----------
# storage.py 
# -----------

# -----------
# Libraries
# -----------
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path 
from typing import Optional, List

# -----------
# Templates/Defaults
# -----------

DEFAULT_CODEX_TEMPLATE = """# Codex — {world_id}

## Places

## People

## Factions / Institutions

## Practices / Rites

## Material Culture (Artifacts, Tech, Craft)

## Theology / Metaphysics

## History / Timeline

## Politics / Law

## Language / Names

## Open questions
"""

DEFAULT_SESSION_TEMPLATE = """# Session: {session_id}
World: {world_id}

## Transcript
"""

# -----------
# Helpers
# -----------
_slug_re = re.compile(r" [^a-z0-9]")

def slugify(to_be_slug: str) -> str:
    s = (to_be_slug or "").strip().lower().replace(" ", "-")
    s = _slug_re.sub("", s)
    return s

def now_local() -> datetime:
    return datetime.now()

def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)

def get_repo_root(start: Optional[Path] = none) -> Path:
    start = (start or Path.cwd()).resolve()
    for p in [start, *start.parents]:
        if (p / "worlds").exists():
            return p
    return start

def atomic_write_text(path: Path, text: str, encoding: str = "utf-8") -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding=encoding)
    tmp.replace(path)

# -----------
# World Paths
# -----------
@dataclass(froze = True)
class WorldPaths:
    root: Path
    world_id: str
    world_dir: Path
    codex_path: Path
    sessions_dir: Path

def get_world_paths(world_id: str, repo_root: Optional[Path] = None) -> WorldPaths:
    repo = (repo_root or get_repo_root()).resolve()
    safe_id = slugify(world_id)
    world_dir = repo / "worlds" / safe_id
    codex_path = world_dir / "codex.md"
    sessions_dir = world_dir / "sessions"

    return WorldPaths(
        root = repo,
        world_id = safe_id,
        world_dir = world_dir,
        codex_path = codex_path,
        sessions_dir = sessions_dir,
    )

# -----------
# World Creation
# -----------

def create_world(world_id: str, repo_root: Optional[Path] = None) -> WorldPaths:
    wp = get_world_paths(world_id, repo_root = repo_root)
    ensure_dir(wp.world_dir)
    ensure_dir(wp.sessions_dir)

    if not wp.codex_path.exists():
        codex = DEFAULT_CODEX_TEMPLATE.format(world_id = wp.world_id)
        atomic_write_text(wp.codex_path, codex)

    return wp