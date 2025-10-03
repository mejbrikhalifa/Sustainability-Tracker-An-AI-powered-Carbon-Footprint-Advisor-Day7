#!/usr/bin/env python3
"""Apply Day 6 priority 1 & 2 improvements to ai_tips.py.
- Add jittered backoff and negative cache
- Sanitize inputs for stable cache keys
- Limit breakdown list lengths
- Sanitize tip outputs
Idempotent: safe to run multiple times.
"""
from __future__ import annotations
import io
import os
import re
from pathlib import Path

ROOT = Path(r"c:\Disc D\Zied Guizani\Windsurf3")
TARGET = ROOT / "ai_tips.py"

if not TARGET.exists():
    raise SystemExit(f"ai_tips.py not found at {TARGET}")

text = TARGET.read_text(encoding="utf-8")
orig = text

# 1) Ensure imports: random, re
if "import random" not in text:
    # add after openai import line
    text = re.sub(r"(from openai import OpenAI, OpenAIError\s*\n)", r"\1import random\n", text, count=1)
if re.search(r"(^|\n)import re(\n|$)", text) is None:
    # place re near top after random
    text = re.sub(r"(import random\s*\n)", r"\1import re\n", text, count=1)

# 2) Negative cache constants after LAST_TIP_SOURCE
if "_NEG_CACHE" not in text:
    text = re.sub(
        r"(LAST_TIP_SOURCE\s*=\s*\"unknown\"\s*\n)",
        r"\1\n# Short-lived negative cache for failing GPT calls to prevent repeated hits\n_NEG_CACHE: dict[str, float] = {}\n_NEG_TTL_SECONDS = 60.0\n",
        text,
        count=1,
    )

# 3) Allowed keys and input sanitizer after CATEGORY_MAP block
if "ALLOWED_KEYS = {" not in text:
    text = re.sub(
        r"(CATEGORY_MAP\s*=\s*\{[\s\S]*?\n\}\s*)",
        r"\1\n# Allowed activity keys for sanitization\nALLOWED_KEYS = {k for keys in CATEGORY_MAP.values() for k in keys}\n\n"
        r"def _sanitize_inputs_for_prompt(user_data: dict) -> dict:\n"
        r"    \"\"\"Return a sanitized dict limited to allowed numeric non-negative floats, clamped to thresholds.\"\"\"\n"
        r"    if not isinstance(user_data, dict):\n"
        r"        return {}\n"
        r"    out = {}\n"
        r"    for k, v in user_data.items():\n"
        r"        if k not in ALLOWED_KEYS:\n"
        r"            continue\n"
        r"        try:\n"
        r"            f = float(v or 0)\n"
        r"        except Exception:\n"
        r"            continue\n"
        r"        if f < 0:\n"
        r"            f = 0.0\n"
        r"        thr = EXTREME_THRESHOLDS.get(k)\n"
        r"        if isinstance(thr, (int, float)) and f > float(thr):\n"
        r"            f = float(thr)\n"
        r"        out[k] = f\n"
        r"    return out\n\n",
        text,
        count=1,
    )

# 4) Limit breakdown lists to top-5 items
text = re.sub(
    r"for k, kg in sorted\(activity_kg\.items\(\), key=lambda x: x\[1\], reverse=True\):",
    r"for k, kg in sorted(activity_kg.items(), key=lambda x: x[1], reverse=True)[:5]:",
    text,
)
text = re.sub(
    r"for cat, val in sorted\(cat_totals\.items\(\), key=lambda x: x\[1\], reverse=True\):",
    r"for cat, val in sorted(cat_totals.items(), key=lambda x: x[1], reverse=True)[:5]:",
    text,
)

# 5) Use sanitized inputs in generate_eco_tip
if "safe_inputs = _sanitize_inputs_for_prompt(user_data)" not in text:
    text = re.sub(
        r"(def generate_eco_tip\(user_data: dict, emissions: float\) -> str:\n[\s\S]*?global LAST_TIP_SOURCE\s*\n)",
        r"\1    # Sanitize inputs for prompting/caching and handle ambiguous/noisy inputs up front\n    safe_inputs = _sanitize_inputs_for_prompt(user_data)\n",
        text,
        count=1,
    )
