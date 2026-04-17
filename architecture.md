# Steve thought capture system architecture

Date: 2026-04-17

Related spec: `~/workspace-max/steve-thought-capture/spec.md`

## Purpose

This document expands the product spec into a concrete system architecture.

The goal is to define:
- module boundaries
- runtime data flow
- decision points
- storage artifacts
- learning loop
- failure handling
- implementation phases

This architecture is optimized for Steve's actual working style:
- Telegram-first interaction
- local ASR by default
- no review-first bottleneck
- strong mixed-language handling
- routing into the right downstream workflow

## System boundary

The system starts when Steve sends a Telegram voice message.

The system ends when one or more of the following have happened:
- Hermes replies in Telegram
- a note is appended or created
- a task/job is created
- a project artifact is updated
- a knowledge candidate is emitted
- learning artifacts are updated in the background

## High-level architecture

```text
Telegram voice message
    -> Hermes gateway ingest
    -> local audio cache
    -> local ASR
    -> transcript normalization
    -> Steve-aware interpretation
    -> routing decision
    -> action execution
    -> Telegram reply + optional side effects
    -> passive learning update
```

## Module map

### 1. Ingest module

Responsibility:
- receive Telegram voice/audio message
- persist local audio file path
- attach thread/session metadata

Inputs:
- Telegram event
- media bytes or media URL
- chat/thread/user metadata

Outputs:
- `VoiceEvent`

Proposed shape:

```text
VoiceEvent {
  platform: telegram
  chat_id: str
  thread_id: str | null
  user_id: str
  message_id: str
  audio_path: str
  mime_type: str
  duration_seconds: float | null
  received_at: datetime
}
```

Notes:
- Hermes gateway already performs a large part of this function.
- This layer should stay thin and deterministic.
- No semantic interpretation should happen here.

### 2. Audio preparation module

Responsibility:
- ensure the local audio file is in a format acceptable to local ASR
- convert Telegram-native formats when required
- preserve original file path for debugging and audit

Inputs:
- `VoiceEvent.audio_path`

Outputs:
- `PreparedAudio`

Proposed shape:

```text
PreparedAudio {
  original_audio_path: str
  prepared_audio_path: str
  original_format: str
  prepared_format: str
  conversion_performed: bool
}
```

Rules:
- if whisper backend accepts the original input format, do not convert
- if conversion is required, perform it locally via ffmpeg
- treat conversion failure as a recoverable error with user-facing fallback

### 3. Transcription module

Responsibility:
- run local ASR on prepared audio
- produce raw transcript plus backend metadata

Default backend:
- local whisper.cpp path

Inputs:
- `PreparedAudio`
- Steve lexicon prompt context
- backend config

Outputs:
- `TranscriptResult`

Proposed shape:

```text
TranscriptResult {
  success: bool
  raw_text: str
  backend: str
  model: str
  language_mode: str
  latency_ms: int
  error: str | null
}
```

Important design rule:
- the transcription module should know nothing about notes, tasks, or routing
- it only turns audio into text

### 3a. ASR backend/model strategy

The system must treat ASR backend selection as a configurable strategy, not a hardcoded implementation detail.

Why:
- Steve's use case depends on mixed Chinese/English handling and proper noun accuracy
- speed/quality trade-offs may change over time
- the currently verified local path may not remain the long-term best path
- experimentation should not require pipeline rewrites

#### Default v1 choice

Default v1 backend:
- `whisper_cpp`

Default v1 model:
- `large-v3-turbo`

Reason:
- this is the currently verified working local path on this machine
- it is meaningfully stronger than smaller defaults for Steve's code-switching and proper noun usage
- it preserves the local-first requirement without introducing cloud dependence

#### Strategy dimensions

The ASR strategy must make these dimensions explicit:
- backend
- model name
- binary/runtime path
- model file path
- language mode
- optional prompt or lexicon biasing
- optional conversion policy

#### Supported evolution path

The architecture should support three kinds of future changes:

1. Same backend, different model
- example: `large-v3-turbo` -> `medium`
- lowest-risk change
- should require config-only updates

2. Same model family, different runtime
- example: `whisper.cpp` -> `faster-whisper`
- useful for latency or deployment trade-offs
- should not require changes to routing or interpretation logic

3. Different backend entirely
- example: future local ASR engine or a domain-specialized backend
- higher-risk change
- should still fit behind the same transcription interface

#### Required abstraction boundary

All downstream modules should depend on a stable transcription contract:
- input: prepared audio + ASR config + Steve context hints
- output: `TranscriptResult`

No downstream module should need to know:
- whether the backend was whisper.cpp or something else
- which exact model family was used
- whether conversion happened internally

#### Configuration artifact

