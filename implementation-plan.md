# Steve thought capture v1 implementation plan

> For Hermes: Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Build the first working version of a Telegram-first, local-ASR, Steve-aware thought capture and routing system.

**Architecture:** Reuse Hermes gateway for Telegram ingest and local audio caching, then add a project-local pipeline that handles local transcription, normalization, intent classification, and routing. Keep v1 local-first, no review-first, and artifact-driven rather than model-fine-tune-driven.

**Tech Stack:** Hermes gateway, Telegram, local audio cache, whisper.cpp, ffmpeg, Python, YAML config artifacts, JSONL logs.

---

## Assumptions

- Repository root: `~/workspace-max/steve-thought-capture`
- Existing live runtime for Telegram ingress: Hermes gateway
- Existing local ASR reference implementation: `~/workspace-max/voice-frontend`
- Existing spec docs:
  - `spec.md`
  - `architecture.md`

## v1 scope

Ship these capabilities only:
1. Telegram voice message arrives
2. local audio path is available
3. local whisper.cpp transcribes
4. transcript is normalized for Steve use
5. system chooses one of:
   - conversational reply
   - note capture
   - task capture
   - project artifact input
   - knowledge capture
6. system replies naturally in Telegram
7. passive learning artifacts are logged

Do not build in v1:
- realtime duplex voice
- always-on microphone
- mandatory transcript review
- model fine-tuning
- native iPhone app

---

## Proposed repository layout

```text
steve-thought-capture/
  README.md
  spec.md
  architecture.md
  implementation-plan.md
  configs/
    lexicon.yaml
    correction_map.yaml
    routing_preferences.yaml
    project_aliases.yaml
  docs/
    decisions/
  src/
    steve_thought_capture/
      __init__.py
      models.py
      audio_prepare.py
      transcription.py
      normalize.py
      steve_context.py
      interpret.py
      route.py
      execute.py
      learning.py
      pipeline.py
      telegram_adapter.py
  tests/
    test_normalize.py
    test_steve_context.py
    test_interpret.py
    test_route.py
    test_pipeline.py
  logs/
    .gitkeep
```

---

## Phase 0: repository scaffolding

### Task 1: Create source package skeleton

**Objective:** Create a minimal Python package structure so the project has a clean implementation home.

**Files:**
- Create: `src/steve_thought_capture/__init__.py`
- Create: `src/steve_thought_capture/models.py`

**Step 1: Write failing test**

Create `tests/test_import.py`:

```python
def test_package_imports():
    import steve_thought_capture
```

**Step 2: Run test to verify failure**

Run:
`PYTHONPATH=src ~/.hermes/hermes-agent/venv/bin/pytest tests/test_import.py -q`

Expected: FAIL — module not found.

**Step 3: Write minimal implementation**

Create empty package files.

**Step 4: Run test to verify pass**

Run:
`PYTHONPATH=src ~/.hermes/hermes-agent/venv/bin/pytest tests/test_import.py -q`

Expected: PASS.

**Step 5: Commit**

```bash
git add src/ tests/test_import.py
git commit -m "feat: scaffold source package"
```

### Task 2: Create config artifact skeletons

**Objective:** Establish editable Steve-aware artifacts before implementing behavior.

**Files:**
- Create: `configs/lexicon.yaml`
- Create: `configs/correction_map.yaml`
- Create: `configs/routing_preferences.yaml`
- Create: `configs/project_aliases.yaml`

**Step 1: Write failing test**

Create `tests/test_steve_context.py` with a test that loads all four files and asserts the expected top-level keys exist.

**Step 2: Run test to verify failure**

Run:
`PYTHONPATH=src ~/.hermes/hermes-agent/venv/bin/pytest tests/test_steve_context.py -q`

Expected: FAIL — files missing.

**Step 3: Write minimal implementation**

Create minimal YAML files with explicit top-level structures.

Suggested starter content:

`configs/lexicon.yaml`
```yaml
proper_nouns:
  - Anthropic
  - Opus
  - Claude
  - OpenAI
  - TW-LLM
  - pdf2zh
```

