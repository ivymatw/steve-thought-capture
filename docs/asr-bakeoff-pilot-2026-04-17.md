# Breeze-ASR-25 pilot results — 2026-04-17

## Purpose

Run a small real-audio pilot before committing to a larger ASR bakeoff.

Compared:
- current baseline transcripts already produced in the Telegram voice pipeline
- Breeze-ASR-25 local inference on the same cached Telegram audio

## Environment used

Project path:
- `/Users/ivyma/workspace-max/steve-thought-capture`

Pilot environment:
- local project venv: `.venv`
- Python: 3.11.15

Installed for pilot:
- `torch`
- `transformers`
- `accelerate`
- `sentencepiece`
- `soundfile`
- `librosa`
- `huggingface_hub`

Downloaded Breeze inference artifacts only, not full training bundle.

## Sample set

Used the 5 most recent real Telegram audio samples from:
- `~/.hermes/audio_cache/`

Manifest:
- `outputs/asr-bakeoff/sample-manifest.jsonl`

Pilot output:
- `outputs/asr-bakeoff/breeze-pilot-results.jsonl`

## High-level result

Breeze-ASR-25 is promising.

It handled all 5 pilot samples successfully and showed clear qualitative wins on:
- Traditional Chinese output
- Mandarin-English code-switching preservation
- specific error repair for the baseline transcript

The most important observed win in this pilot:
- baseline: `中陰夾雜`
- Breeze: `中英夾雜`

That is exactly the kind of Steve-specific error this project needs to reduce.

## Per-sample observations

### 1. `audio_332e05cf0591`
Baseline:
- `好 我們來試 然後把這個討論也寫到文件裡面`

Breeze:
- `好我們來試然後把這個討論也寫到文件裡面`

Judgment:
- essentially equivalent
- Breeze mainly changed spacing style

### 2. `audio_41e20cb531c7`
Baseline:
- `比较好的模型你有Candidate吗? 现在这个GPT 5.4可以吗?还是有什么建议?`

Breeze:
- `比較好的模型你有 candidate 嗎現在這個 gpt 5.4 可以嗎還是有什麼建議`

Judgment:
- Breeze preserved the English term `candidate`
- Breeze normalized more naturally toward Traditional Chinese
- strong sign for mixed-language usage

### 3. `audio_078d2addf907`
Baseline:
- `那这样如果你能够比如说一段时间...加进去学习的loop`

Breeze:
- `那這樣如果你能夠比如說一段時間...加進去學習的 loop`

Judgment:
- Breeze better preserved Traditional Chinese style
- English `text` and `loop` are retained cleanly
- likely better for Steve's natural code-switching pattern

### 4. `audio_bc65e9dd8cfe`
Baseline:
- `像现在这样 我从Telegram 传给你的那个语音的档案 你都有留着吗?`

Breeze:
- `像現在這樣我從 telegram 傳給你的那個語音的檔案你都有留著嗎`

Judgment:
- semantically equivalent
- Breeze better fits Traditional Chinese output
- `telegram` kept as English term

### 5. `audio_ef7dc861f3e2`
Baseline:
- `现在中阴夹杂如果辨识失败会怎么样...`

Breeze:
- `現在中英夾雜如果辨識失敗會怎麼樣...`

Judgment:
- clear Breeze win
- fixed a meaningful baseline recognition error (`中陰` -> `中英`)
- this sample alone justifies continuing the benchmark

## Latency notes

Observed pilot latencies on CPU were roughly:
- 8.3s
- 12.3s
- 24.8s
- 12.5s
- 18.6s

Interpretation:
- probably acceptable for second-pass audit
- probably too slow to adopt immediately as the live Telegram path without more optimization

## Current decision

Do not replace live whisper.cpp yet.

Do continue with the bakeoff.

Recommended next step:
1. expand from 5 samples to 20 samples
2. add `gpt-4o-transcribe` as the cloud challenger
3. use GPT-5.4 as transcript-diff reviewer / correction-candidate extractor

## Interim recommendation

Breeze-ASR-25 is already strong enough to be treated as a serious candidate for:
- second-pass audit transcription
- correction candidate generation
- lexicon / correction-map bootstrapping

It has not yet earned promotion to the live production ASR path.