Backend/model choices should live in a dedicated config artifact:
- `configs/asr.yaml`

That file should be the single source of truth for:
- backend choice
- model choice
- runtime paths
- language behavior
- prompt/lexicon hooks

### 4. Normalization module

Responsibility:
- convert raw transcript into Steve-usable text
- improve utility without forcing user review

Transforms in order:
1. whitespace cleanup
2. script normalization
3. Simplified -> Traditional Chinese conversion
4. known proper noun normalization
5. high-confidence correction map substitutions
6. punctuation cleanup if helpful

Inputs:
- `TranscriptResult.raw_text`
- lexicon
- correction map
- normalization rules

Outputs:
- `NormalizedTranscript`

Proposed shape:

```text
NormalizedTranscript {
  raw_text: str
  normalized_text: str
  applied_rules: list[str]
  uncertainty_flags: list[str]
}
```

Important design rule:
- this module may improve text form
- it must not change intent aggressively when confidence is low
- risky corrections should become uncertainty flags, not silent rewrites

### 5. Steve-aware context module

Responsibility:
- provide user-specific context for interpretation and correction

Artifacts:
- `lexicon.yaml`
- `correction_map.yaml`
- `routing_preferences.yaml`
- `project_aliases.yaml`
- optional `voice_style.md` or `steve-operating-model.md`

Responsibilities include:
- preferred spelling of proper nouns
- project names and aliases
- recurring domain vocabulary
- routing hints such as:
  - "when Steve says '存一下', bias toward note capture"
  - "when utterance contains explicit imperative verbs, bias toward task capture"

This module does not act on the world.
It only loads and exposes structured context.

### 6. Interpretation module

Responsibility:
- determine what Steve is trying to do
- estimate confidence
- decide if clarification is needed

Inputs:
- normalized transcript
- recent Telegram conversation context
- Steve-aware context artifacts

Outputs:
- `IntentDecision`

Proposed shape:

```text
IntentDecision {
  primary_intent: str
  secondary_intents: list[str]
  confidence: float
  needs_clarification: bool
  clarification_question: str | null
  extracted_entities: dict
}
```

Primary intent set:
- `conversation_reply`
- `note_capture`
- `task_capture`
- `project_artifact_input`
- `knowledge_capture`

Example extracted entities:
- project name
- due date
- note topic
- destination path
- referenced person/tool/model

Important design rule:
- this module is where ambiguity should surface
- if ambiguity materially changes routing, ask a short question
- do not ask clarification for low-value stylistic uncertainty

### 7. Routing module

Responsibility:
- map `IntentDecision` to one or more actions

Inputs:
- `IntentDecision`
- conversation context
- routing preferences

Outputs:
- ordered list of `PlannedAction`

Proposed shape:

```text
PlannedAction {
  action_type: str
  target: str
  payload: dict
  blocking: bool
}
```

Examples:
- Telegram reply
- append to Obsidian note
- create/update project file
- create task/job
- emit concept candidate

Routing rules:
- some utterances only need a chat reply
- some should produce both a reply and a side effect
- side effects should be explicit in logs even if not surfaced verbosely to Steve

### 8. Execution module

Responsibility:
- perform the planned actions
- collect success/failure results

Examples:
- send assistant reply to Telegram
- append note in Obsidian
- create file under `~/workspace-max`
- create task or cron entry

Outputs:
- `ExecutionResult`

Proposed shape:

```text
ExecutionResult {
  actions_attempted: list[dict]
  actions_succeeded: list[dict]
  actions_failed: list[dict]
  user_visible_reply: str
}
```

Important design rule:
- user-facing reply should remain concise
- internal action detail can go to structured logs

### 9. Passive learning module

Responsibility:
- improve future accuracy without interrupting current interaction

Inputs:
- raw transcript
- normalized transcript
- final assistant action
- later corrections or clarifications from Steve

Outputs:
- proposed updates to lexicon/correction/routing artifacts

Learning sources:
1. explicit user correction
2. repeated clarification resolution
3. recurring proper noun mistakes
4. repeated routing mistakes

Important design rule:
- do not auto-edit user-facing behavior based on a single example when confidence is low
- accumulate evidence before promoting a correction into a durable rule

## End-to-end runtime data flow

### Default happy path

```text
1. Telegram adapter receives voice message
2. Audio cached locally
3. Audio prepared for local whisper backend
4. whisper.cpp transcribes
5. Transcript normalized
6. Intent interpreted
7. Routing plan created
8. Actions executed
9. Reply sent in Telegram
10. Interaction logged for passive learning
```

### Clarification path

```text
1. Voice received
2. Local transcription completed
3. Interpretation confidence below routing threshold
4. Hermes asks one short clarification question in Telegram
5. Steve replies by text or voice
6. System resumes routing with updated context
```

