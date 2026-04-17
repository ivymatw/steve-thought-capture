from __future__ import annotations

import shutil
import subprocess

from steve_thought_capture.models import NormalizedTranscript


def _to_traditional_chinese(text: str) -> tuple[str, list[str]]:
    opencc_bin = shutil.which("opencc")
    if not opencc_bin:
        return text, []

    try:
        result = subprocess.run(
            [opencc_bin, "-c", "s2twp.json"],
            input=text,
            capture_output=True,
            text=True,
            check=True,
        )
    except Exception:
        return text, []

    converted = (result.stdout or text).strip()
    if converted != text:
        return converted, ["s2twp"]
    return converted, []


def normalize_transcript(raw_text: str, steve_context: dict) -> NormalizedTranscript:
    if not raw_text:
        return NormalizedTranscript(raw_text="", normalized_text="", applied_rules=[], uncertainty_flags=[])

    applied_rules: list[str] = []
    normalized = " ".join(raw_text.strip().split())
    if normalized != raw_text:
        applied_rules.append("collapse_whitespace")

    normalized, script_rules = _to_traditional_chinese(normalized)
    applied_rules.extend(script_rules)

    substitutions = steve_context.get("correction_map", {}).get("substitutions", {})
    for source, target in substitutions.items():
        if normalized == source:
            normalized = target
            applied_rules.append(f"substitute:{source}")
            break

    return NormalizedTranscript(
        raw_text=raw_text,
        normalized_text=normalized,
        applied_rules=applied_rules,
        uncertainty_flags=[],
    )
