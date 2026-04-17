# Hermes integration contract

This repo is a thin local pipeline. Hermes remains the system-of-record runtime.

## Boundary summary

Hermes owns message ingress and outbound delivery.
This repo owns local voice-event processing after a local audio file exists.

## Ownership split

### Hermes owns
- Telegram webhook / polling ingest
- Telegram file download and local audio caching
- Authentication, bot token, chat/session context
- Deciding when to invoke this repo’s pipeline
- Sending reply messages back to Telegram
- Executing side effects outside this repo if action plans are accepted

### steve-thought-capture owns
- `VoiceEvent` contract definition
- audio preparation (`prepare_audio`)
- local ASR invocation (`transcribe_audio`)
- transcript normalization for Steve-aware use
- intent classification
- action planning
- passive learning log emission
- local manual smoke runner

## Required `VoiceEvent` fields

Hermes must supply these fields when calling the pipeline:
- `platform`: source platform string, usually `telegram`
- `chat_id`: Telegram chat ID used for reply routing
- `thread_id`: topic/thread identifier if present, else `None`
- `user_id`: sender identity
- `message_id`: source Telegram message ID
- `audio_path`: absolute local filesystem path to the cached audio file
- `mime_type`: source MIME type if known
- `duration_seconds`: duration if known, else `None`
- `received_at`: timestamp or timestamp-like value for traceability

## Audio path contract

Hermes is responsible for downloading Telegram voice/audio media and materializing a local file.
This repo assumes `audio_path` already exists and is readable.

If the file is already one of the supported formats (`ogg`, `wav`, `mp3`, `flac`, `opus`), `prepare_audio()` passes it through.
If not, this repo may convert it with `ffmpeg` before ASR.

## Pipeline call contract

Hermes should call:

`process_voice_event(voice_event, steve_context)`

Expected inputs:
- `voice_event`: populated `VoiceEvent`
- `steve_context`: dict loaded from repo config artifacts, including ASR and routing preferences

Expected return shapes:
- `status == "ok"`: includes prepared audio, transcript result, normalized transcript, intent decision, and action plan
- `status == "asr_failed"`: recoverable transcription failure with error string
- `status == "needs_clarification"`: transcript parsed but further clarification is required before actioning

## Reply ownership

This repo does not send Telegram messages directly.
It returns a structured result.
Hermes converts that result into a Telegram reply, follow-up question, or downstream action.

For v1, the cleanest contract is:
- this repo returns `actions`
- Hermes decides how to verbalize or execute them

## Execution side effects

This repo currently plans actions only. It does not mutate external systems.
Execution side effects stay inside Hermes or another downstream orchestrator.
That includes:
- sending Telegram text replies
- creating tasks
- writing notes to external systems
- updating project artifacts

## Passive learning logs

This repo writes append-only JSONL learning events to `logs/learning.jsonl` by default, or to `steve_context["learning"]["log_path"]` if provided.
Hermes can override the log path per environment, but should not own the log record schema.

## Recommended Hermes integration flow

1. Hermes receives a Telegram voice message.
2. Hermes downloads the media to a local cache path.
3. Hermes builds a `VoiceEvent` using Telegram metadata.
4. Hermes loads or constructs `steve_context` for this repo.
5. Hermes calls `process_voice_event(voice_event, steve_context)`.
6. Hermes inspects the returned `status`.
7. Hermes sends a reply or triggers downstream execution based on the returned action plan.

## Non-goals for this boundary

Do not make this repo own:
- Telegram bot credentials
- polling/webhook runtime management
- direct Telegram API calls
- external task/note/project writes in v1
- always-on microphone capture
