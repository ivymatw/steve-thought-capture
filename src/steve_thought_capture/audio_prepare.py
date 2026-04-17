from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from steve_thought_capture.models import PreparedAudio

PASSTHROUGH_FORMATS = {"wav", "flac"}
FORCE_CONVERT_FORMATS = {"ogg", "opus", "mp3", "m4a", "aac", "webm"}


def _find_ffmpeg() -> str | None:
    return shutil.which("ffmpeg")


def _convert_with_ffmpeg(src: str, dst: str, ffmpeg_bin: str) -> str:
    subprocess.run([ffmpeg_bin, "-y", "-i", src, dst], check=True, capture_output=True, text=True)
    return dst


def prepare_audio(audio_path: str | Path) -> PreparedAudio:
    path = Path(audio_path).expanduser().resolve()
    ext = path.suffix.lower().lstrip(".")
    if ext in PASSTHROUGH_FORMATS:
        return PreparedAudio(str(path), str(path), ext, ext, False)

    ffmpeg_bin = _find_ffmpeg()
    if not ffmpeg_bin:
        raise RuntimeError("ffmpeg is required to convert unsupported audio formats")

    converted = str(path.with_suffix(".wav"))
    prepared = _convert_with_ffmpeg(str(path), converted, ffmpeg_bin)
    original_format = ext or "unknown"
    return PreparedAudio(str(path), prepared, original_format, "wav", True)
