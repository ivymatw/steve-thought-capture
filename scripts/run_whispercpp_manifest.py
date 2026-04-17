from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def run_one(binary_path: Path, model_path: Path, audio_path: str, language: str, threads: int) -> tuple[str | None, str | None, float]:
    started = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="whispercpp-") as tmpdir:
        output_base = Path(tmpdir) / "transcript"
        cmd = [
            str(binary_path),
            "-m",
            str(model_path),
            "-f",
            audio_path,
            "-l",
            language,
            "-t",
            str(threads),
            "-otxt",
            "-of",
            str(output_base),
            "-np",
            "-nt",
        ]
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            txt_path = output_base.with_suffix(".txt")
            if not txt_path.exists():
                return None, "whisper.cpp did not produce transcript output", time.perf_counter() - started
            return txt_path.read_text(encoding="utf-8").strip(), None, time.perf_counter() - started
        except subprocess.CalledProcessError as exc:
            stderr = (exc.stderr or "").strip()
            stdout = (exc.stdout or "").strip()
            error = stderr or stdout or str(exc)
            return None, error, time.perf_counter() - started


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    manifest_path = Path(args[0]) if len(args) > 0 else Path("outputs/asr-bakeoff/sample-manifest-15.jsonl")
    out_path = Path(args[1]) if len(args) > 1 else Path("outputs/asr-bakeoff/breeze-whispercpp-q5k-results-15.jsonl")
    model_path = Path(args[2]) if len(args) > 2 else Path("models/Breeze-ASR-25-whispercpp/ggml-model-q5_k.bin")
    binary_path = Path(args[3]) if len(args) > 3 else Path("/Users/ivyma/workspace-max/voice-frontend/vendor/whisper.cpp/build/bin/whisper-cli")
    limit = int(args[4]) if len(args) > 4 else 15
    language = args[5] if len(args) > 5 else "auto"
    threads = int(args[6]) if len(args) > 6 else 4

    records = [json.loads(line) for line in manifest_path.read_text(encoding="utf-8").splitlines() if line.strip()][:limit]
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with out_path.open("w", encoding="utf-8") as handle:
        for record in records:
            audio_path = record.get("wav_path") or record.get("ogg_path")
            transcript, error, latency = run_one(binary_path, model_path, audio_path, language, threads)
            row = {
                "sample_id": record["sample_id"],
                "audio_path": audio_path,
                "baseline_transcript": record.get("baseline_transcript"),
                "whispercpp_model_path": str(model_path),
                "whispercpp_transcript": transcript,
                "latency_seconds": round(latency, 3),
                "error": error,
            }
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
            print(json.dumps(row, ensure_ascii=False))

    print(f"wrote {min(len(records), limit)} rows to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