`configs/correction_map.yaml`
```yaml
substitutions: {}
```

`configs/routing_preferences.yaml`
```yaml
keywords:
  note_capture: []
  task_capture: []
  knowledge_capture: []
  project_artifact_input: []
```

`configs/project_aliases.yaml`
```yaml
aliases: {}
```

**Step 4: Run test to verify pass**

Run the test file again.

**Step 5: Commit**

```bash
git add configs/ tests/test_steve_context.py
git commit -m "feat: add Steve-aware config skeletons"
```

---

## Phase 1: transcript normalization

### Task 3: Implement normalization data model

**Objective:** Define the data structures used across the pipeline.

**Files:**
- Modify: `src/steve_thought_capture/models.py`
- Test: `tests/test_models.py`

**Step 1: Write failing test**

Add dataclass construction tests for:
- `VoiceEvent`
- `PreparedAudio`
- `TranscriptResult`
- `NormalizedTranscript`
- `IntentDecision`
- `PlannedAction`

**Step 2: Run test to verify failure**

Run:
`PYTHONPATH=src ~/.hermes/hermes-agent/venv/bin/pytest tests/test_models.py -q`

Expected: FAIL — names not defined.

**Step 3: Write minimal implementation**

Add simple dataclasses only. No extra methods yet.

**Step 4: Run test to verify pass**

Run the test file again.

**Step 5: Commit**

```bash
git add src/steve_thought_capture/models.py tests/test_models.py
git commit -m "feat: define pipeline data models"
```

### Task 4: Implement Steve context loader

**Objective:** Load YAML config artifacts from `configs/` and expose them in a structured form.

**Files:**
- Create: `src/steve_thought_capture/steve_context.py`
- Modify: `tests/test_steve_context.py`

**Step 1: Write failing test**

Add a test that calls `load_steve_context(project_root)` and asserts loaded values match fixture YAML content.

**Step 2: Run test to verify failure**

Run the specific test.

**Step 3: Write minimal implementation**

Implement:
- file loading
- YAML parsing
- simple dict return or dataclass return

**Step 4: Run test to verify pass**

Run the test file again.

**Step 5: Commit**

```bash
git add src/steve_thought_capture/steve_context.py tests/test_steve_context.py
git commit -m "feat: load Steve context artifacts"
```

### Task 5: Implement transcript normalization pipeline

**Objective:** Normalize ASR output into Steve-usable text.

**Files:**
- Create: `src/steve_thought_capture/normalize.py`
- Test: `tests/test_normalize.py`

**Step 1: Write failing tests**

Add tests for:
- whitespace normalization
- Simplified -> Traditional Chinese conversion
- proper noun replacement from correction map
- preserving mixed Chinese/English text

**Step 2: Run tests to verify failure**

Run:
`PYTHONPATH=src ~/.hermes/hermes-agent/venv/bin/pytest tests/test_normalize.py -q`

Expected: FAIL.

**Step 3: Write minimal implementation**

Implement a function like:
`normalize_transcript(raw_text, steve_context) -> NormalizedTranscript`

Reuse best available local conversion path (for example OpenCC if present), but make it best-effort.

**Step 4: Run tests to verify pass**

Run the test file again.

**Step 5: Commit**

```bash
git add src/steve_thought_capture/normalize.py tests/test_normalize.py
git commit -m "feat: add transcript normalization pipeline"
```

---

## Phase 2: local ASR path

### Task 6: Implement audio preparation module

**Objective:** Accept Telegram-local audio files and convert them only when needed.

**Files:**
- Create: `src/steve_thought_capture/audio_prepare.py`
- Test: `tests/test_audio_prepare.py`

**Step 1: Write failing tests**

Test cases:
- input format already supported -> no conversion
- unsupported format with ffmpeg available -> conversion path returned
- ffmpeg missing -> clear error

**Step 2: Run tests to verify failure**

Run the test file.

**Step 3: Write minimal implementation**

