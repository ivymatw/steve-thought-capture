# Breeze-ASR-25 expanded bakeoff — 15 real Telegram clips — 2026-04-17

## Purpose

Expand the initial 5-sample pilot into a larger real-audio check using every currently available recent Telegram voice clip in `~/.hermes/audio_cache/`.

This run is still Breeze vs the current baseline transcripts already produced by the live whisper.cpp-based pipeline.

## Artifacts

Manifest:
- `outputs/asr-bakeoff/sample-manifest-15.jsonl`

Breeze results:
- `outputs/asr-bakeoff/breeze-results-15.jsonl`

## Dataset

Available recent Telegram clips at run time:
- 15

All 15 were used.

These clips include:
- short control phrases
- normal Mandarin conversation
- Traditional Chinese preference cases
- English product / workflow terms
- mixed-language speech such as `candidate`, `GPT 5.4`, `text`, `loop`, `Telegram`, `implement`, `push`, `agent`, `follow`

## Run result

Execution status:
- 15/15 successful
- 0 transcription errors

Latency summary on CPU:
- average: 12.702s
- median: 11.5s
- min: 5.277s
- max: 24.748s

## What Breeze is consistently doing better

### 1. Traditional Chinese output is consistently better
Across the 15 clips, Breeze strongly trends toward Traditional Chinese output and more Taiwan-aligned wording.

Examples:
- `继续测试` -> `繼續測試`
- `看起来不错` -> `看起來不錯`
- `那我们下一步是什么` -> `那我們下一步是什麼`
- `像现在这样` -> `像現在這樣`

This alone makes Breeze feel closer to Steve's desired output style.

### 2. English term retention is materially better
Breeze preserved or restored many English workflow terms naturally inside Chinese sentences.

Representative examples:
- `Candidate` -> `candidate`
- `text` kept as `text`
- `loop` kept as `loop`
- `Telegram` kept as `telegram`
- `implement` kept as `implement`
- `Push` kept as `push`
- `agent` kept as `agent`
- `follow` kept as `follow`

This is the exact pattern the live system needs to handle well.

### 3. It repaired at least one clearly meaningful baseline error
Important example:
- baseline: `中陰夾雜`
- Breeze: `中英夾雜`

This remains the strongest single piece of evidence that Breeze understands Steve's mixed-language speech better than the current baseline.

### 4. It also repaired brand / project spelling drift
Examples:
- baseline: `Hermis agent`
- Breeze: `Hermes agent`

- baseline: `Hermis Ripple`
- Breeze: `Hermes ripple`

This matters because Steve often speaks project, product, and agent names that generic ASR tends to corrupt.

## Where Breeze is not yet proven enough

### 1. Latency is still audit-grade, not obviously live-grade
With a mean of 12.7s and worst-case near 24.7s on CPU, this is fine for:
- second-pass audit transcription
- correction candidate generation
- benchmark comparison

It is not yet strong evidence that Breeze should replace the current live path.

### 2. This round still compares against pipeline baseline, not human gold transcripts
The baseline transcript is useful, but it is not the final truth source.

For a production switch decision, the next stage should include:
- human-checked gold transcripts for a smaller hard set
- a third competitor such as `gpt-4o-transcribe`
- explicit win/loss labels per clip

## Overall judgment

The 5-sample pilot was not a fluke.

The 15-sample expansion reinforces the same conclusion:
- Breeze is consistently better aligned with Steve's real speech pattern
- Breeze is clearly better at Traditional Chinese style
- Breeze is clearly better at Mandarin-English mixed terminology retention
- Breeze fixes at least one high-value semantic error and several name-spelling errors
- Breeze is still too slow on CPU to promote directly to the live Telegram path

## Recommendation

Current recommendation is now stronger:

### Promote Breeze to serious second-pass candidate
Use Breeze for:
- audit transcription
- correction-map candidate generation
- hard-example harvesting
- lexicon bootstrapping for English terms and project names

### Do not replace live whisper.cpp yet
Keep whisper.cpp for the live path until one of these happens:
- Breeze runtime is materially optimized
- a smaller faster local model matches Breeze quality
- `gpt-4o-transcribe` proves to be the better audit layer and makes live replacement unnecessary

## Next concrete step

Run a 3-way bakeoff on a curated hard set:
1. whisper.cpp live baseline
2. Breeze-ASR-25
3. `gpt-4o-transcribe`

Suggested next evaluation set:
- 10 hard clips, not random recent clips
- prioritize clips with English terms, project names, and code-switching
- add human judgment per row: `baseline_wins`, `breeze_wins`, `4o_wins`, `tie`

## Bottom line

After 15 real Telegram clips, Breeze has crossed the threshold from "interesting" to "operationally useful".

The right current role is:
- not the live transcriber yet
- yes as the best current local second-pass ASR candidate
