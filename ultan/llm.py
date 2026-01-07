# -----------
# llm.py 
# -----------

# -----------
# Libraries & Imports
# -----------
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from openai import OpenAI

@dataclass(frozen=True)
class LLMConfig:
    model: str
    timeout_s: float

def load_config() -> LLMConfig:
    model = os.getenv("ULTAN_MODEL", "gpt-5-mini")
    timeout_s = float(os.getenv("ULTAN_TIMEOUT_S", "60"))
    return LLMConfig(model=model, timeout_s=timeout_s)

def _client(timeout_s: float) -> OpenAI:
    return OpenAI(timeout=timeout_s)

def generate(prompt: str, *, model: Optional[str] = None) -> str:
    cfg = load_config()
    use_model = model or cfg.model

    client = _client(cfg.timeout_s)
    resp = client.responses.create(
        model=use_model,
        input=prompt
    )

    return resp.output_text or ""