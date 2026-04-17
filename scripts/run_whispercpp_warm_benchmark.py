from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def run_once(binary_path: Path, model_path: Path, audio_path: str, language: str, threads: int) -> tuple[str | None, str | None, float]:
    started = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="warm-bench-") as tmpdir:
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
            return None, stderr or stdout or str(exc), time.perf_counter() - started


def benchmark_model(binary_path: Path, model_path: Path, audio_path: str, language: str, threads: int) -> dict:
    warmup_text, warmup_error, warmup_latency = run_once(binary_path, model_path, audio_path, language, threads)
    timed_text, timed_error, timed_latency = run_once(binary_path, model_path, audio_path, language, threads)
    return {
        "warmup_transcript": warmup_text,
        "warmup_error": warmup_error,
        "warmup_latency_seconds": round(warmup_latency, 3),
        "timed_transcript": timed_text,
        "timed_error": timed_error,
        "timed_latency_seconds": round(timed_latency, 3),
    }


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    manifest_path = Path(args[0]) if len(args) > 0 else Path("outputs/asr-bakeoff/coreml-sideproject-manifest-5.jsonl")
    out_path = Path(args[1]) if len(args) > 1 else Path("outputs/asr-bakeoff/coreml-sideproject-warm-benchmark-5.jsonl")
    prod_binary = Path(args[2]) if len(args) > 2 else Path("/Users/ivyma/workspace-max/voice-frontend/vendor/whisper.cpp/build/bin/whisper-cli")
    prod_model = Path(args[3]) if len(args) > 3 else Path("models/Breeze-ASR-25-whispercpp/ggml-model-q5_k.bin")
    coreml_binary = Path(args[4]) if len(args) > 4 else Path("/Users/ivyma/workspace-max/voice-frontend/vendor/whisper.cpp/build-coreml/bin/whisper-cli")
    coreml_model = Path(args[5]) if len(args) > 5 else Path("models/Breeze-ASR-25-coreml-ane/ggml-breeze-asr-25-q5k.bin")
    limit = int(args[6]) if len(args) > 6 else 5
    language = args[7] if len(args) > 7 else "auto"
    threads = int(args[8]) if len(args) > 8 else 4

    records = [json.loads(line) for line in manifest_path.read_text(encoding="utf-8").splitlines() if line.strip()][:limit]
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with out_path.open("w", encoding="utf-8") as handle:
        for record in records:
            audio_path = record.get("wav_path") or record.get("ogg_path")
            prod = benchmark_model(prod_binary, prod_model, audio_path, language, threads)
            coreml = benchmark_model(coreml_binary, coreml_model, audio_path, language, threads)
            row = {
                "sample_id": record["sample_id"],
                "audio_path": audio_path,
                "baseline_transcript": record.get("baseline_transcript"),
                "production_q5k_metal": prod,
                "coreml_ane_hybrid_q5k": coreml,
            }
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
            print(json.dumps(row, ensure_ascii=False))

    print(f"wrote {min(len(records), limit)} rows to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
