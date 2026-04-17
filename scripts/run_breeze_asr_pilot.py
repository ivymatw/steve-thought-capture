from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from transformers import AutomaticSpeechRecognitionPipeline, WhisperForConditionalGeneration, WhisperProcessor


def load_pipeline(model_path: str):
    processor = WhisperProcessor.from_pretrained(model_path)
    model = WhisperForConditionalGeneration.from_pretrained(model_path)
    return AutomaticSpeechRecognitionPipeline(
        model=model,
        tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor,
        chunk_length_s=0,
        device='cpu',
    )


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    manifest_path = Path(args[0]) if args else Path('outputs/asr-bakeoff/sample-manifest.jsonl')
    out_path = Path(args[1]) if len(args) > 1 else Path('outputs/asr-bakeoff/breeze-pilot-results.jsonl')
    model_path = args[2] if len(args) > 2 else 'models/Breeze-ASR-25'
    limit = int(args[3]) if len(args) > 3 else 5

    records = [json.loads(line) for line in manifest_path.read_text(encoding='utf-8').splitlines() if line.strip()][:limit]
    pipe = load_pipeline(model_path)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open('w', encoding='utf-8') as handle:
        for record in records:
            sample_path = record.get('wav_path') or record['ogg_path']
            started = time.perf_counter()
            try:
                result = pipe(sample_path, return_timestamps=False)
                transcript = (result or {}).get('text', '').strip()
                error = None
            except Exception as exc:
                transcript = None
                error = str(exc)
            row = {
                'sample_id': record['sample_id'],
                'audio_path': sample_path,
                'baseline_transcript': record.get('baseline_transcript'),
                'breeze_transcript': transcript,
                'latency_seconds': round(time.perf_counter() - started, 3),
                'error': error,
            }
            handle.write(json.dumps(row, ensure_ascii=False) + '\n')
            print(json.dumps(row, ensure_ascii=False))

    print(f'wrote {len(records)} rows to {out_path}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
