# -----------
# engine.py 
# -----------

from __future__ import annotations
from dataclasses import dataclass
from patlib import Path
from typing import Optional

from .llm import generate, load_config
from .prompts import codex_write_prompt, question_prompt, REQUIRED_HEADINGS
from .storage import (
    create_world,
    load_codex,
    save_codex,
    append_transcript,
    read_recent_transcript
)
from .validators import validate_question, validate_codex

@dataclass(frozen=True)
class EngineConfig:
    transcript_turn_window: int = 8
    codex_excerpt_chars: int = 3000
    max_question_retries: int = 2

def _codex_excerpt(codex_md: str, max_chars: int) -> str:
    t = (codex_md or "").strip()
    return t if len(t) <= max_chars else (t[:max_chars] + "\n…")


# Turn Logic
def process_turn(*, world_id: str, session_path: Path, user_text: str, cfg: Optional[EngineConfig] = None) -> str:
    cfg = cfg or EngineConfig()

    append_transcript(session_path, "Sage", user_text)

    create_world(world_id)
    codex = load_codex(world_id)
    recent = read_recent_transcript(session_path, n_turns=cfg.transcript_turn_window)
    excerpt = _codex_excerpt(codex, cfg.codex_excerpt_chars)

    qp = question_prompt(world_id=world_id, codex_excerpt=excerpt, recent_transcript=recent)
    question = generate(qp).strip()

    for _ in range(cfg.max_question_retries):
        ok, _reason = validate_question(question)
        if ok:
            break
        reprompt = qp + "\n\nSTRICT REMINDER: Output only one single question ending with '?'. No other text."
        question = generate(reprompt).strip()

    append_transcript(session_path, "AI", question)
    return question

def finalize_codex_from_session(*, world_id: str, session_path: Path, model: Optional[str] = None) -> Path:
    create_world(world_id)
    codex = load_codex(world_id)
    transcript = session_path.read_text(encoding="utf-8")

    prompt = codex_write_prompt(world_id=world_id, codex_md=codex, session_transcript=transcript)

    updated = generate(prompt, model=model).strip()

    ok, reason = validate_codex(updated, world_id=world_id, required_headings=REQUIRED_HEADINGS)
    if ok:
        save_codex(world_id, updated)
        return (session_path.parent.parent / "codex.md")
    
    dump = session_path.with_suffix(".codex_write_failed.md")
    dump.write_text(updated, encoding="utf-8")
    return dump
