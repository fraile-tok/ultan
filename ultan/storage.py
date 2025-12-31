# -----------
# storage.py 
# -----------

# -----------
# Libraries & Imports
# -----------
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path 
from typing import Optional, List
import re

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

def get_repo_root(start: Optional[Path] = None) -> Path:
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
@dataclass(frozen = True)
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

# -----------
# Codex Loading & Saving
# -----------

def load_codex(world_id: str, repo_root: Optional[Path] = None) -> str:
    wp = create_world(world_id, repo_root = repo_root)
    return wp.codex_path.read_text(encoding="utf-8")

def save_codex(world_id: str, codex_md: str, repo_root: Optional[Path] = None) -> None:
    wp = create_world(world_id, repo_root = repo_root)
    atomic_write_text(wp.codex_path, codex_md)

# -----------
# Session Handling
# -----------

def _next_session_filename(sessions_dir: Path, date_prefix: str) -> str:
    existing = sorted(sessions_dir.glob(f"{date_prefix}_*.md"))

    max_n = 0
    for p in existing:
        m = re.match(rf"^{re.escape(date_prefix)}_(\d{{2}})\.md$", p.name)
        if m:
            max_n = max(max_n, int(m.group(1)))
    return f"{date_prefix}_{max_n + 1:02d}.md"


def create_session(world_id: str, repo_root: Optional[Path] = None) -> Path:
    wp = create_world(world_id, repo_root = repo_root)

    date_prefix = now_local().strftime("%Y-%m-%d")
    filename = _next_session_filename(wp.sessions_dir, date_prefix)
    session_path = wp.sessions_dir / filename

    session_id = filename.replace(".md", "")
    text = DEFAULT_SESSION_TEMPLATE.format(session_id = session_id, world_id = wp.world_id)
    atomic_write_text(session_path, text)
    return session_path

def append_transcript(session_path: Path, speaker: str, text: str) -> None:
    session_path = session_path.resolve()
    if not session_path.exists():
        raise FileNotFoundError(f"Session file not found: {session_path}")
    
    speaker = (speaker or "").strip()
    if not speaker:
        speaker = "Anonymous"

    clean = (text or "").rstrip()

    line = f"**{speaker}:** {clean}\n"
    with session_path.open("a", encoding="utf-8") as f:
        f.write(line)

def read_recent_transcript(session_path: Path, n_turns: int = 6) -> str:
    session_path = session_path.resolve()
    if not session_path.exists():
        raise FileNotFoundError(f"Session file not found: {session_path}")
    
    lines = session_path.read_text(encoding="uft-8").splitlines()
    transcript_lines: List[str] = [ln for ln in lines if ln.startswith("**") and ":** " in ln]
    return "\n".join(transcript_lines[-max(n_turns, 0):])    
