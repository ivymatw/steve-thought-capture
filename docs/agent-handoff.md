# Steve Thought Capture Agent Handoff

This document is for another agent that needs to reproduce the current working system without relying on chat history.

## Goal

Reproduce the current state where:
- Telegram voice messages arrive in Hermes
- Hermes routes them through `steve-thought-capture`
- `conversation_reply` audio becomes normal inbound text for Hermes
- `needs_clarification` replies directly in Telegram
- `asr_failed` replies directly in Telegram
- Telegram `.ogg` voice notes are converted to `.wav` before ASR
- the default local production ASR path is now `Breeze-ASR-25 whisper.cpp q5_k`, not `large-v3-turbo`

## Current ASR default

As of the latest checked-in state, `configs/asr.yaml` points to:
- `backend: whisper_cpp`
- `model_name: breeze-asr-25-q5_k`
- `model_path: /Users/ivyma/workspace-max/steve-thought-capture/models/Breeze-ASR-25-whispercpp/ggml-model-q5_k.bin`

Important evidence files for another agent:
- `docs/breeze-whispercpp-smoke-test-2026-04-17.md`
- `docs/asr-hardset-breeze-vs-large-v3-turbo-2026-04-17.md`
- `outputs/asr-bakeoff/breeze-whispercpp-q5k-results-15.jsonl`
- `outputs/asr-bakeoff/breeze-whispercpp-q5k-hardset-10.jsonl`
- `outputs/asr-bakeoff/baseline-large-v3-turbo-hardset-10.jsonl`

## What is already done

### In this repo (`steve-thought-capture`)

Implemented pipeline spine:
- `src/steve_thought_capture/models.py`
- `src/steve_thought_capture/audio_prepare.py`
- `src/steve_thought_capture/transcription.py`
- `src/steve_thought_capture/normalize.py`
- `src/steve_thought_capture/interpret.py`
- `src/steve_thought_capture/route.py`
- `src/steve_thought_capture/learning.py`
- `src/steve_thought_capture/pipeline.py`
- `src/steve_thought_capture/steve_context.py`
- `src/steve_thought_capture/telegram_adapter.py`
- `scripts/run_local_voice_event.py`

Config artifacts:
- `configs/asr.yaml`
- `configs/lexicon.yaml`
- `configs/correction_map.yaml`
- `configs/routing_preferences.yaml`
- `configs/project_aliases.yaml`

Docs:
- `docs/hermes-integration.md`
- `docs/hermes-gateway-integration.md`
- `docs/agent-handoff.md`

Exported Hermes patch bundle:
- `references/hermes-gateway-steve-voice.patch`

### In local Hermes

Local Hermes changes exist in:
- `gateway/steve_voice.py`
- `gateway/run.py`
- `tests/gateway/test_steve_voice_pipeline.py`

Those local Hermes changes are also exported into:
- `references/hermes-gateway-steve-voice.patch`

## Current working behavior

### Success path

1. Telegram sends a voice note
2. Hermes downloads it to local audio cache
3. Hermes resolves `HERMES_STEVE_THOUGHT_CAPTURE_ROOT`
4. Hermes calls `execute_steve_thought_capture_pipeline(...)`
5. `steve-thought-capture` runs:
   - audio prepare
   - whisper.cpp transcription
   - normalization
   - intent classification
   - action planning
6. Hermes maps the result:
   - if `reply` action -> feed normalized transcript into the normal agent chat loop
   - if `needs_clarification` -> send clarification question directly to Telegram
   - if `asr_failed` -> send a direct failure message to Telegram

### Important bug already fixed

Telegram `.ogg` voice notes could not be reliably passed straight into whisper.cpp.
They now convert to `.wav` first in `audio_prepare.py`.

This is critical.
Without this fix, real Telegram voice notes can fail with:
- `whisper.cpp did not produce transcript output`

## Exact files another agent should read first

### Must-read in this repo

