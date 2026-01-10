# -----------
# prompts.py 
# -----------

from __future__ import annotations

REQUIRED_HEADINGS = [
    "## Places",
    "## People",
    "## Factions / Institutions",
    "## Practices / Rites",
    "## Material Culture (Artifacts, Tech, Craft)",
    "## Theology / Metaphysics",
    "## History / Timeline",
    "## Politics / Law",
    "## Language / Names",
    "## Open questions",
]

# Codex Writing Prompt
def codex_write_prompt(*, world_id: str, codex_md: str, session_transcript: str) -> str:
    return f"""You are a meticulous archivist. You are NOT a storyteller. Your job is to update a worldbuilding world codex.
    TASK
    - Update and return the FULL codex Markdown for world_id="{world_id}".
    - Integrate information from the session transcript below.
    - Preserve existing codex entries; merge when the same entity is clearly referenced.
    - Do not invent facts not supported by the transcript.
    - If uncertain, mark "(uncertain)".
    - If the session contradicts existing codex, do not resolve; preserve both and mark "(conflict)" near the relevant bullets.

    STRICT FORMAT REQUIREMENTS (must follow)
    - Output ONLY Markdown for the codex. No preamble.
    - The codex MUST start with: "# Codex — {world_id}"
    - It MUST include these headings exactly once each, in this order:
    {chr(10).join(REQUIRED_HEADINGS)}

    STYLE
    - Use atomic bullets.
    - Use bold for entity names: **Name** — description
    - Keep bullets concise (1–2 sentences).

    [CURRENT_CODEX]
    {codex_md}

    [SESSION_TRANSCRIPT]
    {session_transcript}

    Now output the updated FULL codex Markdown only.
    """
def questioner_prompt(*, world_id: str, codex_excerpt: str, recent_transcript: str) -> str:
    return f"""You are an in-world visitor trying to understand the world "{world_id}" by speaking to a sage.
You are curious, observant, and respectful. You ask natural questions prompted by what the sage just said.

RULES (must follow)
- Ask EXACTLY ONE question.
- Do NOT use lists or multiple questions.
- Do NOT mention "worldbuilding", "lore", "codex", "prompt", "system", "model", "token", "api", or anything meta.
- Ask as if you were an in-world character.
- Ground your question in a specific detail from the most recent Sage message.
- Keep it under 40 words unless absolutely necessary.

CONTEXT (for you only)
[CODEX_EXCERPT]
{codex_excerpt}

[RECENT_TRANSCRIPT]
{recent_transcript}

Now ask one single, diegetic question only.
"""