### Failure path: ASR fails

```text
1. Voice received
2. Local transcription fails
3. Hermes replies with a short failure notice
4. Logs preserve audio path and error details
5. No cloud fallback by default
```

## Decision thresholds

### Clarification threshold

Ask a clarification question when:
- project destination is ambiguous
- utterance could be either note or task with materially different consequences
- critical named entity is uncertain and action depends on it

Do not ask clarification when:
- transcript is imperfect but meaning is still recoverable
- typo-level errors do not change downstream action
- the system can safely continue with a conversational reply

### Correction threshold

Apply auto-correction when:
- correction is in the approved high-confidence map
- repeated evidence exists
- correction does not distort intent

Do not auto-correct when:
- substitution is speculative
- two plausible proper nouns compete
- context does not strongly disambiguate the term

## Storage design

Recommended project directory:

```text
~/workspace-max/steve-thought-capture/
  spec.md
  architecture.md
  configs/
    lexicon.yaml
    correction_map.yaml
    routing_preferences.yaml
    project_aliases.yaml
  logs/
    voice-events.jsonl
    learning-events.jsonl
  samples/
    transcript-pairs.jsonl
```

### Artifact meanings

`lexicon.yaml`
- canonical names and spelling hints
- examples: Anthropic, Opus, Claude Code, TW-LLM

`correction_map.yaml`
- high-confidence substitutions from repeated ASR mistakes to approved final forms

`routing_preferences.yaml`
- rules and hints that bias note vs task vs project routing

`project_aliases.yaml`
- project nicknames and their canonical destinations

`voice-events.jsonl`
- operational trace for each utterance

`learning-events.jsonl`
- evidence gathered for future adaptation

## Logging model

Each voice event should log:
- message metadata
- audio path
- transcript backend and latency
- raw transcript
- normalized transcript
- intent decision
- clarification asked or not
- actions executed
- final outcome

This is necessary for:
- debugging
- routing evaluation
- correction mining
- later benchmark creation

## Learning loop design

This is the key architectural differentiator.

### Loop stages

1. Capture evidence
- save raw transcript and normalized transcript
- record what Steve ultimately accepted or clarified

2. Detect patterns
- recurring proper noun failures
- recurring script conversion issues
- repeated routing ambiguity

3. Propose updates
- suggest new lexicon entries
- suggest new correction map pairs
- suggest new routing heuristics

4. Promote cautiously
- only high-confidence repeated patterns become default rules

### v1 learning philosophy

Use artifact learning, not model retraining.

Why:
- easier to inspect
- safer to rollback
- lower engineering cost
- more than enough to capture major gains in Steve's use case

## Integration points

### Hermes gateway

Use for:
- Telegram ingest
- session continuity
- local audio path access
- normal Telegram reply path

### Local whisper.cpp path

Use for:
- offline/local transcription
- mixed-language handling with prompt biasing and normalization

### Obsidian/workspace routing

Use existing routing conventions:
- conceptual capture -> Obsidian Conversations when appropriate
- concrete deliverables -> `~/workspace-max`

## v1 phased architecture rollout

### Phase 1: local Telegram voice transcription
Deliver:
- Telegram voice -> local audio path -> local whisper transcription
- no mandatory review step

### Phase 2: normalization and lexicon
Deliver:
- Traditional Chinese conversion
- proper noun correction
- Steve lexicon support

### Phase 3: intent and routing
Deliver:
- note/task/project/conversation classification
- initial routing heuristics

### Phase 4: passive learning
Deliver:
- correction evidence capture
- lexicon/correction proposal loop

### Phase 5: richer Steve-aware context
Deliver:
- stronger project aliasing
- stronger routing preferences
- better knowledge capture hooks

## Open design questions

1. Should note/task/project routing be automatic on first release, or should v1 begin with conversational reply + explicit commands only?
2. Where should candidate knowledge captures land first: a lightweight local queue, Obsidian Conversations, or direct concept-candidate files?
3. Should passive learning proposals remain fully internal at first, or be surfaced occasionally for approval?
4. Should the Steve-aware context live entirely in project-local files, or partially in Hermes memory/skills?

## Recommended architectural stance

Default to:
- auto-transcribe
- no review
- clarify only when ambiguity changes downstream action
- use lightweight editable artifacts for adaptation
- keep learning inspectable and reversible

That combination preserves flow while still allowing the system to improve over time.

## One-line summary

The architecture is a Telegram-native, local-first voice ingestion and interpretation pipeline with a Steve-specific adaptation layer that converts spoken thoughts into replies, notes, tasks, project inputs, and knowledge signals without forcing a transcript-review bottleneck.