Implement:
- supported extension check
- ffmpeg invocation wrapper
- return `PreparedAudio`

**Step 4: Run tests to verify pass**

Run the test file again.

**Step 5: Commit**

```bash
git add src/steve_thought_capture/audio_prepare.py tests/test_audio_prepare.py
git commit -m "feat: add audio preparation for local ASR"
```

### Task 7: Implement whisper.cpp transcription adapter

**Objective:** Wrap the existing local whisper.cpp approach in a project-local module.

**Files:**
- Create: `src/steve_thought_capture/transcription.py`
- Test: `tests/test_transcription.py`

**Step 1: Write failing tests**

Test cases:
- successful subprocess call returns `TranscriptResult`
- missing binary returns a clear error
- failed command returns `success=False` with details

**Step 2: Run tests to verify failure**

Run the test file.

**Step 3: Write minimal implementation**

Implement a wrapper that:
- accepts `PreparedAudio`
- runs local whisper.cpp
- returns raw text and metadata

Use lessons from `~/workspace-max/voice-frontend/app/whisper_runner.py` but keep this module repo-local.

**Step 4: Run tests to verify pass**

Run the test file again.

**Step 5: Commit**

```bash
git add src/steve_thought_capture/transcription.py tests/test_transcription.py
git commit -m "feat: add local whisper transcription adapter"
```

---

## Phase 3: interpretation and routing

### Task 8: Implement initial intent classifier

**Objective:** Convert normalized text into a coarse routing decision.

**Files:**
- Create: `src/steve_thought_capture/interpret.py`
- Test: `tests/test_interpret.py`

**Step 1: Write failing tests**

Cover at least these cases:
- ordinary question -> `conversation_reply`
- "存一下" style utterance -> `note_capture`
- imperative/reminder -> `task_capture`
- explicit project dictation -> `project_artifact_input`
- insight/pattern statement -> `knowledge_capture`

**Step 2: Run tests to verify failure**

Run the test file.

**Step 3: Write minimal implementation**

Implement a heuristic classifier first.
No LLM dependency required in this step.

**Step 4: Run tests to verify pass**

Run the test file again.

**Step 5: Commit**

```bash
git add src/steve_thought_capture/interpret.py tests/test_interpret.py
git commit -m "feat: add initial intent classifier"
```

### Task 9: Implement routing planner

**Objective:** Map `IntentDecision` into concrete actions.

**Files:**
- Create: `src/steve_thought_capture/route.py`
- Test: `tests/test_route.py`

**Step 1: Write failing tests**

Test planned actions for each primary intent.

**Step 2: Run tests to verify failure**

Run the test file.

**Step 3: Write minimal implementation**

Implement a function like:
`plan_actions(intent_decision, context) -> list[PlannedAction]`

**Step 4: Run tests to verify pass**

Run the test file again.

**Step 5: Commit**

```bash
git add src/steve_thought_capture/route.py tests/test_route.py
git commit -m "feat: add routing planner"
```

---

## Phase 4: end-to-end pipeline

### Task 10: Implement pipeline orchestrator

**Objective:** Connect preparation, transcription, normalization, interpretation, and routing into one callable pipeline.

**Files:**
- Create: `src/steve_thought_capture/pipeline.py`
- Test: `tests/test_pipeline.py`

**Step 1: Write failing tests**

Mock each lower-level module and assert:
- happy path returns expected action plan
- ASR failure returns recoverable result
- low-confidence route requests clarification

**Step 2: Run tests to verify failure**

Run the test file.

**Step 3: Write minimal implementation**

Implement a top-level function like:
`process_voice_event(voice_event, steve_context) -> PipelineResult`

**Step 4: Run tests to verify pass**

Run the test file again.

**Step 5: Commit**

```bash
git add src/steve_thought_capture/pipeline.py tests/test_pipeline.py
git commit -m "feat: add end-to-end pipeline orchestrator"
```

### Task 11: Implement passive learning logger

**Objective:** Persist evidence needed for future correction and routing improvements.

