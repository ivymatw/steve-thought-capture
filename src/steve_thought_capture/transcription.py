from __future__ import annotations

import subprocess
import time
from pathlib import Path

from steve_thought_capture.models import PreparedAudio, TranscriptResult


def _output_base_for_audio(path: str | Path) -> Path:
    audio_path = Path(path).expanduser().resolve()
    return audio_path.with_suffix("")


def _run_whisper_cpp(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True, capture_output=True, text=True)


def transcribe_audio(prepared_audio: PreparedAudio, steve_context: dict) -> TranscriptResult:
    asr_cfg = steve_context.get("asr", {})
    if asr_cfg.get("backend") != "whisper_cpp":
        return TranscriptResult(False, "", asr_cfg.get("backend", "unknown"), "", "", 0, "Unsupported backend")

    whisper_cfg = asr_cfg.get("whisper_cpp", {})
    binary_path = Path(whisper_cfg.get("binary_path", "")).expanduser()
    model_path = Path(whisper_cfg.get("model_path", "")).expanduser()
    language_mode = whisper_cfg.get("language_mode", "auto")
    model_name = whisper_cfg.get("model_name", "")

    if not binary_path.exists():
        return TranscriptResult(False, "", "whisper_cpp", model_name, language_mode, 0, "whisper.cpp binary not found")
    if not model_path.exists():
        return TranscriptResult(False, "", "whisper_cpp", model_name, language_mode, 0, "whisper.cpp model not found")

    output_base = _output_base_for_audio(prepared_audio.prepared_audio_path)
    cmd = [
        str(binary_path),
        "-m",
        str(model_path),
        "-l",
        language_mode,
        "-f",
        prepared_audio.prepared_audio_path,
        "-otxt",
        "-of",
        str(output_base),
    ]

    started = time.perf_counter()
    try:
        _run_whisper_cpp(cmd)
    except Exception as exc:
        return TranscriptResult(False, "", "whisper_cpp", model_name, language_mode, 0, str(exc))

    txt_output = output_base.with_suffix(".txt")
    if not txt_output.exists():
        return TranscriptResult(False, "", "whisper_cpp", model_name, language_mode, 0, "whisper.cpp did not produce transcript output")

    raw_text = txt_output.read_text().strip()
    latency_ms = int((time.perf_counter() - started) * 1000)
    return TranscriptResult(True, raw_text, "whisper_cpp", model_name, language_mode, latency_ms, None)
