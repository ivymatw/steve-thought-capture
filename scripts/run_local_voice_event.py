from __future__ import annotations

import json
import sys
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from steve_thought_capture.steve_context import load_steve_context
from steve_thought_capture.telegram_adapter import run_local_voice_event



def _to_jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return {key: _to_jsonable(val) for key, val in asdict(value).items()}
    if isinstance(value, dict):
        return {key: _to_jsonable(val) for key, val in value.items()}
    if isinstance(value, list):
        return [_to_jsonable(item) for item in value]
    return value



def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 1:
        print("Usage: python scripts/run_local_voice_event.py <audio-path>", file=sys.stderr)
        return 1

    audio_path = Path(args[0]).expanduser().resolve()
    context = load_steve_context(REPO_ROOT)
    result = run_local_voice_event(audio_path, context)
    print(json.dumps(_to_jsonable(result), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