**Files:**
- Create: `src/steve_thought_capture/learning.py`
- Modify: `tests/test_pipeline.py`
- Create: `logs/.gitkeep`

**Step 1: Write failing test**

Add a test that asserts a learning event JSONL record is written after processing a voice event.

**Step 2: Run test to verify failure**

Run the specific test.

**Step 3: Write minimal implementation**

Implement append-only JSONL logging for:
- raw transcript
- normalized transcript
- intent decision
- final action plan

**Step 4: Run test to verify pass**

Run the test again.

**Step 5: Commit**

```bash
git add src/steve_thought_capture/learning.py logs/.gitkeep tests/test_pipeline.py
git commit -m "feat: add passive learning logger"
```

---

## Phase 5: Hermes integration

### Task 12: Document integration contract with Hermes gateway

**Objective:** Define the thin boundary between this repository and Hermes runtime.

**Files:**
- Create: `docs/hermes-integration.md`

**Step 1: Write document**

Document:
- expected `VoiceEvent` fields from Telegram/Hermes
- how local audio paths are supplied
- where Telegram replies are sent from
- which parts remain inside Hermes vs this repo

**Step 2: Verify completeness**

Check that the document answers:
- who owns Telegram ingest?
- who owns local ASR?
- who owns routing?
- who owns execution side effects?

**Step 3: Commit**

```bash
git add docs/hermes-integration.md
git commit -m "docs: add Hermes integration contract"
```

### Task 13: Add minimal runner for local manual testing

**Objective:** Make it possible to test the pipeline against a cached audio file without wiring Telegram end-to-end first.

**Files:**
- Create: `src/steve_thought_capture/telegram_adapter.py`
- Create: `scripts/run_local_voice_event.py`
- Test: `tests/test_runner_smoke.py`

**Step 1: Write failing smoke test**

Test that a sample audio path can be passed through a thin runner interface.

**Step 2: Run test to verify failure**

Run the smoke test.

**Step 3: Write minimal implementation**

Add a tiny script that:
- loads Steve context
- constructs a `VoiceEvent`
- runs the pipeline
- prints the result

**Step 4: Run test to verify pass**

Run the smoke test.

**Step 5: Commit**

```bash
git add src/steve_thought_capture/telegram_adapter.py scripts/run_local_voice_event.py tests/test_runner_smoke.py
git commit -m "feat: add local pipeline runner"
```

---

## Verification commands

Use these exact commands during implementation:

```bash
cd ~/workspace-max/steve-thought-capture
PYTHONPATH=src ~/.hermes/hermes-agent/venv/bin/pytest tests/ -q
```

For targeted red/green cycles, run individual test files:

```bash
PYTHONPATH=src ~/.hermes/hermes-agent/venv/bin/pytest tests/test_normalize.py -q
PYTHONPATH=src ~/.hermes/hermes-agent/venv/bin/pytest tests/test_interpret.py -q
PYTHONPATH=src ~/.hermes/hermes-agent/venv/bin/pytest tests/test_pipeline.py -q
```

## Milestone definition

### Milestone A
- repo scaffolding exists
- Steve-aware configs load
- transcript normalization works

### Milestone B
- local whisper transcription works on Telegram-style audio files
- no review step required

### Milestone C
- basic intent classification and routing works
- passive learning logs are written

### Milestone D
- integration contract with Hermes is documented
- local manual runner proves the whole pipeline

## First recommended execution slice

If only one slice is implemented first, do this exact sequence:
1. Task 1
2. Task 2
3. Task 3
4. Task 4
5. Task 5
6. Task 6
7. Task 7
8. Task 10

That sequence gives the first truly useful spine:
- local audio input
- local transcript
- normalized Steve-usable text
- end-to-end processing entrypoint

## Final note

v1 should optimize for flow preservation, inspectability, and reversibility.

Do not overbuild.
Do not add native mobile UI.
Do not add model fine-tuning.
Do not add mandatory review.

Ship the smallest architecture that proves:
- Telegram-first capture
- local-first transcription
- Steve-aware normalization
- routing-capable downstream behavior
