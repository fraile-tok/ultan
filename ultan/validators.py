# -----------
# validators.py 
# -----------

from __future__ import annotations
from typing import Tuple, List

META_BANNED = [
    "worldbuilding", "codex", "prompt", "model", "token", "api", "openai",
]

def validate_question(text: str) -> Tuple[bool, str]:
    t = (text or "").strip()

    if not t:
        return False, "empty"
    
    lower = t.lower()

    for w in META_BANNED:
        if w in lower:
             return False, f"meta word: {w}"
    
    if any(line.strip().startswith(("-", "*")) for line in t.splitlines()):
        return False, "list formatting"
    if t.count("?") != 1:
        return False, "must contain exactly one '?'"
    if not t.endswith("?"):
        return False, "must end with '?'"
    return True, "ok"

def validate_codex(codex_md: str, *, world_id: str, required_headings: List[str]) -> Tuple[bool,str]:
    t = (codex_md or "").strip()

    if not t.startswith(f"# Codex — {world_id}"):
        return False, "missing title"
    for h in required_headings:
        if t.count(h) != 1:
            return False, f"heading missing/duplicated: {h}"
        
    if "STRICT FORMAT REQUIREMENTS" in t or "You are a meticulous archivist" in t:
        return False, "looks like echoed instructions"
    return True, "ok"