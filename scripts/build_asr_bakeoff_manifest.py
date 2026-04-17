from __future__ import annotations

import json
import sys
from pathlib import Path


def build_manifest(audio_cache_dir: Path, limit: int = 20) -> list[dict]:
    records = []
    audio_files = sorted(audio_cache_dir.glob('audio_*.ogg'), key=lambda p: p.stat().st_mtime, reverse=True)[:limit]
    for audio in audio_files:
        stem = audio.stem
        wav = audio.with_suffix('.wav')
        txt = audio.with_suffix('.txt')
        records.append(
            {
                'sample_id': stem,
                'ogg_path': str(audio),
                'wav_path': str(wav) if wav.exists() else None,
                'baseline_txt_path': str(txt) if txt.exists() else None,
                'baseline_transcript': txt.read_text(encoding='utf-8').strip() if txt.exists() else None,
                'mtime': audio.stat().st_mtime,
                'size_bytes': audio.stat().st_size,
            }
        )
    return records


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    audio_cache_dir = Path(args[0]).expanduser() if args else Path.home() / '.hermes' / 'audio_cache'
    out_path = Path(args[1]).expanduser() if len(args) > 1 else Path('outputs/asr-bakeoff/sample-manifest.jsonl')
    limit = int(args[2]) if len(args) > 2 else 20

    records = build_manifest(audio_cache_dir.resolve(), limit=limit)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open('w', encoding='utf-8') as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + '\n')

    print(f'wrote {len(records)} samples to {out_path}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
