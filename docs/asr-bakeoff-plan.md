# ASR bakeoff plan: Whisper.cpp vs Breeze-ASR-25 vs GPT-4o Transcribe

## Why this exists

Steve's real Telegram voice usage is not plain Mandarin. It is often:
- Traditional Chinese / Taiwanese Mandarin
- mixed with English product terms
- mixed with model names and project names
- sometimes code-switched inside a single sentence

That means a generic ASR stack can feel usable while still failing on the exact terms Steve cares about.

This bakeoff exists to compare three layers:
- current real-time baseline: local whisper.cpp
- stronger local candidate: Breeze-ASR-25
- stronger API candidate: gpt-4o-transcribe

The output of this bakeoff should decide:
1. whether Breeze-ASR-25 is good enough to replace or augment the current local ASR
2. whether second-pass audit should use Breeze-ASR-25, gpt-4o-transcribe, or both
3. which errors should feed future lexicon / correction learning loops

## Current facts

### What is working now
- Telegram voice arrives in Hermes
- cached `.ogg` is saved under `~/.hermes/audio_cache/`
- `steve-thought-capture` converts Telegram `.ogg` to `.wav` before ASR
- whisper.cpp currently powers the live path
- successful runs leave:
  - `.ogg`
  - `.wav`
  - `.txt`

### Why Breeze-ASR-25 is interesting
According to its model card, Breeze-ASR-25 is:
- optimized for Traditional Chinese / Taiwanese Mandarin
- optimized for Mandarin-English code-switching
- stronger than Whisper baselines on several mixed-language benchmarks

This directly matches Steve's speech pattern.

## Candidate models

### A. Current baseline — whisper.cpp
Purpose:
- current production path
- measure latency and current live quality

### B. Local challenger — Breeze-ASR-25
Source:
- `https://huggingface.co/MediaTek-Research/Breeze-ASR-25`

Expected strengths:
- Taiwanese Mandarin
- Mandarin-English code-switching
- product / English term retention

Expected risk:
- local environment currently lacks `torch` and `transformers`
- model runtime / memory footprint must be validated before production adoption

### C. API challenger — gpt-4o-transcribe
Purpose:
- high-quality second-pass audit candidate
- easiest fast integration among cloud options

Important note:
- GPT-5.4 is not the primary STT model
- GPT-5.4 should be used as a transcript reviewer / diff analyzer, not the main transcriber

## Evaluation dataset

Use Steve's real Telegram audio cache, not synthetic samples.

Primary sample source:
- `~/.hermes/audio_cache/audio_*.ogg`

Suggested first batch size:
- 20 clips

Target composition:
- 8 short conversational clips
- 6 clips with obvious English model/product terms
- 4 more code-switched clips
- 2 harder / noisier clips

## Scoring rubric

### 1. English term preservation
Did the transcript preserve terms such as:
- Anthropic
- Opus
- Claude Code
- Ripple
- TW-LLM
- pdf2zh
- GPT-4o
- Gemini

### 2. Chinese sentence integrity
Did the Chinese sentence still mean what Steve said?

### 3. Code-switch handling
When Steve switches language mid-sentence, does the model:
- keep the switch correctly
- over-translate English into Chinese
- hallucinate Chinese around the English phrase
- drop English words entirely

### 4. Production practicality
- latency
- local memory cost
- integration complexity
- repeatability

## Decision rules

### Use Breeze-ASR-25 as primary live ASR if
- it clearly beats whisper.cpp on code-switched terms
- it keeps Chinese sentence meaning intact
- latency and local resource cost are acceptable

### Use Breeze-ASR-25 as second-pass audit only if
- quality is clearly better
- but runtime is too heavy or slow for live use

### Keep whisper.cpp as live ASR if
- Breeze gains are small on Steve's real audio
- or deployment complexity is too high relative to gain

### Use gpt-4o-transcribe for audit if
- it is the fastest way to stand up a high-quality second-pass loop
- and quality is competitive enough on Steve's clips

## Implementation plan

### Phase 1 — Environment probe
Check whether local runtime can support Breeze-ASR-25.

Current result on this machine:
- `hf`: available
- `faster_whisper`: available
- `torch`: missing
- `transformers`: missing

That means Breeze-ASR-25 is not runnable yet in the current environment.

### Phase 2 — Minimal local setup for Breeze
Install prerequisites in a controlled environment.

Suggested commands:

```bash
cd ~/workspace-max/steve-thought-capture
source /Users/ivyma/.hermes/hermes-agent/venv/bin/activate
python -m pip install torch transformers accelerate sentencepiece
hf download MediaTek-Research/Breeze-ASR-25
```

If the model is too large or install is messy, stop and record that as a real comparison signal.

### Phase 3 — Benchmark harness
Create a script that:
- loads a list of cached Telegram audio files
- runs each model/backend
- stores transcripts side-by-side
- writes comparison rows to JSONL or CSV

Recommended output path:
- `outputs/asr-bakeoff/`

Recommended artifacts per clip:
- original audio path
- whisper transcript
- Breeze transcript
- gpt-4o transcript
- review notes
- winner

### Phase 4 — Review pass
Use GPT-5.4 or another strong reasoning model to compare transcripts and extract:
- likely mistakes in the baseline
- lexicon candidates
- correction_map candidates
- clips worth keeping as hard examples

## Immediate next action

The next concrete step is:
1. install Breeze runtime dependencies
2. run a 5-clip pilot bakeoff
3. compare against current whisper.cpp outputs
4. decide whether to scale to a 20-clip evaluation

## Important constraint

Do not switch production live ASR to Breeze-ASR-25 before it wins on Steve's real Telegram clips.

The point is not to pick the coolest model.
The point is to pick the model that best understands Steve.
