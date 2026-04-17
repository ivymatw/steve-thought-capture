# Hermes Gateway Integration Implementation Notes

This document explains the exact local Hermes-side changes needed to connect Telegram voice messages to `steve-thought-capture`.

## Scope

This is not generic STT.
This is a Steve-specific Telegram voice path that runs before the normal inbound voice transcription flow.

## Files changed in Hermes

### 1. `gateway/steve_voice.py`

Responsibilities:
- resolve whether Steve voice pipeline should be active
- construct a `VoiceEvent`
- call `steve_thought_capture.pipeline.process_voice_event(...)`
- map pipeline result into a gateway-facing outcome

Important functions:
- `resolve_steve_thought_capture_root(config, source)`
- `execute_steve_thought_capture_pipeline(audio_path, source, project_root)`
- `build_steve_thought_capture_gateway_outcome(result, user_text="")`
- `format_steve_thought_capture_result(result)`

### 2. `gateway/run.py`

Responsibilities:
- import the Steve voice helpers
- call `_enrich_message_with_voice_pipeline(...)` for Telegram audio
- if pipeline says `reply`, return normalized transcript as the inbound message text
- if pipeline says `needs_clarification`, send clarification directly and stop
- if pipeline says `asr_failed`, send direct failure message and stop
- otherwise fall back to generic STT only when Steve pipeline resolution or execution fails unexpectedly

### 3. `tests/gateway/test_steve_voice_pipeline.py`

Responsibilities:
- verify `reply` action returns normalized transcript into the normal agent path
- verify `needs_clarification` sends direct Telegram reply and returns `None`

## Exact control-flow shape

In `gateway/run.py`:

1. `_prepare_inbound_message_text(...)`
2. detect `audio_paths`
3. call `_enrich_message_with_voice_pipeline(event, user_text, audio_paths, source)`
4. inside `_enrich_message_with_voice_pipeline(...)`:
   - resolve Steve project root
   - run pipeline in a thread
   - build gateway outcome
   - branch on outcome kind

Outcome kinds:
- `agent`
  - return text into normal Hermes agent flow
- `reply`
  - call adapter `.send(...)`
  - reply to the original Telegram message
  - include thread metadata if present
  - return `None` so normal agent handling stops

## Why this shape was chosen

Because the system needs two different behaviors:

### For `conversation_reply`
The voice message should behave like normal user input.
That means Hermes should still own the full response generation.
So the normalized transcript is fed back into the standard inbound text path.

### For `needs_clarification` and `asr_failed`
There is no benefit in sending a synthetic meta-prompt into the agent.
The gateway can reply immediately and preserve cleaner control flow.

## Critical audio-format lesson

Do not assume Telegram `.ogg` files are safe to pass directly to whisper.cpp.
In practice, real Telegram voice notes may fail silently unless converted to `.wav` first.

The fix for that is in `steve-thought-capture/src/steve_thought_capture/audio_prepare.py`, not Hermes.
Hermes should keep treating cached audio as opaque input and let `steve-thought-capture` prepare it.

## Environment contract

Hermes needs:
- `HERMES_STEVE_THOUGHT_CAPTURE_ROOT`

Optional gate:
- `HERMES_STEVE_THOUGHT_CAPTURE_CHAT_ID` or `HERMES_STEVE_THOUGHT_CAPTURE_CHAT_IDS`

If root resolution fails, Hermes should fall back to generic STT.

## Recommended apply strategy for another agent

### Option A: Manual reproduction

Read and update these Hermes files directly:
- `gateway/steve_voice.py`
- `gateway/run.py`
- `tests/gateway/test_steve_voice_pipeline.py`

### Option B: Apply the exported patch

Patch file:
- `references/hermes-gateway-steve-voice.patch`

Suggested flow:

```bash
cd /path/to/hermes-agent
git apply /path/to/steve-thought-capture/references/hermes-gateway-steve-voice.patch
source venv/bin/activate
python -m pytest tests/gateway/test_steve_voice_pipeline.py -q
```

If patch application fails because local Hermes has drifted, use the patch as a human-readable diff reference and apply manually.

## Live verification after applying Hermes changes

1. Restart Hermes gateway
2. Send a Telegram voice message
3. Expect one of three outcomes:
   - normal conversational reply
   - direct clarification question
   - direct ASR failure notice

If you get the ASR failure notice repeatedly, check the `steve-thought-capture` audio preparation path first.

## Current known-good local commits

### steve-thought-capture
- `1ad2e4a` fix: convert Telegram ogg audio before ASR
- `0ea2515` feat: add local runner and learning logs

### local Hermes
- `8d8458c5` feat: route Telegram voice through Steve pipeline
- `27520fdb` feat: bridge telegram voice into steve pipeline
