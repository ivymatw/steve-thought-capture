# Breeze CoreML / ANE side-project evaluation — 2026-04-17

## Goal

Evaluate whether `https://huggingface.co/sheep52031/breeze-asr-25-coreml-ane` offers a meaningful advantage over the current production default:
- `Breeze-ASR-25 whisper.cpp q5_k`
- Metal GPU acceleration
- no CoreML / ANE

Important constraint:
- do not change the production path while evaluating

## Current production baseline

Current checked-in default:
- `configs/asr.yaml`
- `model_name: breeze-asr-25-q5_k`
- runtime: whisper.cpp
- acceleration: Metal GPU

Observed current backend signal:
- `WHISPER : COREML = 0`
- `whisper_backend_init_gpu: using MTL0 backend`

## What this side project tested

### 1. Artifact fetch
Downloaded from Hugging Face into a local experimental directory:
- `models/Breeze-ASR-25-coreml-ane/ggml-breeze-asr-25-q5k.bin`
- `models/Breeze-ASR-25-coreml-ane/ggml-breeze-asr-25-encoder.mlmodelc.zip`

### 2. whisper.cpp CoreML build
Built a separate whisper.cpp tree with CoreML enabled:
- build dir: `/Users/ivyma/workspace-max/voice-frontend/vendor/whisper.cpp/build-coreml`
- cmake flag: `-DWHISPER_COREML=ON`

This succeeded.

### 3. Naming compatibility fix
The downloaded encoder directory name did not match the path whisper.cpp automatically expects.

whisper.cpp derives the encoder path from the decoder `.bin` path by replacing `.bin` with:
- `-encoder.mlmodelc`

For this q5_k model, it expected:
- `ggml-breeze-asr-25-q5k-encoder.mlmodelc`

But the repo ships:
- `ggml-breeze-asr-25-encoder.mlmodelc.zip`

To make the experiment work, the encoder zip was unpacked and a symlink was added:
- `ggml-breeze-asr-25-q5k-encoder.mlmodelc -> ggml-breeze-asr-25-encoder.mlmodelc`

This is an important operational detail for any future agent reproducing the experiment.

## First real probe

### Clip used
- `audio_1af92b5380b9.wav`
- transcript topic: `我剛剛就發語音了你確認一下是不是用 breeze`

### Result: current production path (Metal only)
Runtime signal:
- `WHISPER : COREML = 0`

Transcript:
- `我剛剛就發語音了你確認一下是不是用 breeze`

Timing observed earlier on the same clip:
- total time ≈ `1581.91 ms`

### Result: CoreML / ANE hybrid path
Runtime signal:
- `WHISPER : COREML = 1`
- `Core ML model loaded`

Transcript:
- `我剛剛就發語音啊你確認一下是不是用 breeze`

Timings:
- first run: `11504.04 ms` total
  - clearly dominated by cold-start / initialization overhead
- second run: `2270.33 ms` total
  - this is the more meaningful warm result

## Current judgment

Conclusion first:
- no obvious advantage yet
- on the first real probe, the CoreML / ANE hybrid path was worse than the current production Metal path

### Why this is not a win yet

1. Warm latency was slower
- current production q5_k Metal: about `1581.91 ms`
- CoreML / ANE hybrid warm run: about `2270.33 ms`

That is roughly:
- about `688 ms` slower
- about `1.44x` the latency of the current production path

2. Transcript quality did not improve
Current production transcript:
- `我剛剛就發語音了你確認一下是不是用 breeze`

CoreML / ANE transcript:
- `我剛剛就發語音啊你確認一下是不是用 breeze`

This is not a catastrophic error, but it is a regression rather than an improvement.

3. Integration complexity is materially higher
Compared with the current production path, the CoreML experiment requires:
- a separate whisper.cpp build with CoreML enabled
- model artifact download from a different repo
- encoder unzip step
- path-name normalization / symlink fix
- separate runtime validation

So even before quality or speed is judged, the operational burden is already higher.

## What this means

At this point, the CoreML / ANE path has not earned promotion.

The current Breeze q5_k + Metal path remains better because it is:
- simpler
- already in production
- faster on the tested clip
- at least as good qualitatively on the tested clip

## Recommendation

### Keep production unchanged
Do not replace the current production default with the CoreML / ANE hybrid path.

### Continue only as a bounded side project
This path is still worth one limited follow-up test because one clip is not enough to close the question completely.

Recommended next step if continuing:
- run a 5-clip comparison using the same recent Telegram clips
- compare:
  1. current Breeze q5_k Metal production path
  2. CoreML / ANE hybrid q5_k path
- measure:
  - warm latency only
  - cold-start cost separately
  - transcript diffs
  - any new hallucination / regression patterns

### Stop condition
If the 5-clip follow-up still shows:
- slower latency
- no quality improvement

then the side project should be closed as not worth the added complexity.

## 5-clip warm-only follow-up

A broader warm-only benchmark was then run on 5 recent real Telegram clips using:
- `outputs/asr-bakeoff/coreml-sideproject-manifest-5.jsonl`
- `scripts/run_whispercpp_warm_benchmark.py`
- output: `outputs/asr-bakeoff/coreml-sideproject-warm-benchmark-5.jsonl`

Method:
- for each clip and each runtime, run one throwaway warmup pass
- then record the second pass as the timed comparison

Compared:
1. current production `Breeze q5_k + Metal`
2. side-project `Breeze q5_k + CoreML/ANE hybrid`

### Warm-only timing result

Average timed latency across the 5 clips:
- production q5_k Metal: `2.154s`
- CoreML / ANE hybrid q5_k: `3.118s`

Difference:
- CoreML / ANE hybrid was slower by about `964 ms` on average
- CoreML / ANE hybrid was about `1.448x` the latency of the current production path

### Transcript comparison

Across all 5 clips:
- timed transcript differences: `0`

That means the CoreML / ANE hybrid path did not buy better transcription quality on this sample set.
It only added latency and complexity.

## Bottom line

The CoreML / ANE version is technically runnable on this machine.
But after both:
- the first real single-clip probe, and
- the 5-clip warm-only follow-up,

it still does not show a meaningful advantage.

Right now it looks like:
- interesting engineering
- not yet a better production choice
- probably not worth further investment unless a specific longer-audio use case suggests ANE might win there
