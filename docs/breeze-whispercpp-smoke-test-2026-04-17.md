# Breeze-ASR-25 whisper.cpp smoke test — 2026-04-17

## Question

Can Breeze-ASR-25 escape the slow Python + PyTorch CPU path and still preserve the quality wins we observed earlier?

Short answer:
- yes
- and the result is much better than expected

## What was tested

Using the same 15 real Telegram clips from:
- `outputs/asr-bakeoff/sample-manifest-15.jsonl`

Compared three ways of running Breeze:

1. PyTorch / transformers on CPU
- source model: `MediaTek-Research/Breeze-ASR-25`
- artifact size: 2.9G safetensors

2. whisper.cpp Breeze q5_k
- model: `models/Breeze-ASR-25-whispercpp/ggml-model-q5_k.bin`
- size: 1.0G

3. whisper.cpp Breeze q4_k
- model: `models/Breeze-ASR-25-whispercpp/ggml-model-q4_k.bin`
- size: 848M

whisper.cpp binary used:
- `/Users/ivyma/workspace-max/voice-frontend/vendor/whisper.cpp/build/bin/whisper-cli`

## New reusable runner

Added:
- `scripts/run_whispercpp_manifest.py`

Purpose:
- run any whisper.cpp model over a JSONL sample manifest
- emit per-sample transcripts and latencies in JSONL
- reusable for Breeze, baseline Whisper, or future converted models

## Output artifacts

- `outputs/asr-bakeoff/breeze-whispercpp-q5k-results-15.jsonl`
- `outputs/asr-bakeoff/breeze-whispercpp-q4k-results-15.jsonl`
- `outputs/asr-bakeoff/breeze-whispercpp-q5k-smoke.jsonl`

## Latency result

### PyTorch CPU Breeze
- average: 12.702s
- median: 11.5s
- min: 5.277s
- max: 24.748s

### whisper.cpp Breeze q5_k
- average: 2.107s
- median: 2.011s
- min: 1.785s
- max: 2.977s

### whisper.cpp Breeze q4_k
- average: 1.98s
- median: 1.882s
- min: 1.332s
- max: 3.315s

## Speedup vs PyTorch CPU

- whisper.cpp q5_k: 6.03x faster on average
- whisper.cpp q4_k: 6.41x faster on average

This is not a marginal gain.
This changes the deployment conversation.

## Transcript quality vs PyTorch Breeze

### q5_k vs PyTorch
Out of 15 clips, only 3 transcript differences appeared.

1. `audio_ef7dc861f3e2`
- PyTorch: `辨認的更好的部分`
- q5_k: `辨認得更好的部分`
- judgment: negligible wording variation

2. `audio_dd8f1fc944e7`
- PyTorch: `本地的 Hermes ripple 沒有 push 有什麼特別的原因嗎`
- q5_k: `本地的 Hermes ripple mail push 有什麼特別的原因嗎`
- judgment: q5_k regression on this sample (`mail` hallucinated)

3. `audio_6250ceed0436`
- PyTorch: `再測試一次Max你這樣收得到我的語音訊息嗎`
- q5_k: `再測試一次 max 你這樣收得到我的語音訊息嗎`
- judgment: formatting / casing difference only

### q4_k vs PyTorch
Out of 15 clips, only 2 transcript differences appeared.

1. `audio_dd8f1fc944e7`
- same `mail push` regression as q5_k

2. `audio_6250ceed0436`
- same formatting / casing difference as q5_k

## Most important finding

The quality wins that made Breeze interesting are preserved under whisper.cpp.

Still observed:
- Traditional Chinese style is better than baseline
- code-switching terms like `candidate`, `gpt 5.4`, `text`, `loop`, `telegram`, `implement`, `push`, `agent`, `follow` are preserved naturally
- the critical repair remains intact:
  - baseline: `中陰夾雜`
  - whisper.cpp Breeze: `中英夾雜`
- project / agent spelling repair remains intact:
  - `Hermis` -> `Hermes`

## Practical interpretation

This means the earlier concern was only half true.

### Earlier belief
- Breeze is better but too slow

### Updated belief
- Breeze in PyTorch CPU mode is too slow
- Breeze in whisper.cpp form is fast enough to be taken seriously for near-live use

That is a major shift.

## Current recommendation

### Best default local candidate right now
Use Breeze-ASR-25 whisper.cpp q5_k as the main serious candidate.

Why q5_k:
- almost the same speed as q4_k in practice on this 15-clip set
- slightly safer quality posture than q4_k
- still much smaller and much faster than PyTorch Breeze

### q4_k is also viable
q4_k is attractive when memory pressure matters.

Observed here:
- q4_k is the fastest tested option
- but the speed edge over q5_k is small
- transcript behavior is nearly identical on this sample set

### One caution
At least one sample showed a regression:
- `mail push` hallucination on `audio_dd8f1fc944e7`

So do not declare total victory yet.
The next step should be a harder targeted evaluation set, not an immediate production cutover.

## Recommended next step

Run a hard-set comparison with explicit human judgment:
1. current live whisper.cpp model (`large-v3-turbo`)
2. Breeze whisper.cpp q5_k
3. optionally Breeze whisper.cpp q4_k
4. optionally `gpt-4o-transcribe` as audit reference

Target hard examples:
- English product names
- agent / repo / project names
- code-switching sentences
- clips where baseline historically fails

## Bottom line

Yes, Breeze does have a credible fast local path.

Not via Ollama.
Not via generic llama.cpp text inference.

The right path is whisper.cpp.

And on this machine, that path already delivered:
- about 6x speedup over PyTorch CPU Breeze
- much smaller runtime artifacts
- nearly the same transcript quality
- preservation of the most important mixed-language wins