# has meaningful inputs
text = text.replace(
    "if not _has_meaningful_inputs(user_data):",
    "if not _has_meaningful_inputs(safe_inputs):",
)
# local_tip with safe_inputs
text = text.replace(
    "return clean_tip(local_tip(user_data, emissions))",
    "return clean_tip(local_tip(safe_inputs, emissions))",
)
# compute_breakdowns on safe_inputs
text = text.replace(
    "_compute_breakdowns(user_data,",
    "_compute_breakdowns(safe_inputs,",
)
# context_str uses safe_inputs
text = text.replace(
    "for k in sorted(user_data.keys())",
    "for k in sorted(safe_inputs.keys())",
)
text = text.replace(
    "user_data.get(k, 0)",
    "safe_inputs.get(k, 0)",
)
text = text.replace(
    "sorted(user_data.items())",
    "sorted(safe_inputs.items())",
)

# 6) Negative cache in _generate_eco_tip_cached
if "_NEG_CACHE.get(user_data_key)" not in text:
    text = re.sub(
        r"(def _generate_eco_tip_cached\(user_data_key: str, emissions: float\) -> str:\n\s*\"\"\"Cached GPT tip generator[\s\S]*?\"\"\"\n)",
        r"\1    # Negative-cache gate: if we recently failed for this key, skip calling GPT\n    now = time.time()\n    exp = _NEG_CACHE.get(user_data_key)\n    if isinstance(exp, (int, float)) and exp > now:\n        return \"\"\n",
        text,
        count=1,
    )
# Replace tail return with tip + set neg cache if empty
text = re.sub(
    r"return _gpt_tip_from_prompt\(prompt\)",
    r"tip = _gpt_tip_from_prompt(prompt)\n    if not tip:\n        _NEG_CACHE[user_data_key] = time.time() + _NEG_TTL_SECONDS\n    return tip",
    text,
)

# 7) Jittered backoff
text = re.sub(
    r"sleep_s = base_delay \* \(2 \*\* attempt\)",
    r"sleep_s = base_delay * (2 ** attempt) + random.random() * 0.5",
    text,
)

# 8) Use sanitized inputs in generate_eco_tip_with_prompt
if "safe_inputs = _sanitize_inputs_for_prompt(user_data)" not in text:
    text = re.sub(
        r"(def generate_eco_tip_with_prompt\([\s\S]*?\):\n\s*\"\"\"[\s\S]*?\"\"\"\n)",
        r"\1    # Build structured context with sanitized inputs\n    safe_inputs = _sanitize_inputs_for_prompt(user_data)\n",
        text,
        count=1,
    )
text = text.replace(
    "_compute_breakdowns(user_data,",
    "_compute_breakdowns(safe_inputs,",
)
text = text.replace(
    "local_tip(user_data, emissions)",
    "local_tip(safe_inputs, emissions)",
)

# 9) Output sanitization & route clean_tip through it
if "def _sanitize_tip_output(" not in text:
    text += (
        "\n\ndef _sanitize_tip_output(t: str) -> str:\n"
        "    \"\"\"Collapse whitespace, strip URLs/HTML/code fences, and cap length for card display.\"\"\"\n"
        "    if not isinstance(t, str):\n"
        "        return \"\"\n"
        "    t = t.strip()\n"
        "    if not t:\n"
        "        return \"\"\n"
        "    t = re.sub(r\"```[\\s\\S]*?```\", \" \", t)\n"
        "    t = re.sub(r\"<[^>]+>\", \" \", t)\n"
        "    t = re.sub(r\"https?://\\S+\", \"\", t)\n"
        "    t = re.sub(r\"\\s+\", \" \", t).strip()\n"
        "    if len(t) > 240:\n"
        "        t = t[:237].rstrip() + \"…\"\n"
        "    return t\n"
    )
# Replace clean_tip body to call sanitizer + cap sentences
text = re.sub(
    r"def clean_tip\(tip: str, max_sentences: int = 2\) -> str:\n[\s\S]*?return tip\n",
    (
        "def clean_tip(tip: str, max_sentences: int = 2) -> str:\n"
        "    \"\"\"Trim/sanitize and limit the tip to a maximum number of sentences for UI.\"\"\"\n"
        "    tip = _sanitize_tip_output(tip)\n"
        "    if not tip:\n"
        "        return \"\"\n"
        "    parts = [p.strip() for p in tip.split('.') if p.strip()]\n"
        "    if len(parts) > max_sentences:\n"
        "        tip = '. '.join(parts[:max_sentences]).strip() + '.'\n"
        "    return tip\n"
    ),
    text,
)

if text != orig:
    TARGET.write_text(text, encoding="utf-8")
    print("Applied Day 6 perf/error improvements to ai_tips.py")
else:
    print("No changes applied (already up to date)")