1. `docs/hermes-integration.md`
2. `docs/hermes-gateway-integration.md`
3. `src/steve_thought_capture/pipeline.py`
4. `src/steve_thought_capture/audio_prepare.py`
5. `src/steve_thought_capture/transcription.py`
6. `src/steve_thought_capture/interpret.py`
7. `src/steve_thought_capture/route.py`
8. `src/steve_thought_capture/learning.py`
9. `references/hermes-gateway-steve-voice.patch`

### Must-read in local Hermes

1. `gateway/steve_voice.py`
2. `gateway/run.py`
3. `tests/gateway/test_steve_voice_pipeline.py`

## Environment assumptions

The working local setup used these values:
- steve-thought-capture root: `/Users/ivyma/workspace-max/steve-thought-capture`
- Hermes repo root: `/Users/ivyma/.hermes/hermes-agent`
- whisper binary/model configured in `configs/asr.yaml`
- `ffmpeg` installed

Important env vars used by Hermes:
- `HERMES_STEVE_THOUGHT_CAPTURE_ROOT=/Users/ivyma/workspace-max/steve-thought-capture`
- `HERMES_STEVE_THOUGHT_CAPTURE_CHAT_ID=7957198434`

## Verification commands

### Verify steve-thought-capture locally

```bash
cd /Users/ivyma/workspace-max/steve-thought-capture
source /Users/ivyma/.hermes/hermes-agent/venv/bin/activate
PYTHONPATH=src pytest tests/ -q
python scripts/run_local_voice_event.py /path/to/audio.wav
```

### Verify Telegram `.ogg` handling specifically

```bash
cd /Users/ivyma/workspace-max/steve-thought-capture
source /Users/ivyma/.hermes/hermes-agent/venv/bin/activate
PYTHONPATH=src python - <<'PY'
from pathlib import Path
from steve_thought_capture.models import VoiceEvent
from steve_thought_capture.pipeline import process_voice_event
from steve_thought_capture.steve_context import load_steve_context

root = Path('/Users/ivyma/workspace-max/steve-thought-capture')
audio = Path('/Users/ivyma/.hermes/audio_cache/audio_9a21a8e92d85.ogg')
ctx = load_steve_context(root)
event = VoiceEvent(platform='telegram', chat_id='7957198434', thread_id=None, user_id='steve', message_id=audio.stem, audio_path=str(audio), mime_type='audio/ogg', duration_seconds=None, received_at='now')
print(process_voice_event(event, ctx))
PY
```

Expected behavior:
- `prepared_audio_path` becomes `.wav`
- `status` should be `ok`

### Verify Hermes-side mapping behavior

```bash
cd /Users/ivyma/.hermes/hermes-agent
source venv/bin/activate
python -m pytest tests/gateway/test_steve_voice_pipeline.py -q
python -m pytest tests/gateway/test_stt_config.py tests/gateway/test_steve_voice_pipeline.py -q
```

## What is reusable vs local-only

### Reusable

Reusable logic lives in this repo:
- audio preparation
- local ASR invocation contract
- normalization
- heuristic routing
- learning logs
- local runner
- Hermes integration contract docs

Reusable Hermes pattern:
- early Telegram voice interception
- pipeline execution before generic STT
- outcome mapping:
  - `agent` path for reply
  - direct Telegram reply for clarification/failure

### Local-only

These are environment-specific:
- Telegram bot runtime
- local launchd service
- exact whisper model path
- exact ffmpeg path
- allowlists / Telegram auth
- local Hermes checkout state

## Recommended reproduction order for another agent

1. Clone or update `steve-thought-capture`
2. Read `docs/hermes-integration.md`
3. Read `docs/hermes-gateway-integration.md`
4. Verify `steve-thought-capture` tests pass
5. Apply or manually reproduce `references/hermes-gateway-steve-voice.patch` in Hermes
6. Run Hermes gateway tests
7. Set `HERMES_STEVE_THOUGHT_CAPTURE_ROOT`
8. Restart Hermes gateway
9. Send a real Telegram voice message

## Non-goals right now

These are not implemented yet:
- real note/task/project side effects
- project artifact writing
- knowledge capture side effects
- smarter clarification loops
- model-based intent classification

The system is currently strongest at:
- voice in
- transcript normalization
- conversation reply
- basic clarification/failure handling
